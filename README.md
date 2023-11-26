# treecat

Displays a tree view of files and their contents

## Installation

Recommended (latest release):
```sh
python3 -m pip install git+https://github.com/Knio/treecat.git@master
```

`master` branch:
```sh
python -m pip install git+https://github.com/Knio/treecat.git
```

Manual:
```sh
git clone https://github.com/Knio/treecat.git
cd treecat
python setup.py install
```


## Usage

```sh
$ python -m treecat test/
/mnt/k/Programming/treecat/test
├── broken -> foo
├── bye.txt
│   █ So long,
│   █ cruel world.
├── hello -> hi.txt
└── hi.txt => █ Hello, World!
```
