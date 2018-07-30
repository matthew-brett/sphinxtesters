""" Tests for SourcesBuilder utility
"""

from os.path import (join as pjoin, isdir, exists)

from sphinxtesters import SourcesBuilder

A_PAGE = """\
#########
A section
#########

Some text.

More text.

Text is endless."""

A_DOCTREE = """\
<title>A section</title>
<paragraph>Some text.</paragraph>
<paragraph>More text.</paragraph>
<paragraph>Text is endless.</paragraph>"""

B_PAGE = """\
###############
Another section
###############

Some more text."""

B_DOCTREE = """\
<title>Another section</title>
<paragraph>Some more text.</paragraph>"""

NO_TITLE_PAGE = """\
Just text, no title."""

NO_TITLE_DOCTREE = """\
Just text, no title."""


class CheckSources(SourcesBuilder):
    """ Template for testing some pages
    """

    def test_structure(self):
        assert isdir(self.out_dir)
        assert isdir(self.doctree_dir)
        assert exists(pjoin(self.doctree_dir, 'contents.doctree'))
        for page_name in self.rst_sources:
            assert exists(pjoin(self.doctree_dir,
                                page_name + '.doctree'))

    def check_page(self, page_name, expected_doctree):
        doctree = self.get_doctree(page_name)
        assert len(doctree.document) == 1
        doctree_str = self.doctree2str(doctree)
        assert doctree_str == expected_doctree


class TestAPage(CheckSources):

    rst_sources = dict(a_page=A_PAGE)
    expected_doctree = A_DOCTREE

    def test_page(self):
        page_name = list(self.rst_sources)[0]
        self.check_page(page_name, self.expected_doctree)


class TestBPage(TestAPage):

    rst_sources = dict(b_page=B_PAGE)
    expected_doctree = B_DOCTREE


class TestNoTitlePage(TestAPage):

    rst_sources = dict(no_title_page=NO_TITLE_PAGE)
    expected_doctree = NO_TITLE_DOCTREE
