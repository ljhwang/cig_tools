"""Exports `filepaths_gen` function.
"""

import os
import pathlib


def _is_hidden_path(path: pathlib.PurePath) -> bool:
    """Returns `True` if `path` is a hidden file or directory.
    """
    def _is_hidden_basename(basename):
        return basename.startswith(os.extsep)

    return any(_is_hidden_basename, path.parts)


def _is_visible_path(path: pathlib.PurePath) -> bool:
    """Returns `False` if `path` is a hidden file or directory.
    """
    return not _is_hidden_path(path)


def _os_walk_filter(filter_func, top_dir):
    """Generator for filtered `os.walk` concrete paths. `filter_func` must
    accept a `pathlib.Path` relative to `top_dir`.
    """
    for cwd, dirs, files in os.walk(top_dir):
        for dirname in dirs:
            if not filter_func(
                    pathlib.Path(cwd, dirname).relative_to(top_dir)):
                dirs.remove(dirname)

        for filename in files:
            path = pathlib.Path(cwd, filename).relative_to(top_dir)
            if filter_func(path):
                yield path


def filepaths_gen(top_dir, include_hidden=False):
    """Generator for concrete filepaths in `top_dir` and sub directores. If
    `include_hidden` is false, the generator will not include hidden files or
    files in hidden directories. All paths will be relative to `top_dir`.
    """
    if not include_hidden:
        return _os_walk_filter(_is_visible_path, top_dir)
    else:
        return _os_walk_filter(lambda _: True, top_dir)
