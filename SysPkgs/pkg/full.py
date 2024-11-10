#!/bin/python3

import os
from tempfile import TemporaryDirectory
import tomllib
import tomli_w
# from packaging.version import Version
from collections import namedtuple
import argparse
from shutil import copytree, copyfile
import termcolor
from termcolor import colored
import sys
# from semver.version import Version

# Dependency = namedtuple('dep_info_t', ['name', 'comparison', 'version'])

root = ""

GOOD = 0
INFO = 1
WARNING = 2
ERROR = 3

def log(msg: str, level: int = 0):
	if level == GOOD:
		print(f"[{colored('+', 'green')}] {msg}")
	elif level == INFO:
		print(f"[{colored('*', 'blue')}] {msg}")
	elif level == WARNING:
		print(f"[{colored('!', 'yellow')}] {msg}")
	elif level == ERROR:
		print(f"[{colored('X', 'red')}] {msg}")

class Version:
	def __init__(self, version: str):
		self.version = version

	def __lt__(self, other):
		return os.system(f"dpkg --compare-versions {self.version} lt {other.version}") == 0
	def __gt__(self, other):
		return os.system(f"dpkg --compare-versions {self.version} gt {other.version}") == 0
	def __eq__(self, other):
		return os.system(f"dpkg --compare-versions {self.version} eq {other.version}") == 0
	def __ne__(self, other):
		return os.system(f"dpkg --compare-versions {self.version} ne {other.version}") == 0
	def __le__(self, other):
		return os.system(f"dpkg --compare-versions {self.version} le {other.version}") == 0
	def __ge__(self, other):
		return os.system(f"dpkg --compare-versions {self.version} ge {other.version}") == 0

	def __str__(self):
		return self.version

class Package:
	def __init__(self, name: str, version: Version, path: str):
		assert os.path.exists(path), "Package not found!"
		assert os.path.exists(path + "/pkg-info")
		self.name = name
		self.version = version
		self.path = path

	def __eq__(self, other):
		if type(other) != Package:
			return False
		return self.name == other.name and self.version == other.version and self.path == other.path

	def get_info(self) -> dict:
		"""
		Reads and returns package metadata from a pkg-info file.

		This function asserts the existence of a package directory and its pkg-info file,
		then loads the metadata from the pkg-info file using the TOML format and returns
		it as a dictionary.

		:return: A dictionary containing the package metadata.
		:raises AssertionError: If the package directory or pkg-info file does not exist.
		"""
		path = self.path
		assert os.path.exists(path), "Package not found!"
		assert os.path.exists(path + "/pkg-info")
		with open(path + "/pkg-info", "rb") as f:
			info = tomllib.load(f)
		return info

	def get_deps(self) -> list:
		"""
		:returns list(Packages):
		"""
		info = self.get_info()
		deps2 = info["Package"]["Dependencies"].split(",")
		deps = []
		for dep in deps2:
			if len(dep.split("|")) != 1:
				# We have an OR situation here...
				deps.append(OR([Dependency.parse(dep.lstrip().rstrip()) for dep in dep.split("|")]))
			else:
				deps.append(Dependency.parse(dep))
		print(deps)
		pkgs = deps_to_pkgs(deps)

		return pkgs

	def __repr__(self):
		return f"Pkg({self.name}, {self.version}, {self.path})"

