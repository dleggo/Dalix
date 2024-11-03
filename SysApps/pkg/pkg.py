#!/bin/python3

import os
from tempfile import TemporaryDirectory
import tomllib

def get_pkg_info(path: str) -> dict:
	assert os.path.exists(path), "Package not found!"
	assert os.path.exist(path + "/pkg-info") # FIXME
	with open(path + "/pkg-info", "rb") as f:
		info = tomllib.load(f)
	return info

def get_deb_info(path: str) -> dict:
	assert os.path.exists(path), "Supplied path does not exist!"


# path should point to a .deb file
def install_deb(path: str, root: str):
	assert os.path.exists(path), "Supplied path does not exist!"
	assert path.lower()[-4:] == ".deb", "Path does not point to a .deb file!"
	# create pkg directory
	with TemporaryDirectory() as tmpdir:
		# extract pkg
		os.system(f"dpkg -x {path} {tmpdir}")
		# extract metadata

if __name__ == "__main__":
	install_deb("/home/derek/Code/Dalix/Resources/bwrap.deb", "/home/derek/Code/Dalix/Tests")
