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
    assert len(list(lines)) == 4

    lines = read_text_lines(file(some_file), strip=False)
    assert list(lines) == ['line 1\n', '\n', '  line 2\n', 'line 3 ']

    lines = read_text_lines(file(some_file), skip_empty=True)
    assert list(lines) == ['line 1', 'line 2', 'line 3']

    assert not capsys.readouterr().out
    list(read_text_lines(file(some_file), tqdm=True))
    assert '[00:00' in capsys.readouterr().err


def test_write_text_lines(tmpdir, capsys):
    some_file = tmpdir.join('file')
    write_text_lines(file(some_file), [' foo', '', 'bar '])
    assert some_file.read() == 'foo\n\nbar\n'

    some_file = tmpdir.join('file2')
    write_text_lines(file(some_file), [' foo', '', 'bar '], skip_empty=True)
    assert some_file.read() == 'foo\nbar\n'

    some_file = tmpdir.join('file3')
    write_text_lines(file(some_file), [' foo', 'bar '], strip=False)
    assert some_file.read() == ' foo\nbar \n'

    some_file = tmpdir.join('file4')
    write_text_lines(file(some_file), [' foo', 'bar '], newline='\r')
    assert some_file.read_binary() == b'foo\rbar\r'

    assert not capsys.readouterr().out
    write_text_lines(file(some_file), [' foo', 'bar '], tqdm=True)
    assert '[00:00' in capsys.readouterr().err


def test_json_lines(tmpdir):
    some_file = tmpdir.join('file')
    structs = [{'foo': 'bar'}, {'baz': '中文'}]
    write_json_lines(file(some_file), structs)
    assert list(read_json_lines(file(some_file))) == structs

    some_file = tmpdir.join('file2')
    write_json_lines(file(some_file), structs, ensure_ascii=False)
    assert list(read_json_lines(file(some_file))) == structs

    class Foo:
        pass

    some_file = tmpdir.join('file3')
    with pytest.raises(TypeError):
        write_json_lines(file(some_file), [Foo()])

    some_file = tmpdir.join('file4')
    write_text_lines(file(some_file), ['foobar'])
    with pytest.raises(json.JSONDecodeError):
        list(read_json_lines(file(some_file)))


def test_csv_lines(tmpdir):
    some_file = tmpdir.join('file')
    structs = [['a', 'b', 'c'], ['d', 'e', 'f']]
    write_csv_lines(file(some_file), structs)
    assert list(read_csv_lines(file(some_file))) == structs
    assert list(read_csv_lines(file(some_file), skip_header=True)) == structs[1:]

    some_file = tmpdir.join('file2')
    structs = [{'a': 1, 'b': 2}, {'b': 4, 'a': 3}]
    write_csv_lines(file(some_file), structs, from_dict=True)
    assert list(read_csv_lines(file(some_file))) == [['a', 'b'], ['1', '2'], ['3', '4']]
