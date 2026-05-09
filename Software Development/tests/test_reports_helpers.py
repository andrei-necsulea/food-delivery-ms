from collections import deque


def _read_last_lines(file_path, line_count):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as log_file:
        return list(deque(log_file, maxlen=line_count))


def test_read_last_lines_returns_last_two_lines(tmp_path):
    log_file = tmp_path / 'app.log'
    log_file.write_text('line1\nline2\nline3\n', encoding='utf-8')

    assert _read_last_lines(log_file, 2) == ['line2\n', 'line3\n']


def test_read_last_lines_when_count_exceeds_file(tmp_path):
    log_file = tmp_path / 'app.log'
    log_file.write_text('a\nb\n', encoding='utf-8')

    assert _read_last_lines(log_file, 10) == ['a\n', 'b\n']