class Dependency:
	def __init__(self, name: str, comparisons: list, versions: list):
		self.name = name
		self.comparisons = comparisons
		self.versions = versions

	def satisfied_by(self, version: Version) -> bool:
		if self.versions == None:
			return True
		if self.comparisons == None:
			return True
		for comparison, needed_ver in zip(self.comparisons, self.versions):
			if comparison == "=":
				if Version(needed_ver) != Version(version):
					return False
			elif comparison == ">=":
				if Version(needed_ver) > Version(version):
					return False
			elif comparison == "<=":
				if Version(needed_ver) < Version(version):
					return False
			elif comparison in [">", ">>"]:
				if Version(needed_ver) >= Version(version):
					return False
			elif comparison in ["<", "<<"]:
				if Version(needed_ver) <= Version(version):
					return False
		return True

	def __repr__(self):
		return f"Dependency({self.name}, {self.comparisons}, {self.versions})"

	def parse(dep: str):
		"""
		Parses a dependency string and returns a dep_info_t representing the parsed dependency.

		The dep_info_t structure has the following fields:
			- name: The name of the package.
			- comparison: The comparison operator used in the dependency string.
			- version: The version of the package.

		For example, if given the input "pkg1 (>= 2.1.0)", the output will be:
			Dependency("pkg1", ">=", "2.1.0")

		:returns Dependency:
		"""
		if "(" in dep:
			name, constraint = dep.split("(", 1)
			name = name.rstrip().lstrip()
			constraint = constraint.strip(" )")
			comparisons = []
			versions = []
			for part in constraint.split(","):
				part = part.strip()
				comparison, version = part.split(" ", 1)
				comparisons.append(comparison)
				versions.append(version)
			return Dependency(name, comparisons, versions)
		else:
			return Dependency(dep, None, None)

class OR:
	def __init__(self, deps: list):
		self.deps = deps

	def satisfied_by(self, version: Version) -> bool:
		for dep in self.deps:
			if dep.satisfied_by(version):
				return True
		return False

	def __repr__(self):
		return f"OR({self.deps})"


def get_deb_info(path: str) -> dict:
	"""
	Extracts metadata from a .deb package.

	This function extracts all the metadata from a .deb package, and returns it as a dictionary.

	:raises ValueError: The package's control file is invalid.
	:raises FileNotFoundError: The package does not exist.
	:returns dict:
	"""
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
	"""
	Convert a debian control file info dict into a dalixOS pkg-info dict.

	This function takes a dict generated by get_deb_info and converts it into a dict
	that can be written to a pkg-info file.

	:raises ValueError: If the control file is invalid
	:returns dict:
	"""
	assert type(info) == dict
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
			deps = info["Depends"]
			# deps = deps.replace(",", "\n").replace("(", "").replace(")", "").replace(" ", "")
			pkg_info["Package"]["Dependencies"] = deps
		else:
			pkg_info["Package"]["Dependencies"] = ""
	except KeyError:
		raise ValueError("Invalid debian control file in package!")
	assert type(pkg_info) == dict
	return pkg_info

def symlink(src: str, dst: str):
	"""
	Creates a symbolic link from src to dst. dst is what gets created.

	Ensures that the directory of dest exists before creating the symlink.
	"""

	assert type(src) == str and type(dst) == str
	os.makedirs(src, exist_ok=True)

	dst_dir = os.path.dirname(dst)
	os.makedirs(dst_dir, exist_ok=True)

	# relative_path = os.path.relpath(source_path, target_dir)
	os.symlink(src, dst, target_is_directory=os.path.isdir(src))

def init_system():
	"""
	Initializes the system by first running debbootstrap to create a
	basic system in the root directory,
	then copies the necessary files into the root directory,
	and finally runs the init script to finish setting up the system.
	"""
	global root
	print(colored("running debootstrap..", "green", attrs=["bold"]))
	print(colored("this may take a while..", "green", attrs=["bold"]))
	os.system(f"debootstrap stable {root} http://deb.debian.org/debian/")
	script_dir = os.path.dirname(os.path.realpath(__file__))
	print(colored("copying files..", "green", attrs=["bold"]))
	os.system(f"cp {script_dir}/init_script.sh {root}/usr/bin/init_script.sh")
	os.system(f"cp {script_dir}/full.py {root}/usr/bin/pkg")
	os.system(f"chmod +x {root}/usr/bin/init_script.sh")
	print(colored("running init script..", "green", attrs=["bold"]))
	os.system(f"arch-chroot {root} /usr/bin/init_script.sh")
	print(colored("done", "green", attrs=["bold"]))


