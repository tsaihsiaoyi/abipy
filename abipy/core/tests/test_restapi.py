"""Tests for core.restapi module"""

import contextlib
import os
from unittest.mock import patch

import pytest

import abipy.data as abidata
from abipy import abilab
from abipy.core.testing import AbipyTest
from abipy.core.structure import Structure
from abipy.core.restapi import get_mprester


class TestMpRestApi(AbipyTest):
    """Test interfaces with the Materials Project REST API."""

    @pytest.mark.skipif(
        os.environ.get("ABIPY_REAL_API_TEST") is not None,
        reason="Interface with real MP Rester is broken / requires API key"
    )
    def is_test_mprester(self):
        """Testing MP Rest API wrappers."""
        # Test mp_search
        mp = abilab.mp_search("MgB2")
        repr(mp)
        str(mp)
        assert mp.structures
        assert "mp-763" in mp.ids
        assert len(mp.structures) == len(mp.data)
        assert hasattr(mp.dataframe, "describe")
        mp.print_results(fmt="abivars", verbose=2)
        new = mp.add_entry(mp.structures[-1], "newid")
        assert len(new.ids) == len(mp.ids) + 1
        assert new.ids == mp.ids + ["newid"]

        with contextlib.redirect_stdout(None):
            new.print_results(fmt="cif", verbose=2)

        # Test mp_match_structure
        mp = abilab.mp_match_structure(abidata.cif_file("al.cif"))
        repr(mp)
        str(mp)
        assert mp.structures and mp
        assert "mp-134" in mp.ids
        assert mp.data is None and mp.dataframe is None
        mp.print_results(fmt="abivars", verbose=2)

        if self.has_nbformat():
            mp.write_notebook(nbpath=self.get_tmpname(text=True))

    def test_cod(self):
        """Testing COD interface."""
        self.skip_if_not_executable("mysql")
        # Test abilab.cod_search
        cod = abilab.cod_search("MgB2", primitive=True)
        repr(cod)
        str(cod)
        assert cod.structures and cod
        assert 1000026 in cod.ids
        assert cod.data is not None
        assert hasattr(cod.dataframe, "describe")

        with contextlib.redirect_stdout(None):
            cod.print_results(fmt="POSCAR", verbose=2)

    def test_mp_connectivity(self):
        """Check real connectivity to Materials Project API."""
        if os.environ.get("ABIPY_REAL_API_TEST") is None:
            pytest.skip("Only run in real API connectivity check")

        api_key = os.environ.get("PMG_MAPI_KEY")
        if not api_key:
            pytest.skip("PMG_MAPI_KEY env var not set")

        with get_mprester() as rest:
            struct = rest.get_structure_by_material_id("mp-149")
            assert struct is not None

