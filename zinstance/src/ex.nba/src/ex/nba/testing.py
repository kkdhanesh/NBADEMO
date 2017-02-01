# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import ex.nba


class ExNbaLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=ex.nba)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ex.nba:default')


EX_NBA_FIXTURE = ExNbaLayer()


EX_NBA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EX_NBA_FIXTURE,),
    name='ExNbaLayer:IntegrationTesting'
)


EX_NBA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EX_NBA_FIXTURE,),
    name='ExNbaLayer:FunctionalTesting'
)


EX_NBA_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        EX_NBA_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='ExNbaLayer:AcceptanceTesting'
)
