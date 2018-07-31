""" Utilities for running sphinx tasks in-process
"""

import sys
import os
from os.path import join as pjoin, isdir, split as psplit, isfile
import shutil
from contextlib import contextmanager
from copy import copy
from tempfile import mkdtemp
import pickle
import warnings

from docutils import nodes

from docutils.parsers.rst import directives, roles

from sphinx.application import Sphinx
from sphinx.domains.std import StandardDomain

fresh_roles = copy(roles._roles)
fresh_directives = copy(directives._directives)
fresh_visitor_dict = nodes.GenericNodeVisitor.__dict__.copy()
fresh_std_domain_init_labels = StandardDomain.initial_data['labels'].copy()

@contextmanager
def in_dir(path):
    """ Change into directory for duration of context
    """
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


def reset_class(cls, original_dict):
    for key in list(cls.__dict__):
        if key not in original_dict:
            delattr(cls, key)
        else:
            setattr(cls, key, original_dict[key])


class TestApp(Sphinx):

    def __init__(self, *args, **kwargs):
        self._set_cache()
        with self.own_namespace():
            super(TestApp, self).__init__(*args, **kwargs)

    def _set_cache(self):
        self._global_cache = dict(
            directives=copy(fresh_directives),
            roles=copy(fresh_roles),
            visitor_dict = copy(fresh_visitor_dict),
            std_domain_init_labels = copy(fresh_std_domain_init_labels))


    @contextmanager
    def own_namespace(self):
        """ Set docutils namespace for builds """
        cache = self._global_cache
        _directives = directives._directives
        _roles = roles._roles
        _visitor_dict = nodes.GenericNodeVisitor.__dict__.copy()
        _std_domain_init_labels = StandardDomain.initial_data['labels']
        directives._directives = cache['directives']
        roles._roles = cache['roles']
        reset_class(nodes.GenericNodeVisitor, cache['visitor_dict'])
        StandardDomain.initial_data['labels'] = cache['std_domain_init_labels']
        try:
            yield
        finally:
            # Reset docutils, Sphinx global state
            directives._directives = _directives
            roles._roles = _roles
            reset_class(nodes.GenericNodeVisitor, _visitor_dict)
            StandardDomain.initial_data['labels'] = _std_domain_init_labels

    def build(self, *args, **kwargs):
        with self.own_namespace():
            return super(TestApp, self).build(*args, **kwargs)


class TempApp(TestApp):
    """ An application pointing to its own temporary directory.

    The instance deletes its temporary directory when garbage collected.

    Parameters
    ----------
    rst_text : str
        String containing ReST to build.
    conf_text : str, optional
        Text for configuration ``conf.py`` file.
    buildername : str, optional
        Name of default builder.
    status : file-like object or None, optional
        File-like object to which to write build status messages, or None for
        no build status messages.
    warningiserror : {True, False}, optional
        If True, raise an error for warning during the Sphinx build.
    """

    def __init__(self, rst_text, conf_text='', buildername='html',
                 status=sys.stdout, warningiserror=True):
        self.tmp_dir = tmp_dir = mkdtemp()
        with open(pjoin(tmp_dir, 'conf.py'), 'wt') as fobj:
            fobj.write(conf_text)
        with open(pjoin(tmp_dir, 'contents.rst'), 'wt') as fobj:
            fobj.write(rst_text)
        self._set_cache()
        with self.own_namespace():
            TestApp.__init__(self,
                             tmp_dir,
                             tmp_dir,
                             tmp_dir,
                             tmp_dir,
                             buildername,
                             status=status,
                             warningiserror=warningiserror)

    def cleanup(self):
        if self.tmp_dir is None:
            return
        shutil.rmtree(self.tmp_dir)
        self.tmp_dir = None

    def __del__(self):
        # Sphinx application may or may not have a __del__ method.
        try:
            super(TempApp, self).__del__()
        except AttributeError:
            pass
        self.cleanup()


