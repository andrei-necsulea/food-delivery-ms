import importlib.util
import sys
from pathlib import Path
from types import ModuleType


class FakeHttpResponse:
    def __init__(self, content, content_type=None):
        self._content = content
        self.headers = {}

    @property
    def content(self):
        return self._content.encode('utf-8') if isinstance(self._content, str) else self._content

    def __setitem__(self, k, v):
        self.headers[k] = v

    def __getitem__(self, k):
        return self.headers.get(k)


def test_export_csv_contains_headers_and_rows(monkeypatch):
    fake_django = ModuleType('django')
    fake_django.__path__ = []
    fake_http = ModuleType('django.http')
    fake_http.HttpResponse = FakeHttpResponse
    monkeypatch.setitem(sys.modules, 'django', fake_django)
    monkeypatch.setitem(sys.modules, 'django.http', fake_http)

    exporters_path = Path(__file__).resolve().parents[1] / 'reports' / 'exporters.py'
    spec = importlib.util.spec_from_file_location('exporters_under_test', exporters_path)
    exporters = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(exporters)

    filename = 'testfile'
    headers = ['id', 'name']
    rows = [[1, 'Alice'], [2, 'Bob']]

    resp = exporters.export_csv(filename, headers, rows)
    content = resp.content.decode('utf-8')

    assert 'id' in content and 'name' in content
    assert '1' in content
    assert '2' in content
    # Content-Disposition header should be set
    assert 'attachment' in resp['Content-Disposition']
