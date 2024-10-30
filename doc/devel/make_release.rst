#######################
Releasing sphinxtesters
#######################

* Review the open list of `sphinxtesters issues`_.  Check whether there are
  outstanding issues that can be closed, and whether there are any issues that
  should delay the release.  Label them.

* Review and update the release notes.  Review and update the :file:`Changelog`
  file.  Get a partial list of contributors with something like::

      git log 0.2.0.. | grep '^Author' | cut -d' ' -f 2- | sort | uniq

  where ``0.2.0`` was the last release tag name.

  Then manually go over ``git shortlog 0.2.0..`` to make sure the release notes
  are as complete as possible and that every contributor was recognized.

* Use the opportunity to update the ``.mailmap`` file if there are any
  duplicate authors listed from ``git shortlog -ns``.

* Check the copyright years in ``doc/conf.py`` and ``LICENSE``;

* Check the output of::

    rst2html.py README.rst > ~/tmp/readme.html

  because this will be the output used by PyPi_

* Check Github Actions are passing.

* Update the version in ``sphinxtesters/__init__.py`` to release version.  Add
  and commit.

* Clean::

    # Check no files outside version control that you want to keep
    git status
    # Nuke
    git clean -fxd

* When ready::

    pip install twine build
    python -m build --sdist
    twine upload dist/sphinxtesters*tar.gz

* Upload the release commit and tag to github::

    git push
    git push --tags

* Once everything looks good, tag the release::

    git tag -s 0.2.4

* Update the version in ``sphinxtesters/__init__.py`` to reflect this is a
  development version.  Add and commit.

* Push current branch and tags::

    git push
    git push --tags

.. include:: ../links_names.inc
