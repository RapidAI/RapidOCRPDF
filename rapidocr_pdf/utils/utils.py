# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import importlib
from pathlib import Path
from typing import Union

import filetype


def import_package(name, package=None):
    try:
        module = importlib.import_module(name, package=package)
        return module
    except ModuleNotFoundError:
        return None


def which_type(content: Union[bytes, str, Path]) -> str:
    if isinstance(content, (str, Path)) and not Path(content).exists():
        raise FileExistsError(f"{content} does not exist.")

    kind = filetype.guess(content)
    if kind is None:
        raise TypeError(f"The type of {content} does not support.")

    return kind.extension