class PageBuilder(object):
    """ Test class to build sphinx pages in temporary directory

    When child class has a name Pytest recognizes as a test class, Pytest will
    call :meth:`setup_class`.  In this class method, :meth:`set_page_source`
    copies / makes / manipulates the source pages.  It likely calls
    :meth:`modify_source` at the end, allowing you to hook in any other
    modifications.  :meth:`setup_class` then initializes the Sphinx applicaton
    object, and builds the pages, using :meth:`build_source`.

    The default behavior is to initialize the source directory by copying from
    a template directory specified in ``page_source_template``.  This can be
    None, to start with an empty source directory, before modifications by
    :meth:`modify_source`.
    """

    # If True, assert that the build raised an error
    should_error = False

    # Builder
    builder = 'html'

    # Set to path containing any original sources that we copy to initialize
    # the source directory.  Can be None (no pages copied).
    page_source_template = None

    @classmethod
    def setup_class(cls):
        cls.build_error = None
        cls.build_path = mkdtemp()
        try:  # Catch exceptions during test setup
            # Sets page_source, maybe modifies source
            cls.set_page_source()
            cls.out_dir = pjoin(cls.build_path, cls.builder)
            cls.doctree_dir = pjoin(cls.build_path, 'doctrees')
            # App to build the pages with warnings turned into errors
            cls.build_app = TestApp(
                cls.page_source,
                cls.page_source,
                cls.out_dir,
                cls.doctree_dir,
                cls.builder,
                warningiserror=True)
        except Exception as e:  # Exceptions during test setup
            shutil.rmtree(cls.build_path)
            raise e
        cls.build_source()

    @classmethod
    def set_page_source(cls):
        """ Set directory containing page sources, maybe modify source.
        """
        cls.page_source = pjoin(cls.build_path, 'source')
        if cls.page_source_template:
            shutil.copytree(cls.page_source_template, cls.page_source)
        else:
            os.mkdir(cls.page_source)
        cls.modify_source()

    @classmethod
    def modify_source(cls):
        """ Override to modify sources before initial build
        """

    @classmethod
    def build_source(cls):
        try:  # Catch exceptions during sphinx build
            cls.build_app.build(False, [])
            if cls.build_app.statuscode != 0:
                cls.build_error = "Unknown error"
        except Exception as e:  # Exceptions during sphinx build
            cls.build_error = e
        # We will later check if a page build that should error, did error
        if cls.build_error is None or cls.should_error:
            return
        # An unexpected error - delete temp dir and report.
        shutil.rmtree(cls.build_path)
        raise RuntimeError('page build failed with build error {}'
                           .format(cls.build_error))

    def get_doctree(self, name):
        """ Return doctree given by `name` from pickle in doctree file """
        with open(pjoin(self.doctree_dir, name + '.doctree'), 'rb') as fobj:
            content = fobj.read()
        return pickle.loads(content)

    @classmethod
    def get_built_file(cls, basename, encoding='utf8'):
        """ Contents of file in build dir with basename `basename`

        Parameters
        ----------
        basename : str
            Basename of file to load, including extension.
        encoding : str, optional
            If None, return contents as bytes.  If not None, decode contents
            with the given encoding.

        Returns
        -------
        content : str or bytes
            Return text contents of file if `encoding` not None, else return
            binary contents of file.
        """
        with open(pjoin(cls.out_dir, basename), 'rb') as fobj:
            content = fobj.read()
        return content if encoding is None else content.decode(encoding)

    def doctree2str(self, doctree):
        """ Return simple string representation from `doctree` """
        return '\n'.join(str(p) for p in doctree.document[0])

    def test_build_error(self):
        # Check whether an expected build error has occurred
        assert self.should_error == (self.build_error is not None)

    @classmethod
    def append_conf(cls, string):
        """ Append stuff to the conf.py file """
        with open(pjoin(cls.page_source, 'conf.py'), 'a') as fobj:
            fobj.write(string)

    @classmethod
    def teardown_class(cls):
        if isdir(cls.build_path):
            shutil.rmtree(cls.build_path)


