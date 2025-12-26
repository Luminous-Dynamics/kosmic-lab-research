{
  description = "LLM K-Index Consciousness Research Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;  # Allow unfree packages (PyTorch's triton dependency)
        };

        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          # Core ML frameworks
          torch-bin
          torchvision-bin

          # Scientific computing
          numpy
          scipy
          matplotlib
          pandas

          # Testing
          pytest
          pytest-cov

          # Additional utilities
          tqdm
          pillow
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.git
          ];

          shellHook = ''
            echo "🧠 LLM K-Index Consciousness Research Environment"
            echo "   PyTorch with torchvision ready!"
            echo ""
            python --version
            python -c "import torch; print(f'PyTorch {torch.__version__}')" 2>/dev/null || echo "Loading PyTorch..."
            python -c "import torchvision; print(f'torchvision {torchvision.__version__}')" 2>/dev/null || echo "Loading torchvision..."
          '';
        };
      });
}
