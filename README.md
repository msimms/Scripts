# Scripts
A random collection of useful scripts. These are mostly intended for myself, but others can use them if they so desire. This repo is basically my public junk drawer.

## test_tools/file_fuzzer.py
A very simple file fuzzer.
```sh
python file_fuzzer.py --in-dir ~/input_data/ --out-dir ~/output_data/ --n 3
```

## test_tools/fuzzer.py
Implements simple fuzzing logic. Not meant to be called directly, but instead imported into another script to perform network or file fuzzing. Options are passed to the constructor as a dictionary.
```python
import fuzzer
fuzz = fuzzer.Fuzzer({})
out_contents, out_len = fuzz.fuzz(in_contents, len(in_contents))
```

## test_tools/proxy.py
A simple network proxy for use in fuzz testing my own code.
```sh
python proxy.py --bindip 127.0.0.1 --bindport 8080 --destip 127.0.0.1 --destport 80 --post do_stuff.py
```

## kvb.py
A script for cleaning up whitespace. The name is an inside joke.
```sh
python kvb.py --dir ~/src/myproject/ --trailing-whitespace
```

## make_python.py
In progress.

## mine_boss.py
A python script for scheduling compute tasks. Originally intended to swap between miners, keeping the computer on the most profitable coin, but can be used for scheduling non-mining tasks as well. I use it to keep one of my more power computers swapping between various charitable projects. Logic is controlled from the configuration file, an example of which is provided.
```sh
python mine_boss.py --config miner.config
```

## pysync.py
A simplistic python knockoff of rsync. I wrote it because rsync was corrupting file dates and also stumbling into os-specific bugs, so writing this seemed like an easy alternative. It compares files using a SHA-256 hash. By default, it operates recursively. Files will not be copied unless the `sync` flag is provided.
```sh
python pysync.py --source-dir ~/Downloads/src/ --dest-dir ~/Downloads/dst/ --sync --fix-dates
python pysync.py --source-dir ~/Downloads/src/ --dest-dir ~/Downloads/dst/ --report-missing-files
```

## shell_over_slack.py
This is a very dumb script and no one should use it. It listens to a Slack channel for commands and then does them.

## update_all_repos.py
A python script that (optionally) recurses through a directory looking for git repos. When a git repo is found it updates it and (optionally) prunes local branches that are no longer on the remote. I use this for keeping unattended machines up-to-date with the latest code.
```sh
python update_all_repos.py --root /home/me/src --prune --recurse
```

## License
This is open source software and is released under the MIT license.
