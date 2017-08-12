""" Test TempApp, TestApp classes
"""

from os.path import (join as pjoin, isdir)

from sphinxtesters.sphinxutils import TempApp

from nose.tools import assert_false, assert_equal


def assert_contents_equal(fname, contents, mode='t'):
    with open(fname, 'r' + mode) as fobj:
        f_contents = fobj.read()
    assert_equal(f_contents, contents)


def test_tempapp():
    rst_txt = 'A simple page'
    app = TempApp(rst_txt)
    app.build()
    app_path = app.tmp_dir
    assert_contents_equal(pjoin(app_path, 'contents.rst'), rst_txt)
    assert_contents_equal(pjoin(app_path, 'conf.py'), '')
    app.cleanup()
    assert_false(isdir(app_path))
