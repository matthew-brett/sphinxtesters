""" Test PageBuilder
"""

from os.path import (dirname, join as pjoin, isdir, isfile)

from sphinx.errors import ConfigError

from sphinxtesters.sphinxutils import PageBuilder

import pytest

HERE = dirname(__file__)
PROJ1 = pjoin(HERE, 'proj1')

class TestPageBuilder(PageBuilder):
    # Test a minmal source tree

    @classmethod
    def modify_source(cls):
        # Make an empty conf.py and contents.rst file with text
        cls.append_conf('')
        with open(pjoin(cls.page_source, 'contents.rst'), 'wt') as fobj:
            fobj.write('some text')

    def test_build(self):
        assert isdir(self.out_dir)
        assert isdir(self.doctree_dir)
        assert isfile(pjoin(self.out_dir, 'contents.html'))
        doctree = self.get_doctree('contents')
        assert doctree.document.astext() == 'some text'


class TestMaster(PageBuilder):
    # Test we can change the master document

    @classmethod
    def modify_source(cls):
        cls.append_conf('master_doc = "foo"')
        with open(pjoin(cls.page_source, 'foo.rst'), 'wt') as fobj:
            fobj.write('more text')

    def test_build(self):
        assert not isfile(pjoin(self.out_dir, 'contents.html'))
        assert isfile(pjoin(self.out_dir, 'foo.html'))
        doctree = self.get_doctree('foo')
        assert doctree.document.astext() == 'more text'


class TestTemplatePageBuilder(PageBuilder):

    page_source_template = PROJ1

    def test_build(self):
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


class TestRewrite(TestTemplatePageBuilder):
    # Replace page, check we get replacement page

    _page = u"""
Fancy title
+++++++++++

Compelling text
"""

    @classmethod
    def modify_source(cls):
        fname = pjoin(cls.page_source, 'a_page.rst')
        with open(fname, 'wt') as fobj:
            fobj.write(cls._page)

    def test_build(self):
        doctree = self.get_doctree('a_page')
        doctree_str = self.doctree2str(doctree)
        expected = (
            '<title>Fancy title</title>\n'
            '<paragraph>Compelling text</paragraph>')
        assert doctree_str == expected


def test_bad_pagebuilder_with_template():
    """ Tests that warning on build generates error
    """

    class TestBadPageBuilder(TestRewrite):

        _page = u"""
Fancy title
+++++++++++

:ref:`not-a-target`
"""

    with pytest.raises(RuntimeError):
        TestBadPageBuilder.setup_class()


class TestAppendConf(TestRewrite):
    # Test append_conf method

    @classmethod
    def modify_source(cls):
        super(TestAppendConf, cls).modify_source()
        cls.append_conf('# Spurious comment')

    def test_append_conf(self):
        with open(pjoin(PROJ1, 'conf.py'), 'rt') as fobj:
            before_contents = fobj.read()
        with open(pjoin(self.page_source, 'conf.py'), 'rt') as fobj:
            after_contents = fobj.read()
        assert (after_contents == before_contents + '# Spurious comment')