# path should point to a .deb file
def install_deb(path: str, fetch_dependencies: bool = True):
	"""
	Installs a .deb package into the system.

	This function will install a .deb package into the system. The package will be extracted and
	installed into a directory under /System/Packages, and the metadata will be extracted and stored
	in a file called pkg-info in the same directory.

	All symlinks will be created to point to the correct location.

	:raises ValueError: The package's control file is invalid.
	:raises FileNotFoundError: The package does not exist.
	:raises AssertionError: The package's path does not end with .deb.
	"""
	assert type(path) == str and type(fetch_dependencies) == bool
	global root

	assert os.path.exists(path), "Supplied path does not exist!"
	assert path.lower()[-4:] == ".deb", "Path does not point to a .deb file!"
	# create pkg directory
	with TemporaryDirectory() as tmpdir:
		# extract pkg
		log(f"Extracting {path}...")
		os.system(f"dpkg -x {path} {tmpdir}")
		# extract metadata
		info = get_deb_info(path)
		info = deb_to_pkg_info(info)
		# install package

		log(f"Installing {path}...")

		inst_dir = f"{root}/System/Packages/{info['Package']['Name']}***{info['Package']['Version']}"

		if os.path.exists(inst_dir):
			os.system(f"rm -R {inst_dir}")
		os.system(f"mkdir -p {inst_dir}")

		# create symlinks
		chroot = inst_dir + "/chroot"
		symlink(f"{chroot}/usr/bin", f"{chroot}/bin")
		symlink(f"{chroot}/usr/bin", f"{chroot}/usr/local/bin")
		symlink(f"{chroot}/usr/sbin", f"{chroot}/sbin")
		symlink(f"{chroot}/usr/lib", f"{chroot}/lib")
		symlink(f"{chroot}/usr/lib64", f"{chroot}/lib64")
		symlink(f"{chroot}/usr/etc", f"{chroot}/etc")
		symlink(f"{chroot}/usr/var", f"{chroot}/var")

		# os.system(f"cp -Ra {tmpdir}/. {inst_dir}/chroot")
		copytree(
			tmpdir,
			f"{inst_dir}/chroot",
			symlinks=True,
			dirs_exist_ok=True
		)

		# install config
		os.system(f"touch {inst_dir}/pkg-info")
		with open(f"{inst_dir}/pkg-info", "w") as info_f:
			info_f.write(
				tomli_w.dumps(
					info,
					multiline_strings=True
				),
			)
		# install dependencies from debians servers.
		if "Dependencies" in info["Package"] and fetch_dependencies:
			install_deps_for_pkg(Package(info["Package"]["Name"], Version(info["Package"]["Version"]), inst_dir))

def install_deps(dep_string: str):
	"""
	Downloads and installs all dependencies specified in dep_string.

	:raises FileNotFoundError: Apt-get failed to download the specified package.
	:raises Exception: Any other exception will be raised if the install fails.
	:param dep_string: A string of dependencies to install
	"""
	assert type(dep_string) == str
	cmd = "apt-get satisfy --download-only"
	with TemporaryDirectory() as tmpdir:
		os.system(f"{cmd} \"{dep_string}\" -o Dir::Cache::Archives={tmpdir} -y")
		deps = os.listdir(tmpdir)
		for dep in deps:
			if dep[-4:] != ".deb":
				continue
			log(f"Going to install {dep}...")
			try:
				install_deb(f"{tmpdir}/{dep}", fetch_dependencies=False)
			except Exception as e:
				log(f"Failed to install {dep}! Skipping for now...", WARNING)
				print(e)
				continue

def install_pkg_from_online(pkg: str):
	"""
	:param str: A string repersenting the package to install
	"""
	assert type(pkg) == str
	cmd = "apt-get install --download-only --reinstall"
	with TemporaryDirectory() as tmpdir:
		os.system(f"{cmd} \"{pkg}\" -o Dir::Cache::Archives={tmpdir} -y")
		pkgs = os.listdir(tmpdir)
		for pkg in pkgs:
			if pkg[-4:] != ".deb":
				continue
			log(f"Going to install {pkg}...")
			try:
				install_deb(f"{tmpdir}/{pkg}", fetch_dependencies=False)
			except Exception as e:
				log(f"Failed to install {pkg}! Skipping for now...", WARNING)
				log(e, WARNING)
				continue
