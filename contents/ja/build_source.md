---
type: snippet
---


# Pythonのビルド手順(Unix)


## 1. Pythonのビルドに必要な依存ファイルをインストールします。

:jinja:`{{ page.load("../unix_deps.md").html }}`


## 2. ダウンロードしたソースファイルを展開します。

```sh
# 例
wget https://www.python.org/ftp/python/3.x.y/Python-3.x.y.tar.xz
tar xJf Python-3.x.y.tar.xz
```



## 3. ビルド

以下のコマンドで、`/usr/local/` 以下にインストールします。

```sh
cd Python3.x.y
./configure
make
sudo make install
```

デフォルト以外のディレクトリにインストールする場合は、`configure` に `--prefix`オプションを指定します。

```sh
cd Python3.x.y
./configure --prefix=/home/user/.local/python
make
make install
```

