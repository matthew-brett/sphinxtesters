""" Test PageBuilder
"""

from os.path import (dirname, join as pjoin, isdir, isfile)

from sphinx.errors import ConfigError

from sphinxtesters.sphinxutils import PageBuilder

import pytest

HERE = dirname(__file__)
PROJ1 = pjoin(HERE, 'proj1')


class TestPageBuilder(PageBuilder):

    @classmethod
    def set_page_source(cls):
        cls.page_source = PROJ1

    def test_basic_build(self):
        assert isdir(self.out_dir)
        assert isdir(self.doctree_dir)
        doctree = self.get_doctree('a_page')
        assert len(doctree.document) == 1
        doctree_str = self.doctree2str(doctree)
        expected = (
            '<title>A section</title>\n'
            '<paragraph>Some text.</paragraph>\n'
            '<paragraph>More text.</paragraph>\n'
            '<paragraph>Text is endless.</paragraph>')
        assert doctree_str == expected
        assert isfile(pjoin(self.doctree_dir, 'index.doctree'))
        html = self.get_built_file('a_page.html')
        assert 'Text is endless' in html


def test_bad_pagebuilder():

    class TestBadPageBuilder(PageBuilder):

        @classmethod
        def set_page_source(cls):
            cls.page_source = HERE

    # ConfigError as of Sphinx 1.6.6
    with pytest.raises((IOError, ConfigError)):
        TestBadPageBuilder.setup_class()