class SourcesBuilder(PageBuilder):
    """ Build pages with text in class attribute ``rst_sources``.

    Class that stores page names, page contents as key, value pairs in the
    ``rst_sources`` class attribute.  ``conf.py`` contents can go in the
    ``conf_source`` class attribute.
    """

    # rst_sources is a dict with key, value pairs, where the keys are the page
    # names, with directory names separated by / regardless of platform we're
    # running on.  ``.rst`` extension assumed (do not add it).  The values are
    # strings giving the page contents.
    rst_sources = dict()

    # Contents for conf.py.  Can be empty to use existing contents.  If not
    # empty, then contents overwrites any existing conf.py file.
    conf_source = ''

    # Pages to be listed in the master document toctree
    toctree_pages = []

    @classmethod
    def _touch(cls, fname):
        if isfile(fname):
            return
        with open(fname, 'wt') as fobj:
            fobj.write('')

    @classmethod
    def modify_source(cls):
        conf_fname = pjoin(cls.page_source, 'conf.py')
        if cls.conf_source:
            with open(conf_fname, 'wt') as fobj:
                fobj.write(cls.conf_source)
        else:
            cls._touch(conf_fname)
        for page_root, page_content in cls.rst_sources.items():
            # page root may contain directories
            page_root = page_root.replace('/', os.path.sep)
            page_dir, page_base = psplit(page_root)
            page_dir = pjoin(cls.page_source, page_dir)
            if not isdir(page_dir):
                os.makedirs(page_dir)
            page_path = pjoin(page_dir, page_base + '.rst')
            with open(page_path, 'wt') as fobj:
                # Avoid warning (-> error) when page not included in toctree
                fobj.write(":orphan:\n\n")
                fobj.write(page_content)
        master_fname = cls._get_master()
        # Always write blank master document, if not already present.
        cls._touch(master_fname)
        # Write toctree to master doc, if needed
        cls.write_toctree(cls.toctree_pages, master_fname)

    @classmethod
    def get_conf_vars(cls, force=False):
        vars = {}
        with in_dir(cls.page_source):
            with open('conf.py', 'rt') as fobj:
                conf = fobj.read()
            exec(conf, {}, vars)
        return vars

    @classmethod
    def _get_master(cls):
        """ Return filename of master page for project """
        master_doc = cls.get_conf_vars().get('master_doc', 'contents')
        return pjoin(cls.page_source, master_doc + '.rst')

    @classmethod
    def write_toctree(cls, page_list, master_fname=None):
        """ Write toctree directive for given page list
        """
        if len(page_list) == 0:
            return
        if master_fname is None:
            master_fname = cls._get_master()
        with open(master_fname, 'at') as fobj:
            fobj.write("\n\n.. toctree::\n\n    {0}\n\n".format(
                '\n'.join(page_list)))


class ModifiedPageBuilder(PageBuilder):
    """ Add utilities for changing pages from template.

    This class now deprecated, please use PageBuilder instead.
    """

    # Default page.  Should specify a path-less page name that can be replaced
    # in modified builds.
    default_page = None

    @classmethod
    def setup_class(cls):
        warnings.warn('ModifedPageBuilder deprecated, please '
                      'use PageBuilder instead',
                      DeprecationWarning,
                      stacklevel=2)
        super(ModifiedPageBuilder, cls).setup_class()

    @classmethod
    def replace_page(cls, file_like):
        """ Replace default page with contents of `file_like`
        """
        out_fname = pjoin(cls.page_source, cls.default_page + '.rst')
        if hasattr(file_like, 'read'):
            contents = file_like.read()
            with open(out_fname, 'wt') as fobj:
                fobj.write(contents)
            return
        shutil.copyfile(file_like, out_fname)

    @classmethod
    def add_page(cls, file_like, out_name):
        """ Add another page from `file_like` with name `out_name`

        Parameters
        ----------
        file_like : file-like or str
            File-like object or filename.
        out_name : str
            Base of filename for output.  We will prepend the
            ``cls.page_source`` path, and add a ``.rst`` suffix.
        """
        out_fname = pjoin(cls.page_source, out_name + '.rst')
        if hasattr(file_like, 'read'):
            contents = file_like.read()
            with open(out_fname, 'wt') as fobj:
                fobj.write(contents)
        else:
            shutil.copyfile(file_like, out_fname)
        with open(pjoin(cls.page_source, 'index.rst'), 'a') as fobj:
            fobj.write("\n\n.. toctree::\n\n    {0}\n\n".format(out_name))
