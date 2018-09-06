# Scripts
A random collection of useful scripts. These are mostly intended for myself, but others can use them if they so desire.

## file_fuzzer.py
A very simple file fuzzer.
```sh
python file_fuzzer.py --in-dir ~/input_data/ --out-dir ~/output_data/ --n 3
```

## fuzzer.py
Implements simple fuzzing logic. Not meant to be called directly, but instead imported into another script to perform network or file fuzzing.

## mine_boss.py
A python script for scheduling compute tasks. Originally intended to swap between miners, keeping the computer on the most profitable coin, but can be used for scheduling non-mining tasks as well. Logic is controlled from the configuration file, an example of which is provided.
```sh
python mine_boss.py --config miner.config
```

## proxy.py
A simple network proxy for use in fuzz testing my own code.
```sh
python proxy.py --bindip 127.0.0.1 --bindport 8080 --destip 127.0.0.1 --destport 80 --post do_stuff.py
```

## update_all_repos.py
A python script that (optionally) recurses through a directory looking for git repos. When a git repo is found it updates it and (optionally) prunes local branches that are no longer on the remote.
```sh
python update_all_repos.py --root /home/me/src --prune --recurse
```
