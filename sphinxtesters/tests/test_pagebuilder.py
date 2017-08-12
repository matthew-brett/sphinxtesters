""" Test PageBuilder
"""

from os.path import (dirname, join as pjoin, isdir, isfile)

from sphinxtesters.sphinxutils import PageBuilder

from nose.tools import assert_true, assert_equal, assert_raises

HERE = dirname(__file__)
PROJ1 = pjoin(HERE, 'proj1')


class TestPageBuilder(PageBuilder):

    @classmethod
    def set_page_source(cls):
        cls.page_source = PROJ1

    def test_basic_build(self):
        assert_true(isdir(self.out_dir))
        assert_true(isdir(self.doctree_dir))
        doctree = self.get_doctree('a_page')
        assert_equal(len(doctree.document), 1)
        doctree_str = self.doctree2str(doctree)
        expected = (
            '<title>A section</title>\n'
            '<paragraph>Some text.</paragraph>\n'
            '<paragraph>More text.</paragraph>\n'
            '<paragraph>Text is endless.</paragraph>')
        assert_equal(doctree_str, expected)
        assert_true(isfile(pjoin(self.doctree_dir, 'index.doctree')))
        html = self.get_built_file('a_page.html')
        assert_true('Text is endless' in html)


def test_bad_pagebuilder():

    class TestBadPageBuilder(PageBuilder):

        @classmethod
        def set_page_source(cls):
            cls.page_source = HERE

    assert_raises(IOError, TestBadPageBuilder.setup_class)
