#!/bin/python3

import os
from tempfile import TemporaryDirectory
import toml
from packaging.version import Version

root = ""

def get_pkg_info(path: str) -> dict:
	assert os.path.exists(path), "Package not found!"
	assert os.path.exist(path + "/pkg-info") # FIXME
	with open(path + "/pkg-info", "r") as f:
		info = toml.load(f)
	return info

def get_deb_info(path: str) -> dict:
	assert os.path.exists(path), "Supplied path does not exist!"
	with TemporaryDirectory() as tmpdir:
		os.system(f"dpkg-deb -R {path} {tmpdir}")
		assert os.path.exists(tmpdir + "/DEBIAN/control"), "No control file found in package!"
		info_list = [] # contains tuples of (key: str, value: str)
		with open(tmpdir + "/DEBIAN/control") as control:
			file = control.read().rstrip()
			entry_list = file.split("\n")
			for entry in entry_list:
				if entry[0] == " " or entry[0] == "\t":
					if info_list:
						info_list[-1] = (info_list[-1][0], info_list[-1][1] + "\n"  + entry)
					else:
						raise ValueError("Invalid control file in package!")
				else:
					entry_split = entry.split(":")
					entry_split[1] = ''.join(entry_split[1:])

					key,value = entry_split[0:2]
					key = key.lstrip().rstrip()
					value = value.lstrip().rstrip()
					info_list.append((key, value))
	info = {}
	for entry_list in info_list:
		info[entry_list[0]] = entry_list[1]
	return info

def deb_to_pkg_info(info: dict) -> dict:
	pkg_info = {
		"InfoType": 1,
		"Package": {}
	}
	try:
		pkg_info["Package"]["Name"] = info["Package"]
		pkg_info["Package"]["Version"] = info["Version"]
		pkg_info["Package"]["Arch"] = info["Architecture"]
		pkg_info["Package"]["Maintainer"] = info["Maintainer"]
		pkg_info["Package"]["Description"] = info["Description"]
		if "Depends" in info:
			pkg_info["Package"]["Dependencies"] = info["Depends"]
		else:
			pkg_info["Package"]["Dependencies"] = ""
	except KeyError:
		raise ValueError("Invalid debian control file in package!")
	return pkg_info

# path should point to a .deb file
def install_deb(path: str):
	global root

	assert os.path.exists(path), "Supplied path does not exist!"
	assert path.lower()[-4:] == ".deb", "Path does not point to a .deb file!"
	# create pkg directory
	with TemporaryDirectory() as tmpdir:
		# extract pkg
		os.system(f"dpkg -x {path} {tmpdir}")
		# extract metadata
		info = get_deb_info(path)
		info = deb_to_pkg_info(info)
		# install package
		# FIXME: make symlinks e.g. /bin -> usr/bin etc.
		inst_dir = f"{root}/System/Packages/{info["Package"]["Name"]}***{info["Package"]["Version"]}"
		os.system(f"mkdir -p {inst_dir}")
		os.system(f"cp -r {tmpdir} {inst_dir}/chroot")
		# install config
		os.system(f"touch {inst_dir}/pkg-info")
		with open(f"{inst_dir}/pkg-info", "w") as info_f:
			toml.dump(info, info_f)

def get_pkg_list():
	packages = os.listdir(f"{root}/System/Packages")
	for pkg in packages:
		pkg_name = pkg.split("***")
		if len(pkg_name) != 2:
			print(f"Corrupt package in system! \"{pkg}\" Skipping for now.")
			continue
		pkg_dict = {
			"Name": pkg_name[0],
			"Version": Version(pkg_name[1]),
			"Path": pkg
		}
		yield pkg_dict

def search_pkg_list(name: str, strict=False):
	global root

	for pkg in get_pkg_list():
		if strict:
			if pkg["Name"] == name:
				yield pkg
		else:
			if name in pkg["Name"]:
				yield name

def get_pkg(name: str):
	# We try to use the newest version availible to us.
	candidates = list(search_pkg_list(name))
	if not candidates: return None
	newest = None
	for candidate in candidates:
		if newest == None:
			newest = candidate
		else:
			if newest["Version"] < candidate["Version"]:
				newest = candidate
	return newest


if __name__ == "__main__":
	root = "/home/derek/Code/Dalix/Tests/testroot"
	install_deb("/home/derek/Code/Dalix/Tests/bwrap0.10.0.deb")
