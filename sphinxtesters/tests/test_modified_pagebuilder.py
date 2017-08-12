""" Test ModifiedPageBuilder
"""

from io import StringIO
from os.path import (dirname, join as pjoin, isdir, isfile)

from sphinxtesters.sphinxutils import ModifiedPageBuilder

from nose.tools import assert_true, assert_equal, assert_raises

HERE = dirname(__file__)
PROJ1 = pjoin(HERE, 'proj1')

NEW_PAGE = u"""
Fancy title
+++++++++++

Compelling text
"""


class TestModifiedPageBuilder(ModifiedPageBuilder):

    page_source_template = PROJ1
    default_page = 'a_page'

    @classmethod
    def modify_source(cls):
        page_fobj = StringIO(NEW_PAGE)
        cls.replace_page(page_fobj)

    def test_a_build(self):
        doctree = self.get_doctree(self.default_page)
        doctree_str = self.doctree2str(doctree)
        expected = (
            '<title>Fancy title</title>\n'
            '<paragraph>Compelling text</paragraph>')
        assert_equal(doctree_str, expected)
