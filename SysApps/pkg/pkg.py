#!/bin/python3

import os
import tempfile
import tomllib

def get_info(path: str) -> dict:
	assert os.path.exists(path), "Package not found!"
	assert os.path.exist(path + "/pkg-info") # FIXME
	with open(path + "/pkg-info", "rb") as f:
		info = tomllib.load(f)
	return info


# path should point to a .deb file
def install(path: str):
	assert os.path.exists(path), "Supplied path does not exist!"
	# create pkg directory
	# extract pkg
	# extract metadata

if __name__ == "__main__":
	install("/home/derek/Code/Dalix/Resources/bwrapchroot.deb")
