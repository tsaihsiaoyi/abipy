"""abipy is a set of tools for the analysis of ABINIT results."""

# -----------------------------------------------------------------------------
# Setup the top level names
# -----------------------------------------------------------------------------

from abipy.core import release

# Release data
__author__ = ""
for author, email in release.authors.values():
    __author__ += author + " <" + email + ">\n"
del author, email

__license__ = release.license
__version__ = release.version

import os
import sys

# Automatically set global mock environment variable if running tests via pytest
# and real API connectivity check is not explicitly requested.
is_testing = "pytest" in sys.modules or any("pytest" in arg for arg in sys.argv)
if is_testing and os.environ.get("ABIPY_REAL_API_TEST") is None:
    os.environ["ABIPY_MOCK_API"] = "true"

if os.environ.get("ABIPY_MOCK_API") == "true":
    import pymatgen.ext.cod
    from abipy.core.restapi import MockCOD
    pymatgen.ext.cod.COD = MockCOD

