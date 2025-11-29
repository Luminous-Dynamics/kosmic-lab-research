{
  description = "Overcooked O/R Index Validation - NixOS Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # Python with base packages available in nixpkgs
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          numpy
          pandas
          matplotlib
          seaborn
          scipy
          scikit-learn
          tqdm
          torch
          torchvision
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv

            # System dependencies for Overcooked-AI (SDL2 for rendering)
            SDL2
            SDL2_image
            SDL2_ttf
            SDL2_mixer

            # Build tools
            pkg-config
            gcc

            # Convenience tools
            gnumake
          ];

          shellHook = ''
            echo "🍳 Overcooked O/R Index Validation Environment"
            echo "=============================================="
            echo ""
            echo "Setting up Python virtual environment..."

            # Create venv if it doesn't exist
            if [ ! -d .venv ]; then
              python -m venv .venv
              echo "✓ Virtual environment created"
            fi

            # Activate venv
            source .venv/bin/activate

            # Install pip-only packages
            if [ ! -f .venv/.installed ]; then
              echo ""
              echo "Installing pip dependencies (overcooked-ai, pettingzoo)..."
              pip install --upgrade pip
              pip install -r requirements.txt
              touch .venv/.installed
              echo "✓ Dependencies installed"
            fi

            echo ""
            echo "Environment ready! Available commands:"
            echo "  make help              - Show all available targets"
            echo "  make test-env          - Test environment setup"
            echo "  make overcooked-train  - Train all policies (4-6 hours GPU)"
            echo "  make overcooked-collect - Collect trajectories (30 seeds)"
            echo "  make overcooked-analyze - Generate figures and CSV"
            echo "  make overcooked-all    - Run full pipeline"
            echo ""
            echo "Or run scripts directly:"
            echo "  python env_overcooked.py       - Test environment wrapper"
            echo "  python train_overcooked.py     - Train policies"
            echo "  python collect_overcooked.py   - Collect trajectories"
            echo "  python analyze_overcooked.py   - Analyze and plot"
            echo ""
          '';

          # Environment variables
          SDL_VIDEODRIVER = "dummy";  # Headless rendering
          MPLBACKEND = "Agg";         # Matplotlib non-interactive backend
        };
      }
    );
}
