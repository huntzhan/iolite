from pathlib import Path
import shutil
import os
import logging
from tqdm import tqdm as _tqdm


def folder(raw_path, exists=False, reset=False, touch=False):
    path = Path(raw_path)

    if exists:
        if not path.exists():
            raise FileNotFoundError(f'{raw_path} not found.')
        if not path.is_dir():
            raise NotADirectoryError(f'{raw_path} should be a folder.')

    if reset:
        try:
            if path.exists():
                shutil.rmtree(path)
            os.makedirs(path)
        except OSError:
            logging.warn(f'Cannot remove {raw_path}')

    if touch:
        os.makedirs(path, exist_ok=True)

    return path


def file(raw_path, exists=False):
    path = Path(raw_path)

    if exists:
        if not path.exists():
            raise FileNotFoundError(f'{raw_path} not found.')
        if not path.is_file():
            raise IsADirectoryError(f'{raw_path} should be a file.')

    return path


def read_text_lines(
    path,
    buffering=-1,
    encoding=None,
    errors=None,
    newline=None,
    strip=True,
    skip_empty=True,
    tqdm=False,
):
    with path.open(
        mode='r',
        buffering=buffering,
        encoding=encoding,
        errors=errors,
        newline=newline,
    ) as fin:
        if tqdm:
            fin = _tqdm(fin)

        for line in fin:
            if strip:
                line = line.strip()
            if not skip_empty or line:
                yield line


def write_text_lines(
    path,
    lines,
    buffering=-1,
    encoding=None,
    errors=None,
    newline=None,
    strip=True,
    skip_empty=True,
    tqdm=False,
):
    with path.open(
        mode='w',
        buffering=buffering,
        encoding=encoding,
        errors=errors,
        newline=newline,
    ) as fout:
        if tqdm:
            fout = _tqdm(fout)

        for line in lines:
            if strip:
                line = line.strip()
            if skip_empty and not line:
                continue
            fout.write(line)
            fout.write('\n')
