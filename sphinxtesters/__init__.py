""" Sphinxtesters package
"""

from .sphinxutils import (PageBuilder, SourcesBuilder, ModifiedPageBuilder,
                          TempApp)

from . import _version
__version__ = _version.get_versions()['version']
