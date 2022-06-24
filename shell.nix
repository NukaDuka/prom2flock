let
	sources = import ./nix/sources.nix;
	pkgs = import sources.nixpkgs {};
in

pkgs.mkShell {
	buildInputs = with pkgs; [
		niv
		git
        python3
	];
	shellHook = ''
		export nixpkgs=${pkgs.path}
        export DIR_PREFIX=$PWD
        clean_env () {
            rm -rf $DIR_PREFIX/env
        }

        create_env () {
            ${pkgs.python3}/bin/python3 -m venv $DIR_PREFIX/env
            source $DIR_PREFIX/env/bin/activate
        }

        activate () {
            source $DIR_PREFIX/env/bin/activate
        }
	'';
}
