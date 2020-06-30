---
type: snippet
---


# Building Python on Unix.



## 1. Install dependencies.

:jinja:`{{ page.load("../unix_deps.md").html }}`


## 2. Extract files from archive.

```sh
# e.g.
wget https://www.python.org/ftp/python/3.x.y/Python-3.x.y.tar.xz
tar xJf Python-3.x.y.tar.xz
```


## 3. Build

Following commands install Python under `/usr/local/` directory.

```sh
cd Python3.x.y
./configure
make
sudo make install
```

To install to the other directory, run `configure` command with `--prefix` option.

```sh
cd Python3.x.y
./configure --prefix=/home/user/.local/python3.x.y
make
make install
```
