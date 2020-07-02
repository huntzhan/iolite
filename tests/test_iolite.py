import pytest
import os.path
from iolite import *


def test_folder(tmpdir):
    with pytest.raises(FileNotFoundError):
        folder(str(tmpdir.join('not-exists')), exists=True)

    with pytest.raises(NotADirectoryError):
        path = tmpdir.join('is-a-file')
        path.write('something')
        folder(path, exists=True)

    path = tmpdir.join('not-exists')
    folder(path, reset=True)
    assert os.path.exists(path)

    path = tmpdir.join('not-exists-2')
    folder(path, touch=True)
    assert os.path.exists(path)

    path = tmpdir.mkdir('folder')
    some_file = (path / 'file')
    some_file.write('something')
    folder(path, reset=True)
    assert not os.path.exists(some_file)


def test_file(tmpdir):
    with pytest.raises(FileNotFoundError):
        file(tmpdir.join('not-exists'), exists=True)

    with pytest.raises(IsADirectoryError):
        path = tmpdir.mkdir('folder')
        file(path, exists=True)


def test_read_text_lines(tmpdir, capsys):
    some_file = tmpdir.join('file')
    some_file.write('''line 1

  line 2
line 3 ''')
    lines = read_text_lines(file(some_file))
    assert list(lines) == ['line 1', 'line 2', 'line 3']

    lines = read_text_lines(file(some_file), strip=False)
    assert list(lines) == ['line 1\n', '\n', '  line 2\n', 'line 3 ']

    lines = read_text_lines(file(some_file), skip_empty=False)
    assert len(list(lines)) == 4

    assert not capsys.readouterr().out
    list(read_text_lines(file(some_file), tqdm=True))
    assert '[00:00' in capsys.readouterr().err


def test_write_text_lines(tmpdir, capsys):
    some_file = tmpdir.join('file')
    write_text_lines(file(some_file), [' foo', '', 'bar '])
    assert some_file.read() == 'foo\nbar\n'

    some_file = tmpdir.join('file2')
    write_text_lines(file(some_file), [' foo', '', 'bar '], skip_empty=False)
    assert some_file.read() == 'foo\n\nbar\n'

    some_file = tmpdir.join('file3')
    write_text_lines(file(some_file), [' foo', '', 'bar '], strip=False)
    assert some_file.read() == ' foo\nbar \n'

    assert not capsys.readouterr().out
    write_text_lines(file(some_file), [' foo', '', 'bar '], tqdm=True)
    assert '[00:00' in capsys.readouterr().err
