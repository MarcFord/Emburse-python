import sys
from emburse import util


def test_json():
    assert util.json


def test_parse_qsl():
    assert util.parse_qsl


def test_string_io():
    assert util.StringIO


def test_utf8():
    if sys.version_info < (3, 0):
        unicode_str = "this is a test".encode('ascii')
        assert util.utf8(unicode_str) == "this is a test"
    else:
        assert util.utf8('testing 1 2 3') == 'testing 1 2 3'
