{
  description = "Kosmic Lab development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        projectDir = ./.;
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          numpy
          scipy
          pandas
          networkx
          tqdm
          pyyaml
          jsonschema
          pytest
          pip
          black
          matplotlib
          seaborn
          pygame  # Pre-built, avoids build issues
          fastapi
          uvicorn
          httpx
        ]);
        runTestsScript = pkgs.writeShellApplication {
          name = "kosmic-run-tests";
          runtimeInputs = [ pythonEnv pkgs.ruff ];
          text = ''
            cd ${projectDir}
            export PYTHONPATH=${projectDir}:$PYTHONPATH
            pytest --maxfail=1 --disable-warnings -q
          '';
        };
        runLintScript = pkgs.writeShellApplication {
          name = "kosmic-run-lint";
          runtimeInputs = [ pythonEnv pkgs.ruff ];
          text = ''
            cd ${projectDir}
            black --check core fre historical_k scripts tests
            ruff check core fre historical_k scripts tests --select E,F,I --ignore E501 --no-cache
            # Enforce E501 on targeted high-value files
            ruff check scripts/analyze_track_b.py fre/track_f_runner.py --select E501 --no-cache
          '';
        };
      in {
        devShells.default = pkgs.mkShell {
          packages = [
            pythonEnv
            pkgs.ruff
            pkgs.poetry
            pkgs.git
            pkgs.texlive.combined.scheme-full  # full LaTeX distribution with all packages
            # SDL2 and pygame dependencies for pettingzoo MPE
            pkgs.SDL2
            pkgs.SDL2_image
            pkgs.SDL2_mixer
            pkgs.SDL2_ttf
            pkgs.pkg-config
            pkgs.freetype
            pkgs.portaudio
            pkgs.libpng
            pkgs.libjpeg
            # OpenGL/Mesa dependencies for MuJoCo (mujoco-py headless rendering)
            pkgs.libGLU
            pkgs.mesa
            pkgs.mesa.osmesa
            pkgs.libGL
            pkgs.xorg.libX11
            pkgs.xorg.libXext
            pkgs.xorg.libXrandr
            pkgs.xorg.libXi
            pkgs.gcc
            pkgs.patchelf
            pkgs.zlib  # Required for numpy C-extensions
          ];
          shellHook = ''
            export PYTHONUNBUFFERED=1
            export KOSMIC_LAB_ROOT=${toString projectDir}
            # SDL2 and pygame library paths + OpenGL/Mesa for MuJoCo + zlib for numpy
            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
              pkgs.SDL2
              pkgs.SDL2_image
              pkgs.SDL2_mixer
              pkgs.SDL2_ttf
              pkgs.freetype
              pkgs.portaudio
              pkgs.libpng
              pkgs.libjpeg
              pkgs.libGLU
              pkgs.mesa
              pkgs.mesa.osmesa
              pkgs.libGL
              pkgs.xorg.libX11
              pkgs.xorg.libXext
              pkgs.xorg.libXrandr
              pkgs.xorg.libXi
              pkgs.zlib
            ]}:$LD_LIBRARY_PATH"
            # MuJoCo 210 binaries path (required for mujoco-py)
            export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/.mujoco/mujoco210/bin"
            echo "Kosmic Lab dev shell activated (with LaTeX + SDL2 for MPE + OpenGL for MuJoCo)."
          '';
        };

        apps = rec {
          run-tests = {
            type = "app";
            program = "${runTestsScript}/bin/kosmic-run-tests";
          };
          run-lint = {
            type = "app";
            program = "${runLintScript}/bin/kosmic-run-lint";
          };
          run-archive-verify = {
            type = "app";
            program = "${pkgs.writeShellApplication {
              name = "kosmic-archive-verify";
              runtimeInputs = [ pythonEnv ];
              text = ''
                if [ -z "$1" ]; then
                  echo "Usage: kosmic-archive-verify ARCHIVE.tar.gz"
                  exit 1
                fi
                cd ${projectDir}
                export PYTHONPATH=${projectDir}:$PYTHONPATH
                python scripts/archive_tool.py verify --archive "$1"
              '';
            }}/bin/kosmic-archive-verify";
          };
          run-archive-summary = {
            type = "app";
            program = "${pkgs.writeShellApplication {
              name = "kosmic-archive-summary";
              runtimeInputs = [ pythonEnv ];
              text = ''
                if [ -z "$1" ]; then
                  echo "Usage: kosmic-archive-summary ARCHIVE.tar.gz"
                  exit 1
                fi
                cd ${projectDir}
                export PYTHONPATH=${projectDir}:$PYTHONPATH
                python scripts/archive_tool.py summary --archive "$1"
              '';
            }}/bin/kosmic-archive-summary";
          };
          run-ruff = {
            type = "app";
            program = "${pkgs.writeShellApplication {
              name = "kosmic-run-ruff";
              runtimeInputs = [ pkgs.ruff ];
              text = ''
                ruff check . --no-cache
              '';
            }}/bin/kosmic-run-ruff";
          };
          run-api-fixtures = {
            type = "app";
            program = "${pkgs.writeShellApplication {
              name = "kosmic-api-fixtures";
              runtimeInputs = [ pythonEnv ];
              text = ''
                cd ${projectDir}
                export PYTHONPATH=${projectDir}:$PYTHONPATH
                python scripts/generate_api_fixtures.py --out logs
              '';
            }}/bin/kosmic-api-fixtures";
          };
          run-api = {
            type = "app";
            program = "${pkgs.writeShellApplication {
              name = "kosmic-api";
              runtimeInputs = [ pythonEnv ];
              text = ''
                cd ${projectDir}
                export PYTHONPATH=${projectDir}:$PYTHONPATH
                exec uvicorn historical_k.api:app --host 0.0.0.0 --port "${PORT:-8052}"
              '';
            }}/bin/kosmic-api";
          };
          default = run-tests;
        };

        checks.pytest = pkgs.runCommand "kosmic-pytest" { buildInputs = [ pythonEnv ]; } ''
          export HOME=$TMPDIR
          cd ${projectDir}
          export PYTHONPATH=${projectDir}:$PYTHONPATH
          pytest --maxfail=1 --disable-warnings -q
          touch $out
        '';

        checks.archive = pkgs.runCommand "kosmic-archive-check" { buildInputs = [ pythonEnv ]; } ''
          export HOME=$TMPDIR
          cd ${projectDir}
          mkdir -p tmp/checks
          cat <<'JSON' > tmp/checks/min_checkpoint.json
{"metadata":{"config":{"path":"synthetic","sha256":"dummy"}},"state":{}}
JSON
          export PYTHONPATH=${projectDir}:$PYTHONPATH
          python scripts/archive_tool.py create --checkpoint tmp/checks/min_checkpoint.json --config fre/configs/track_g_threshold.yaml --output tmp/checks/sample_bundle.tar.gz
          python scripts/archive_tool.py verify --archive tmp/checks/sample_bundle.tar.gz
          touch $out
        '';

        checks.lint = pkgs.runCommand "kosmic-lint" { buildInputs = [ pythonEnv pkgs.ruff ]; } ''
          export HOME=$TMPDIR
          cd ${projectDir}
          ruff check core fre historical_k scripts tests --select F --no-cache --exit-zero
          touch $out
        '';

        checks.registry = pkgs.runCommand "kosmic-registry" { buildInputs = [ pythonEnv ]; } ''
          cd ${projectDir}
          export PYTHONPATH=${projectDir}:$PYTHONPATH
          python scripts/validate_registry.py --path configs/config_registry.json
          touch $out
        '';
      });
}
