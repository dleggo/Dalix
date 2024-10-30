#!/bin/python3

import os

class InvalidPathError(Exception):
	pass

class InvalidFileTypeError(Exception):
	pass

# Describing a Dalix Package
class Pkg:
	def __init__(self, path: str):
		if not os.path.exists(path):
			raise InvalidPathError("Supplied path does not exist!")
		# path exists
		if path[-4:].lower() == ".deb":
			raise InvalidFileTypeError(
				"Supplied file cannot be a .deb file. Maybe use install_from_deb instead?")