def install_deps_for_pkg(pkg: Package):
	"""
	Fetches the dependencies of a package from debian's servers.
	We make apt do the heavy lifting
	:param Package: A package to install dependencies for.
	"""
	assert type(pkg) == Package
	deps = []
	print(pkg)
	info = pkg.get_info()
	if not "Dependencies" in info["Package"]:
		return
	cmd = "apt satisfy --download-only"
	dep_string = info["Package"]["Dependencies"]
	install_deps(dep_string)


def get_pkg_list():
	"""
	Yields a list of all packages in the system
	:return list(Package):
	"""
	packages = os.listdir(f"{root}/System/Packages")
	for pkg in packages:
		pkg_name = pkg.split("***")
		if len(pkg_name) != 2:
			print(f"Corrupt package in system! \"{pkg}\" Skipping for now.")
			continue
		pkg_ret = Package(
			pkg_name[0],
			Version(pkg_name[1]),
			f"{root}/System/Packages/{pkg}"
		)
		assert type(pkg_ret) == Package
		yield pkg_ret

def search_pkg_list(name: str, strict=False):
	"""
	Searches for packages in the system package list by name.

	This function iterates over the list of packages installed in the system
	and yields packages that match the given name. If `strict` is True,
	it yields packages with an exact name match. If `strict` is False,
	it yields packages that contain the given name as a substring.

	:param name: The name or substring to search for in package names.
	:param strict: A boolean indicating whether to perform a strict name match.
	:return yield Packages:
	"""
	assert type(name) == str
	global root

	for pkg in get_pkg_list():
		if strict:
			if pkg.name == name:
				assert type(pkg) == Package
				yield pkg
		else:
			if name in pkg.name:
				assert type(pkg) == Package
				yield pkg

def get_pkg(name: str):
	"""
	Returns the newest package matching the given name.

	This function iterates over the list of packages installed in the system
	and returns the newest package that matches the given name. If no packages
	match the given name, it returns None.

	:param name: The name of the package to search for.
	:return Package: The newest package matching the given name, or None if no packages match.
	"""
	assert type(name) == str
	candidates = list(search_pkg_list(name))
	if not candidates: return None
	newest = None
	for candidate in candidates:
		if newest == None:
			newest = candidate
		else:
			if newest.version < candidate.version:
				newest = candidate
	assert type(newest) == Package
	return newest

def list_directory_tree(path: str) -> list:
	"""
	Returns a recursive list of all files and directories in the given path.

	:param path: The path to list the directory tree of.
	:return: A list of all files and directories (recursively) in the given path.
	"""
	assert type(path) == str
	files = []
	for root, dirs, filenames in os.walk(path):
		files.append(root)
		files.extend(os.path.join(root, f) for f in filenames)
	files.remove(path)
	assert type(files) == list
	return files




def parse_deps(deps: list) -> list:
	"""
	Parses a list of dependencies and returns a
	list of `Dependency` representing the parsed dependencies.

	The dep_info_t structure has the following fields:
		- name: The name of the package.
		- comparison: The comparison operator used in the dependency string.
		- version: The version of the package.

	For example, if given the input ["pkg1 (>= 2.1.0)", "pkg2 (= 3.2.1)", "pkg3 (<= 4.3.2)", "pkg4"],
	the output will be:
	[
		Dependency("pkg1", [">="], ["2.1.0"]),
		Dependency("pkg2", ["="], ["3.2.1"]),
		Dependency("pkg3", ["<="], ["4.3.2"]),
		Dependency("pkg4", None, None)
	]

	:param deps: A list of strings representing dependencies.
	:return list(Dependency):
	"""
	assert type(deps) == list
	for dep in deps:
		assert type(dep) == str
	deps_info = []
	for dep in deps:
		deps_info.append(Dependency.parse(dep))

	assert type(deps_info) == list
	return deps_info

