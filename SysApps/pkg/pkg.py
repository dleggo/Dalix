#!/bin/python3

import os
from tempfile import TemporaryDirectory
import toml

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
			f = control.read().rstrip()
			a = f.split("\n")
			for b in a:
				if b[0] == " " or b[0] == "\t":
					if info_list:
						info_list[-1] = (info_list[-1][0], info_list[-1][1] + "\n"  + b)
					else:
						raise ValueError("Invalid control file in package!")
				else:
					c = b.split(":")
					assert len(c) == 2, "Invalid control file in package!"
					key,value = c[0], c[1]
					key = key.lstrip().rstrip()
					value = value.lstrip().rstrip()
					info_list.append((key, value))
	info = {}
	for a in info_list:
		info[a[0]] = a[1]
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
def install_deb(path: str, root: str):
	assert os.path.exists(path), "Supplied path does not exist!"
	assert path.lower()[-4:] == ".deb", "Path does not point to a .deb file!"
	# create pkg directory
	with TemporaryDirectory() as tmpdir:
		# extract pkg
		os.system(f"dpkg -x {path} {tmpdir}")
		# extract metadata
		info = get_deb_info(path)
		info = deb_to_pkg_info(info)
		print(info)
		# install package
		inst_dir = f"{root}/System/Packages/{info["Package"]["Name"]}***{info["Package"]["Version"]}"
		os.system(f"mkdir -p {inst_dir}")
		os.system(f"cp -r {tmpdir} {inst_dir}/chroot")
		# install config
		os.system(f"touch {inst_dir}/pkg-info")
		with open(f"{inst_dir}/pkg-info", "w") as info_f:
			toml.dump(info, info_f)


if __name__ == "__main__":
	install_deb(
		"/home/derek/Code/Dalix/Resources/bwrap.deb",
		"/home/derek/Code/Dalix/Tests/testroot"
	)
