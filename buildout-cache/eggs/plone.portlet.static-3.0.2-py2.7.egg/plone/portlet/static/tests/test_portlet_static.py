# -*- coding: utf-8 -*-
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.portlet.static import static
from plone.portlet.static.testing import PLONEPORTLETSTATIC_INTEGRATION_TESTING
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from zope.component import getUtility, getMultiAdapter
import unittest2 as unittest


class TestPortlet(unittest.TestCase):

    layer = PLONEPORTLETSTATIC_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='plone.portlet.static.Static')
        self.assertEquals(portlet.addview, 'plone.portlet.static.Static')

    def testInterfaces(self):
        portlet = static.Assignment(header=u"title", text="text")
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='plone.portlet.static.Static')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn'
        )
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(
            data={'header': u"test title", 'text': u"test text"}
        )

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], static.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.portal.REQUEST

        mapping['foo'] = static.Assignment(header=u"title", text="text")
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, static.EditForm))

    def testRenderer(self):
        context = self.portal
        request = self.portal.REQUEST
        view = self.portal.restrictedTraverse('@@plone')
        manager = getUtility(
            IPortletManager,
            name='plone.rightcolumn',
            context=self.portal
        )
        assignment = static.Assignment(header=u"title", text="text")

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment),
            IPortletRenderer
        )
        self.failUnless(isinstance(renderer, static.Renderer))

        self.failUnless(renderer.available,
                        "Renderer should be available by default.")


class TestRenderer(unittest.TestCase):

    layer = PLONEPORTLETSTATIC_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.portal
        request = request or self.portal.REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager,
            name='plone.rightcolumn',
            context=self.portal
        )
        assignment = assignment or static.Assignment(
            header=u"title",
            text="text"
        )
        ren = getMultiAdapter(
            (context, request, view, manager, assignment),
            IPortletRenderer
        )
        ren.__portlet_metadata__ = {
            'key': '/'.join(self.portal.getPhysicalPath())
        }
        return ren

    def test_render(self):
        r = self.renderer(
            context=self.portal,
            assignment=static.Assignment(
                header=u"title",
                text="<b>text</b>"
            )
        )
        r = r.__of__(self.portal)
        r.update()
        output = r.render()
        self.failUnless('title' in output)
        self.failUnless('<b>text</b>' in output)

    def test_no_header(self):
        r = self.renderer(
            context=self.portal,
            assignment=static.Assignment(text="<b>text</b>")
        )
        r = r.__of__(self.portal)
        r.update()
        output = r.render()
        self.assertTrue('<a class="tile"' not in output)
        self.assertTrue('<header class="portletHeader titleless"' in output)

    def test_hide(self):
        self.assertRaises(TypeError, static.Assignment, hide=True)

    def test_css_class(self):
        r = self.renderer(
            context=self.portal,
            assignment=static.Assignment(
                header=u"Welcome text",
                text="<b>text</b>"
            )
        )
        self.assertEquals('portlet-static-welcome-text', r.css_class())

    def test_relative_link(self):
        r = self.renderer(
            context=self.portal,
            assignment=static.Assignment(
                text="""<a href="relative/link">link</a>"""
            )
        )
        r = r.__of__(self.portal)
        r.__portlet_metadata__ = dict(
            category='context', key='/'.join(self.portal.getPhysicalPath()))
        r.update()
        output = r.render()
        self.assertTrue("http://nohost/plone/relative/link" in output)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite