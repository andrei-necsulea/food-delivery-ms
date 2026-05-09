import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest


class FakeHttpResponse:
    def __init__(self, content, content_type=None):
        self._content = content
        self.headers = {}

    @property
    def content(self):
        return self._content if isinstance(self._content, bytes) else self._content

    def __setitem__(self, k, v):
        self.headers[k] = v

    def __getitem__(self, k):
        return self.headers.get(k)


def test_export_xlsx_raises_when_openpyxl_missing(monkeypatch):
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

    monkeypatch.setattr(exporters, 'openpyxl', None)

    with pytest.raises(RuntimeError):
        exporters.export_xlsx('f', ['h1'], [[1, 2]])
