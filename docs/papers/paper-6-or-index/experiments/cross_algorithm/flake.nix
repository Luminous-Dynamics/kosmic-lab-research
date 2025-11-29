{
  description = "Cross-Algorithm Robustness Experiments for O/R Index Paper";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python + Poetry (Hybrid Approach)
            python311
            poetry

            # System libraries for Python packages
            zlib
            SDL2
            SDL2_image
            SDL2_mixer
            SDL2_ttf

            # Build tools
            gcc
            pkg-config
            stdenv.cc.cc.lib  # libstdc++
          ];

          shellHook = ''
            echo "================================"
            echo "Cross-Algorithm Training Environment"
            echo "Hybrid Poetry + Nix Approach"
            echo "================================"
            echo "Python: $(python --version)"
            echo "Poetry: $(poetry --version)"
            echo ""

            # Set library paths for Python packages
            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
              pkgs.zlib
              pkgs.SDL2
              pkgs.SDL2_image
              pkgs.SDL2_mixer
              pkgs.SDL2_ttf
              pkgs.stdenv.cc.cc.lib
            ]}:$LD_LIBRARY_PATH"

            # Initialize Poetry environment if needed
            if [ ! -d ".venv" ]; then
              echo "Creating Poetry virtual environment..."
              poetry config virtualenvs.in-project true
              poetry install
            fi

            echo ""
            echo "Ready to train!"
            echo "  Run: poetry run python ma_dqn_trainer.py"
            echo "  Or activate: poetry shell"
            echo ""
          '';
        };
      });
}
