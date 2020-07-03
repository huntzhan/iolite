from pathlib import Path
import shutil
import os
import logging
import json
import csv
from collections import abc

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
    skip_empty=False,
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

        for text in fin:
            if strip:
                text = text.strip()
            if not skip_empty or text:
                yield text


def write_text_lines(
    path,
    texts,
    buffering=-1,
    encoding=None,
    errors=None,
    newline=None,
    strip=True,
    skip_empty=False,
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

        for text in texts:
            if strip:
                text = text.strip()
            if skip_empty and not text:
                continue
            fout.write(text)
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
    for num, text in enumerate(
        read_text_lines(
            path,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
            strip=False,
            tqdm=tqdm,
        )
    ):
        try:
            struct = json.loads(text)
            if skip_empty and not struct:
                continue
            yield struct

        except json.JSONDecodeError:
            if not ignore_error:
                raise
            if not silent:
                logging.warning(f'Cannot parse #{num}: "{text}"')


def _encode_json_lines(structs, skip_empty, ensure_ascii, silent, ignore_error):
    for num, struct in enumerate(structs):
        try:
            if skip_empty and not struct:
                continue
            text = json.dumps(struct, ensure_ascii=ensure_ascii)
            yield text

        except (TypeError, OverflowError, ValueError):
            if not ignore_error:
                raise
            if not silent:
                logging.warning(f'Cannot encode #{num}: "{struct}"')


def write_json_lines(
    path,
    structs,
    buffering=-1,
    encoding=None,
    errors=None,
    newline=None,
    skip_empty=False,
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


def read_csv_lines(
    path,
    buffering=-1,
    encoding=None,
    errors=None,
    newline=None,
    header_exists=True,
    skip_header=False,
    match_header=True,
    to_dict=False,
    ignore_error=False,
    silent=False,
    tqdm=False,
    dialect='excel',
    **fmtparams,
):
    if not header_exists and match_header:
        msg = 'Cannot match header if header does not exists.'
        if not ignore_error:
            raise RuntimeError(msg)
        elif not silent:
            logging.warning(msg)
        return

    if to_dict and not match_header:
        msg = 'Must match header before converting to dict.'
        if not ignore_error:
            raise RuntimeError(msg)
        elif not silent:
            logging.warning(msg)
        return

    with path.open(
        mode='r',
        buffering=buffering,
        encoding=encoding,
        errors=errors,
        newline=newline,
    ) as fin:
        if tqdm:
            fin = _tqdm(fin)

        header = None
        for num, struct in enumerate(csv.reader(fin, dialect, **fmtparams)):
            if header_exists and num == 0:
                if not isinstance(struct, abc.Iterable):
                    msg = 'Header not iterable.'
                    if not ignore_error:
                        raise TypeError(msg)
                    elif not silent:
                        logging.warning(msg)
                    return

                header = list(struct)
                if skip_header:
                    continue

            if match_header:
                # Make linter happy.
                assert isinstance(header, list)
                if len(header) != len(struct):
                    msg = f'Cannot match #{num} = {struct} with header header = {header}.'
                    if not ignore_error:
                        raise ValueError(msg)
                    elif not silent:
                        logging.warning(msg)
                    # Skip this line.
                    continue

                if to_dict:
                    struct = dict(zip(header, struct))

            yield struct


def write_csv_lines(
    path,
    structs,
    buffering=-1,
    encoding=None,
    errors=None,
    newline=None,
    ignore_error=False,
    silent=False,
    from_dict=False,
    set_missing_key_to_none=False,
    ignore_unknown_key=True,
    tqdm=False,
    dialect='excel',
    **fmtparams,
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

        csv_writer = csv.writer(fout, dialect, **fmtparams)

        from_dict_keys = None
        if from_dict:
            if not structs:
                msg = 'empty list.'
                if not ignore_error:
                    raise ValueError(msg)
                elif not silent:
                    logging.warning(msg)
                return

            if not isinstance(structs[0], abc.Mapping):
                msg = f'structs[0]={structs[0]} should be a mapping.'
                if not ignore_error:
                    raise TypeError(msg)
                elif not silent:
                    logging.warning(msg)
                return

            from_dict_keys = list(structs[0])
            csv_writer.writerow(from_dict_keys)

        for num, struct in enumerate(structs):
            if from_dict:
                if not isinstance(struct, abc.Mapping):
                    msg = f'#{num} {struct} should be a mapping.'
                    if not ignore_error:
                        raise TypeError(msg)
                    elif not silent:
                        logging.warning(msg)
                    # Skip this line.
                    continue

                # Make linter happy.
                assert isinstance(from_dict_keys, list)
                items = []
                skip_this_struct = False
                for key in from_dict_keys:
                    if key not in struct and not set_missing_key_to_none:
                        msg = f'#{num} key "{key}" not found.'
                        if not ignore_error:
                            raise KeyError(msg)
                        if not silent:
                            logging.warning(msg + ' Skip.')
                        # Abort.
                        skip_this_struct = True
                        break

                    items.append(struct.get(key))

                if skip_this_struct:
                    continue
                if not ignore_unknown_key:
                    unknown_keys = set(struct) - set(from_dict_keys)
                    if unknown_keys:
                        msg = f'#{num} contains unknown_keys {unknown_keys}'
                        if not ignore_error:
                            raise KeyError(msg)
                        if not silent:
                            logging.warning(msg + ' Skip.')
                        continue

                csv_writer.writerow(items)

            else:
                if not isinstance(struct, abc.Iterable):
                    msg = f'#{num} {struct} not iterable.'
                    if not ignore_error:
                        raise ValueError(msg)
                    if not silent:
                        logging.warning(msg + ' Skip.')
                    continue

                csv_writer.writerow(struct)


def read_json(
    path,
    buffering=-1,
    encoding=None,
    errors=None,
    newline=None,
    ignore_error=False,
    silent=False,
):
    with path.open(
        mode='r',
        buffering=buffering,
        encoding=encoding,
        errors=errors,
        newline=newline,
    ) as fin:
        try:
            return json.load(fin)
        except json.JSONDecodeError:
            if not ignore_error:
                raise
            if not silent:
                logging.warning(f'Cannot load {path}')
            return {}


def write_json(
    path,
    struct,
    buffering=-1,
    encoding=None,
    errors=None,
    newline=None,
    ensure_ascii=True,
    indent=None,
    ignore_error=False,
    silent=False,
):
    with path.open(
        mode='w',
        buffering=buffering,
        encoding=encoding,
        errors=errors,
        newline=newline,
    ) as fout:
        try:
            json.dump(struct, fout, ensure_ascii=ensure_ascii, indent=indent)
        except (TypeError, OverflowError, ValueError):
            if not ignore_error:
                raise
            if not silent:
                logging.warning(f'Cannot encode "{struct}"')


# TODO: toml
