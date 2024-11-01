#!/bin/python3

import os
import tempfile

class InvalidPathError(Exception):
	pass

class InvalidFileTypeError(Exception):
	pass

# Describing a Dalix Package
class Pkg:
	def __init__(self, path: str):
		self.path = path
		self.metadata = None

class App:
	def __init__(self, path: str):
		pass

# delegates to install_pkg or install_app
def install(path: str):
	assert os.path.exists(path), "Supplied path does not exist!"
	# create pkg directory
	# extract pkg
	# extract metadata

if __name__ == "__main__":
	install("")