def deps_to_pkgs(deps_info: list) -> list:
	"""
	Takes a list of Dependency objects and returns a list of Package objects representing
	the newest version of each dependency that satisfies the dependency's comparison operators.

	:param deps_info: A list of Dependency objects.
	:return list(Package):
	"""
	assert type(deps_info) == list
	for d in deps_info:
		assert type(d) == Dependency
	pkg_deps = []

	for dep in deps_info:
		pkgs = list(search_pkg_list(dep.name, strict=True))
		if not pkgs:
			raise ValueError(f"Could not find dependency \"{dep}\"")

		best = None
		for pkg in pkgs:
			if best == None and dep.satisfied_by(pkg.version):
				best = pkg
			elif best == None:
				continue
			elif pkg.version > best.version and dep.satisfied_by(pkg.version):
				best = pkg
		if best == None:
			raise ValueError(f"Could not find dependency \"{dep.name}\"")
		pkg_deps.append(best)

	assert type(pkg_deps) == list
	return pkg_deps

def get_files_and_directories_from_pkgs(deps: list):
	"""
	:param deps: A list of `Package` objects.
	:return list(item_t): A list of `item_t` objects representing the
	files and directories in the given packages.
	"""
	assert type(deps) == list
	for dep in deps:
		assert type(dep) == Package

	class item_t:
		def __init__(self, bwrap_loc, fullpath, pkg, occurences):
			self.bwrap_loc = bwrap_loc
			self.fullpath = fullpath
			self.pkg = pkg
			self.occurences = occurences
		def __repr__(self):
			return f"Item({self.bwrap_loc}, {self.fullpath}, {self.pkg.name}, {self.occurences})"

	# generate trees of all of them, and merge them together
	directories = []
	files = []
	for dep in deps:
		# for each dependency...
		dep_root = os.path.join(dep.path, "chroot")
		dep_contents = list_directory_tree(dep_root)
		for dep_item in dep_contents:
			if os.path.isdir(dep_item):
				directories.append(item_t(
					dep_item[len(dep_root):], # removes down the common prefix
					dep_item,
					dep,
					None
				))
			elif os.path.isfile(dep_item):
				files.append(item_t(
					dep_item[len(dep_root):], # removes down the common prefix
					dep_item,
					dep,
					None
				))

	# So now we have a list of all the files and directories that need to be included
	# This list is massive but we must not panic...

	# files, and directories are all of type item_t
	# so we need to convert them to their bwrap location

	directories_bwrap_locations = [x.bwrap_loc for x in directories]
	files_bwrap_locations = [x.bwrap_loc for x in files]

	dirs_occ = occurence_count(directories_bwrap_locations)
	files_occ = occurence_count(files_bwrap_locations)

	for dir,occ in zip(directories, dirs_occ):
		dir.occurences = dirs_occ[occ]

	for file,occ in zip(files, files_occ):
		file.occurences = files_occ[occ]

	assert type(directories) == list
	assert type(files) == list
	return files, directories

def occurence_count(l: list) -> dict:
	"""
	Returns a dictionary where the keys are the elements of the list and the values are the
	number of occurances of each element in the list.

	Example:
		>>> occurence_count([1, 1, 2, 3, 4, 4, 5])
		{1: 2, 2: 1, 3: 1, 4: 2, 5: 1}
	"""
	assert type(l) == list
	r = {x: l.count(x) for x in l}
	assert type(r) == dict
	return r


def fill_dep_tree(dep, ignore_list=[]) -> list:
	"""
	Returns a list of all dependencies required for the container from a list of all the
	dependenecies that are specified by the caller.

	:param deps: A Dependency object
	:return list(Package): A list of all dependencies required for the dependency
	"""
	assert type(dep) == Dependency
	assert type(ignore_list) == list

	output = []
	# Package
	dep = deps_to_pkgs([Dependency.parse(dep)])[0] # ;)

	if dep in ignore_list:
		return []
	# Package
	output.append(dep)

	for child in dep.get_deps(): # Packages
		if child not in ignore_list:
			print(child)
			print(child.get_deps())
			output.extend(fill_dep_tree(child.get_deps(), ignore_list=output))

	assert type(output) == list
	for out in output:
		assert type(out) == Package
	return output

