{
  description = "CrossNote style generator for markdown-preview-enhanced";

  outputs = {self, ...}: {
    homeManagerModules.mdcss = import ./module.nix;
    homeManagerModules.default = self.homeManagerModules.mdcss;
  };
}
