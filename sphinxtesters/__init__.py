""" Sphinxtesters package
"""

from .sphinxutils import (SourcesBuilder, ModifiedPageBuilder, TempApp)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
