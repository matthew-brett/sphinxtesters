#######################################################
Sphinxtesters - utilities for testing Sphinx extensions
#######################################################

.. shared-text-body

**********
Quickstart
**********

If you have a directory containing a sphinx project, test that it builds with
something like:

.. code:: python

    class TestMyProject(SourcesBuilder):

        page_source_template = 'path/to/sphinx_dir'

        def test_basic_build(self):
            # Get doctree for page "a_page.rst"
            doctree = self.get_doctree('a_page')
            # Assert stuff about doctree version of page
            html = self.get_built_file('a_page.html')
            # Assert stuff about html version of page

You can try adding other page content by using the ``rst_sources`` dictionary:

.. code:: python

    class TestChangedProject(SourcesBuilder):

        page_source_template = 'path/to/sphinx_dir'
        rst_sources = {'a_page': """Replacement text for page""",
                       'b_page': """An entirely new page"""}

        def test_basic_build(self):
            a_doctree = self.get_doctree('a_page')
            b_doctree = self.get_doctree('b_page')
            # Your tests for the new page content here

Set the text of the ``conf.py`` file with the ``conf_source`` attribute:

.. code:: python

    class TestConfeddProject(SourcesBuilder):

        page_source_template = 'path/to/sphinx_dir'
        rst_sources = {'a_page': """Replacement text for page""",
                       'b_page': """An entirely new page"""}
        conf_source = """ # This overwrites existing conf.py """

        def test_basic_build(self):
            a_doctree = self.get_doctree('a_page')
            b_doctree = self.get_doctree('b_page')
            # Your tests for the new page content here

You don't need to set ``page_source_template``; if you don't, you start with a
fresh project, where the only pages are the ones you specify in
``rst_sources``.

.. code:: python

    class TestFreshProject(SourcesBuilder):

        rst_sources = {'a_page': """A new page""",
                       'b_page': """Another new page"""}
        conf_source = """ # Stuff for the conf.py file """

        def test_basic_build(self):
            a_doctree = self.get_doctree('a_page')
            b_doctree = self.get_doctree('b_page')
            # Your tests for the new page content here

See the tests for examples of using Sphinxtesters for testing builds of Sphinx
projects.

************
Installation
************

::

    pip install sphinxtesters

****
Code
****

See https://github.com/matthew-brett/sphinxtesters

Released under the BSD two-clause license - see the file ``LICENSE`` in the
source distribution.

`travis-ci <https://travis-ci.org/matthew-brett/sphinxtesters>`_ kindly tests the
code automatically under Python versions 2.7, and 3.3 through 3.6.

The latest released version is at https://pypi.python.org/pypi/sphinxtesters

*****
Tests
*****

* Install ``sphinxtesters``
* Install the pytest_ testing framework::

    pip install pytest

* Run the tests with::

    pytest sphinxtesters

*******
Support
*******

Please put up issues on the `sphinxtesters issue tracker`_.

.. standalone-references

.. |sphinxtesters-documentation| replace:: `sphinxtesters documentation`_
.. _sphinxtesters documentation:
    https://matthew-brett.github.com/sphinxtesters/sphinxtesters.html
.. _documentation: https://matthew-brett.github.com/sphinxtesters
.. _pandoc: http://pandoc.org
.. _jupyter: jupyter.org
.. _homebrew: brew.sh
.. _sphinx: http://sphinx-doc.org
.. _rest: http://docutils.sourceforge.net/rst.html
.. _sphinxtesters issue tracker: https://github.com/matthew-brett/sphinxtesters/issues
.. _pytest: https://pytest.org
.. _mock: https://github.com/testing-cabal/mock
