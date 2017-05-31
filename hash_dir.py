import argparse
import glob
import hashlib
import os
import shutil
import subprocess

def normjoin(*args):
	return os.path.normpath(os.path.join(*args))
	
def hash_file(file_to_hash):
	hash_algorithm = hashlib.sha256()
	file = open(file_to_hash)
	while True:
		contents = file.read(65536)
		if not contents:
			break
		hash_algorithm.update(contents)
	hash_str = hash_algorithm.hexdigest()
	return hash_str

def hash_dir(dir, rename_file, git_move_file, extension):
	files_to_hash = glob.glob(normjoin(dir, '*'))
	for file_to_hash in files_to_hash:
		try:			
			hash_str = hash_file(file_to_hash)
			print file_to_hash + " hashes to " + hash_str
			
			path, name = os.path.split(file_to_hash)
			new_file = os.path.join(path, hash_str)
			if extension is not None and len(extension) > 0:
				new_file = new_file + "." + extension
			if rename_file:
				shutil.move(file_to_hash, new_file)
			elif git_move_file:
				subprocess.call(["git", "mv", file_to_hash, new_file])
		except:
			print "Exception with " + file_to_hash

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--dir", type=str, action="store", default=".", help="Directory to hash", required=True)
	parser.add_argument("--rename", action="store_true", default=False, help="Set to TRUE to rename the files", required=False)
	parser.add_argument("--git-move", action="store_true", default=False, help="Set to TRUE to git mv the files", required=False)
	parser.add_argument("--extension", type=str, action="store", default=".", help="Extension to append", required=False)

	try:
		args = parser.parse_args()
	except IOError as e:
		parser.error(e)
		sys.exit(1)

	hash_dir(args.dir, args.rename, args.git_move, args.extension)

if __name__ == "__main__":
    main()