def fill_dep_tree_from_list(deps: list) -> list:
	"""
	:return list(Package):
	"""
	assert type(deps) == list
	output = []
	for dep in deps:
		output.extend(fill_dep_tree(dep, ignore_list=output))
	assert type(output) == list
	for out in output:
		assert type(out) == Package
	return output



def generate_bwrap_args(deps: list) -> list:
	"""
	Generates a list of bubblewrap arguments for setting up the container environment.

	This function constructs bubblewrap arguments to set up the container with necessary
	overlays and bind mounts. The root of the system is mounted as an overlay for the source,
	and specific directories are bound to their respective locations.

	deps should be passed in a form of
	["pkg1==2.1.0", "pkg2>=3.2.1", "pkg3<=4.3.2"]

	:param deps: A list of dependency strings
	:return: A list of bubblewrap arguments for container setup.
	"""
	global root
	args = []
	args.append(f"--overlay-src {root}")
	args.append(f"--tmp-overlay /")
	args.append(f"--bind {root}/System /System")
	args.append(f"--bind {root}/Users /Users")
	args.append(f"--bind {root}/Volumes /Volumes")

	# generate list of packages that need to be included

	# Parse list of dependencies
	# deps_info = parse_deps(deps)

	# Get list of packages from list of dependencies
	# deps = deps_to_pkgs(deps_info)
	deps = fill_dep_tree_from_list(deps)

	# item_t = namedtuple('item_t', ['bwrap_loc', 'fullpath', 'pkg', "occurences"])

	# Get list of files and directories from list of dependencies
	files, directories = get_files_and_directories_from_pkgs(deps)

	# We need to follow the rules defined in Pkgs.md

	# for each directory...
	# if occurence count = 1, symlink
	# if occurence count > 1, create directory
	symlinked = []
	for dir in directories:
		if dir.occurences == 1:
			# Everything is mounted within / so we don't have to worry about root inside the
			# container. But outside of the container we do. therfore, src_path must be to
			# inside /System/Packages not {root}/System/Package.
			for sym in symlinked:
				if dir.bwrap_loc.startswith(sym):
					break
			else:
				src_path = dir.fullpath[len(root):]
				args.append(f"--symlink {dir.bwrap_loc} {src_path}")
				symlinked.append(dir.bwrap_loc)
		elif dir.occurences > 1:
			args.append(f"--mkdir {dir.bwrap_loc}")

	# for each file...
	# if occurence count = 1, symlink
	# if occurence count > 1, only the file closest to the main package will be symlinked

	for file in files:
		if True: # file.occurences == 1:
			# Everything is mounted within / so we don't have to worry about root inside the
			# container. But outside of the container we do. therfore, src_path must be to
			# inside /System/Packages not {root}/System/Package.
			for sym in symlinked:
				if file.bwrap_loc.startswith(sym):
					break
			else:
				src_path = file.fullpath[len(root):]
				args.append(f"--symlink {file.bwrap_loc} {src_path}")

	return args



































if __name__ != "__main__":
	print("This file is not meant to be imported!")
	sys.exit(1)

parser = argparse.ArgumentParser(description='dalixOS package manager')
parser.add_argument(
	'-r',
	'--root',
	help='Root directory of the system',
	default=''
)
parser.add_argument(
	'-i',
	'--install',
	help='Install a .deb package',
)
parser.add_argument(
	'-t',
	'--test',
	help='Run a random test script',
	action='store_true'
)
parser.add_argument(
	'-b',
	'--bootstrap',
	help='Init a system',
	action='store_true'
)

args = parser.parse_args()

root = args.root

if args.install:
	if args.install.startswith("./"):
		install_deb(args.install)
	else:
		install_pkg_from_online(args.install)
elif args.test:
	args = generate_bwrap_args([
		"neovim",
	])
	for arg in args:
		print(arg)
elif args.bootstrap:
	init_system()
