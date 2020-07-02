from pathlib import Path
import shutil
import os
import logging
import json

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
            logging.warning(f'Cannot remove {raw_path}')

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


def read_json_lines(
    path,
    buffering=-1,
    encoding=None,
    errors=None,
    newline=None,
    skip_empty=True,
    ignore_error=False,
    silent=False,
    tqdm=False,
):
    for line_num, line in enumerate(
        read_text_lines(
            path,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
            strip=True,
            skip_empty=skip_empty,
            tqdm=tqdm,
        )
    ):
        try:
            struct = json.loads(line)
            if skip_empty and not struct:
                continue
            yield struct

        except json.JSONDecodeError:
            if not silent:
                logging.warning(f'Cannot parse L{line_num}: "{line}"')
            if not ignore_error:
                raise


def _encode_json_lines(structs, skip_empty, ensure_ascii, silent, ignore_error):
    for line_num, struct in enumerate(structs):
        try:
            if skip_empty and not struct:
                continue
            line = json.dumps(struct, ensure_ascii=ensure_ascii)
            yield line

        except (TypeError, OverflowError, ValueError):
            if not silent:
                logging.warning(f'Cannot encode L{line_num}: "{struct}"')
            if not ignore_error:
                raise


def write_json_lines(
    path,
    structs,
    buffering=-1,
    encoding=None,
    errors=None,
    newline=None,
    skip_empty=True,
    ensure_ascii=True,
    ignore_error=False,
    silent=False,
    tqdm=False,
):
    write_text_lines(
        path,
        _encode_json_lines(
            structs,
            skip_empty=skip_empty,
            ensure_ascii=ensure_ascii,
            silent=silent,
            ignore_error=ignore_error,
        ),
        buffering=buffering,
        encoding=encoding,
        errors=errors,
        newline=newline,
        tqdm=tqdm,
    )


# TODO: csv
# TODO: json
# TODO: toml
