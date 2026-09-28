{
  description = "CrossNote style generator for markdown-preview-enhanced";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    nix-vscode-extensions = {
      url = "github:nix-community/nix-vscode-extensions";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {self, nix-vscode-extensions, ...}: {
    homeManagerModules.mdcss = import ./module.nix;
    homeManagerModules.default = self.homeManagerModules.mdcss;
    homeManagerModules.markdown-preview-enhanced =
      import ./markdown-preview-enhanced.nix nix-vscode-extensions;
  };
}
