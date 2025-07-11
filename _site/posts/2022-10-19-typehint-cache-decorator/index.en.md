---
title: Hinting Cache Decorator Types
format: hugo
jupyter: python3
author: Patrick Sadil
date: '2022-10-23'
slug: typehint-callable
categories:
  - gist
tags:
  - python
subtitle: ''
summary: ''
authors: []
lastmod: '2022-10-23T22:59:09-04:00'
featured: 'no'
projects: []
---


Recently, I encountered a python function that I didn't want to modify, but whose output I wanted cached. Providing typehints for this seemed a bit complicated, so I'm posting this gist as a reminder. The main trick involves extensions from [PEP 612](https://peps.python.org/pep-0612/).

In words, the decorator will take some function `f` that takes parameters `P` and produces a `str`. I want to be able to call `f` and additionally provide a filename that will point to a file in which the string will be written. The cache will be super basic, checking just for the existence of the file and skipping `f` if that file exists.

In code, that looks like the following

``` python
from pathlib import Path
import typing
P = typing.ParamSpec("P")

def cache_str(f: typing.Callable[P, str]) -> typing.Callable[typing.Concatenate[Path, P], str]:
    def wrapper(_filename: Path, *args: P.args, **kwargs: P.kwargs) -> str:
        if _filename.exists():
            print(f"Found cached result {_filename}. Skipping!")
            i = _filename.read_text()
        else:
            # run!
            i = f(*args, **kwargs)
            _filename.touch()
            _filename.write_text(i)
        return i
    return wrapper
```

And then the decorator could be used like

``` python
@cache_str
def get_str(msg: str) -> str:
    print(
        "This function takes so long to run--I hope that I don't need to run it twice"
    )
    return msg
```

``` python
import tempfile

msg = "cached message"

with tempfile.TemporaryDirectory() as tmpdir:
    tmp_path = Path(tmpdir) / "cache.txt"
    get_str(tmp_path, msg=msg)
    print("trying to read message from cache...")
    print(f"{tmp_path.read_text()=}")
    get_str(tmp_path, msg=msg)
```

    This function takes so long to run--I hope that I don't need to run it twice
    trying to read message from cache...
    tmp_path.read_text()='cached message'
    Found cached result /var/folders/v_/kcpb096s1m3_37ctfd2sp2xm0000gn/T/tmpc3scqbcc/cache.txt. Skipping!

This is neat, but although my editor recognizes that the decorated function can accept a path as the first argument, that first argument could not be named. This appears to have been an explicit choice in PEP 612, made to avoid potential clashes with keyword arguments from the decorated function.
