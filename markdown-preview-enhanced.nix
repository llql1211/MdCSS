nix-vscode-extensions: {
  lib,
  pkgs,
  config,
  options,
  ...
}: let
  cfg = config.programs.markdown-preview-enhanced;

  extensionSubdir = "share/vscode/extensions/shd101wyy.markdown-preview-enhanced";

  patched = cfg.package.overrideAttrs (old: {
    nativeBuildInputs = (old.nativeBuildInputs or []) ++ [pkgs.python3];
    postInstall = (old.postInstall or "") + ''
      python3 ${./tools/patch_mpe.py} --extension-dir $out/${extensionSubdir} --no-backup
    '';
  });

  # home-manager >= 25.11 renamed programs.vscode.extensions to profiles.default.extensions
  vscodeIntegration =
    if options ? programs.vscode.profiles
    then {programs.vscode.profiles.default.extensions = [patched];}
    else if options ? programs.vscode.extensions
    then {programs.vscode.extensions = [patched];}
    else {};
in {
  options.programs.markdown-preview-enhanced = {
    enable = lib.mkEnableOption "markdown-preview-enhanced with the mdcss preview-script patch";

    package = lib.mkOption {
      type = lib.types.package;
      default = nix-vscode-extensions.extensions.${pkgs.stdenv.hostPlatform.system}.vscode-marketplace.shd101wyy.markdown-preview-enhanced;
      defaultText = "latest Marketplace build from the nix-vscode-extensions flake input";
      description = ''
        markdown-preview-enhanced derivation to patch. The patch is applied
        on top of this package and is a no-op for MPE <= 0.8.35, which
        needs none.
      '';
    };

    finalPackage = lib.mkOption {
      type = lib.types.package;
      readOnly = true;
      visible = false;
      description = ''
        The patched markdown-preview-enhanced derivation. Reference it in a
        vscode-with-extensions extension list; with programs.vscode the
        module adds it to the default profile's extensions by itself.
      '';
    };
  };

  config = lib.mkIf cfg.enable (lib.mkMerge [
    {
      programs.markdown-preview-enhanced.finalPackage = patched;
    }
    vscodeIntegration
    (lib.optionalAttrs (options ? services.mdcss) {
      services.mdcss.extensionDir = lib.mkDefault "${patched}/${extensionSubdir}";
    })
  ]);
}
