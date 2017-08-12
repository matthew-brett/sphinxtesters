""" Tests for SourcesBuilder utility
"""

from os.path import (join as pjoin, dirname, isdir, exists)

from sphinxtesters import SourcesBuilder

from nose.tools import assert_true, assert_equal

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


class CheckSources(SourcesBuilder):
    """ Template for testing some pages
    """

    def test_structure(self):
        assert_true(isdir(self.out_dir))
        assert_true(isdir(self.doctree_dir))
        assert_true(exists(pjoin(self.doctree_dir, 'contents.doctree')))
        for page_name in self.rst_sources:
            assert_true(exists(pjoin(self.doctree_dir,
                                     page_name + '.doctree')))

    def check_page(self, page_name, expected_doctree):
        doctree = self.get_doctree(page_name)
        assert_equal(len(doctree.document), 1)
        doctree_str = self.doctree2str(doctree)
        assert_equal(doctree_str, expected_doctree)


class TestAPage(CheckSources):

    rst_sources = dict(a_page=A_PAGE)

    def test_a_page(self):
        self.check_page('a_page', A_DOCTREE)


class TestBPage(CheckSources):

    rst_sources = dict(b_page=B_PAGE)

    def test_b_page(self):
        self.check_page('b_page', B_DOCTREE)
