{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "id_pdi";
  buildInputs = [
    pkgs.python312 
    pkgs.python312Packages.pandas
  ];
}