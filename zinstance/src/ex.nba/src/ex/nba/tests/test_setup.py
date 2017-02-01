# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from ex.nba.testing import EX_NBA_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that ex.nba is properly installed."""

    layer = EX_NBA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ex.nba is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('ex.nba'))

    def test_browserlayer(self):
        """Test that IExNbaLayer is registered."""
        from ex.nba.interfaces import IExNbaLayer
        from plone.browserlayer import utils
        self.assertIn(IExNbaLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = EX_NBA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['ex.nba'])

    def test_product_uninstalled(self):
        """Test if ex.nba is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled('ex.nba'))

    def test_browserlayer_removed(self):
        """Test that IExNbaLayer is removed."""
        from ex.nba.interfaces import IExNbaLayer
        from plone.browserlayer import utils
        self.assertNotIn(IExNbaLayer, utils.registered_layers())
