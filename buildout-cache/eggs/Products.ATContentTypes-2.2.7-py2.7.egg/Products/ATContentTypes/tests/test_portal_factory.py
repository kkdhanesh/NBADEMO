from AccessControl import Permissions
from AccessControl import getSecurityManager
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone.tests import PloneTestCase
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
import urlparse



def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)

ADD_DOC_PERM = 'ATContentTypes: Add Document'


class TestPortalFactory(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.addMember('member', 'secret', ['Member'], [])
        self.membership.addMember('manager', 'secret', ['Manager'], [])

    def testTraverse(self):
        temp_doc = self.folder.restrictedTraverse(
                        'portal_factory/Document/tmp_id')
        self.assertEqual(temp_doc.portal_type, 'Document')
        self.assertEqual(temp_doc.getId(), 'tmp_id')

    def testTraverseEditView(self):
        edit_view = self.folder.restrictedTraverse(
                        'portal_factory/Document/tmp_id/edit')
        self.assertEqual('tmp_id', edit_view.im_self.getId())
        self.assertEqual('Document', edit_view.im_self.portal_type)

    def testTraverseTwiceByDifferentContentTypes(self):
        temp_doc = self.folder.restrictedTraverse(
                        'portal_factory/Document/tmp_id')
        self.assertEqual(temp_doc.portal_type, 'Document')
        self.assertEqual(temp_doc.getId(), 'tmp_id')
        temp_img = self.folder.restrictedTraverse(
                        'portal_factory/Image/tmp_id_image')
        self.assertEqual(temp_img.portal_type, 'Image')
        self.assertEqual(temp_img.getId(), 'tmp_id_image')

    def testTempFolderLocalRoles(self):
        # Temporary objects should "inherit" local roles from container
        member = self.membership.getMemberById('member')
        self.portal.acl_users.addRole('Foo')

        self.folder.manage_addLocalRoles('member', ('Foo',))
        self.folder.invokeFactory('Folder', id='folder2')
        self.folder.folder2.manage_addLocalRoles('member', ('Reviewer',))

        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Foo', 'Member'))

        temp_object = self.folder.restrictedTraverse(
                        'portal_factory/Document/tmp_id')
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object)),
                         ('Authenticated', 'Foo', 'Member'))

        temp_object2 = self.folder.folder2.restrictedTraverse(
                        'portal_factory/Document/tmp_id')
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object2)),
                         ('Authenticated', 'Foo', 'Member', 'Reviewer'))

    def testTempFolderLocalRolesWithBlocking(self):
        # Temporary objects should "inherit" local roles from container,
        # but also need to respect PLIP 16 local role blocking
        member = self.membership.getMemberById('member')
        self.portal.acl_users.addRole('Foo')

        self.folder.manage_addLocalRoles('member', ('Foo',))
        self.folder.invokeFactory('Folder', id='folder2')
        self.folder.folder2.manage_addLocalRoles('member', ('Reviewer',))
        # make folder2 not inherit local roles
        self.portal.plone_utils.acquireLocalRoles(self.folder.folder2,
                                                  status=0)

        self.assertEqual(
                sortTuple(member.getRolesInContext(self.folder.folder2)),
                ('Authenticated', 'Member', 'Reviewer'))

        temp_object2 = self.folder.folder2.restrictedTraverse(
                        'portal_factory/Document/tmp_id')
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object2)),
                         ('Authenticated', 'Member', 'Reviewer'))

    def testTempObjectLocalRolesBug(self):
        # Evil monkey patch should not change all objects of a class
        self.createMemberarea('member')
        member = self.membership.getMemberById('member')
        # Make an unrelated non-temporary object for comparison
        self.login('manager')
        # BBB: we you launch this test suite with the others you need to reset
        # global_allow to True
        self.portal.portal_types.Document.manage_changeProperties(global_allow=1)
        self.portal.invokeFactory('Document', id='nontmp_id')
        nontemp_object = getattr(self.portal, 'nontmp_id')

        # Assume identify of the ordinary member
        self.login('member')
        folder = self.membership.getHomeFolder()
        temp_object = \
                folder.restrictedTraverse('portal_factory/Document/tmp_id')

        # Make sure member is owner of temporary object
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object)),
                         ('Authenticated', 'Member', 'Owner'))
        self.assertEqual(temp_object.Creator(), 'member')

        # Make sure member is not owner of non-temporary object
        # (i.e. make sure our evil monkey patch of the temporary instance has
        # not resulted in our patching all instances of the class)
        self.assertEqual(sortTuple(member.getRolesInContext(nontemp_object)),
                         ('Authenticated', 'Member'))

    def testTempFolderPermissions(self):
        # TempFolder should "inherit" permission mappings from container
        previous_roles = \
                [r for r in self.folder.rolesOfPermission(AddPortalContent)
                    if r['name'] == 'Anonymous']
        self.folder.manage_permission(AddPortalContent, ['Anonymous'], 1)
        new_roles = [r for r in self.folder.rolesOfPermission(AddPortalContent)
                        if r['name'] == 'Anonymous']
        self.assertNotEqual(previous_roles, new_roles)

        temp_folder = self.folder.restrictedTraverse(
                                'portal_factory/Document/tmp_id').aq_parent
        temp_roles = \
                [r for r in temp_folder.rolesOfPermission(AddPortalContent)
                    if r['name'] == 'Anonymous']

        self.assertEqual(temp_roles, new_roles)


class TestCreateObject(PloneTestCase.PloneTestCase):

    def testCreateObjectByDoCreate(self):
        # doCreate should create the real object
        temp_object = \
            self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        foo = temp_object.portal_factory.doCreate(temp_object, 'foo')
        self.assertTrue('foo' in self.folder)
        self.assertEqual(foo.get_local_roles_for_userid(TEST_USER_ID),
                         ('Owner',))

    def testUnauthorizedToCreateObjectByDoCreate(self):
        # Anonymous should not be able to create the (real) object
        # Note that Anonymous used to be able to create the temp object...
        temp_object = \
            self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.logout()
        self.assertRaises(ValueError, temp_object.portal_factory.doCreate,
                          temp_object, 'foo')

    def testCopyPermission(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Folder', id='folder_to_copy')

        pm = self.portal.portal_membership
        pm.addMember('editor', 'secret', ['Editor'], [])
        self.login('editor')
        member = pm.getMemberById('editor')
        self.assertTrue(member.checkPermission(Permissions.copy_or_move,
                                               self.portal))
        security = getSecurityManager()
        self.assertTrue(security.validate(
            self.portal, self.portal, 'manage_copyObjects'))

    def testRenamePermission(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Folder', id='folder_to_copy')

        pm = self.portal.portal_membership
        pm.addMember('editor', 'secret', ['Editor'], [])
        self.login('editor')
        member = pm.getMemberById('editor')
        self.assertTrue(member.checkPermission(ModifyPortalContent,
                                               self.portal))
        security = getSecurityManager()
        self.assertTrue(security.validate(
            self.portal, self.portal, 'manage_renameObjects'))


class TestCreateObjectByURL(PloneTestCase.FunctionalTestCase):
    '''Weeee, functional tests'''

    def afterSetUp(self):
        self.folder_url = self.folder.absolute_url()
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.basic_auth = '%s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD)
        # We want 401 responses, not redirects to a login page
        plugins = self.portal.acl_users.plugins
        try:
            plugins.deactivatePlugin(IChallengePlugin,
                                     'credentials_cookie_auth')
        except KeyError:
            pass

        # Enable portal_factory for Document type
        self.factory = self.portal.portal_factory
        self.factory.manage_setPortalFactoryTypes(listOfTypeIds=['Document'])

    def testCreateObject(self):
        # createObject script should make a temp object
        response = self.publish(self.folder_path +
                                '/createObject?type_name=Document',
                                self.basic_auth)

        # Redirect to document edit form
        self.assertEqual(response.getStatus(), 302)

        # The redirect URL should contain the factory parts
        location = response.getHeader('Location')
        self.assertTrue(location.startswith(
                                self.folder_url + '/portal_factory/Document/'))
        # CMFFormController redirects should not do alias translation
        self.assertTrue('/edit' in location)

        # Perform the redirect
        edit_form_path = location[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(edit_form_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200)  # OK

    def testCreateNonGloballyAllowedObject(self):
        # TempFolder allows to create all portal types
        self.portal.portal_types.Document.manage_changeProperties(
                                                        global_allow=0)
        response = self.publish(self.folder_path +
                                '/createObject?type_name=Document',
                                self.basic_auth)

        # Redirect to document edit form
        self.assertEqual(response.getStatus(), 302)

        # The redirect URL should contain the factory parts
        location = response.getHeader('Location')
        self.assertTrue(location.startswith(
                                self.folder_url + '/portal_factory/Document/'))
        self.assertTrue('/edit' in location)

        # Perform the redirect
        edit_form_path = location[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(edit_form_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200)  # OK

    def testUnauthorizedToViewEditForm(self):
        # Anonymous should not be able to see document edit form
        response = self.publish(self.folder_path +
                                '/createObject?type_name=Document',
                                )  # No basic out info
        # We got redirected to the factory
        self.assertEqual(response.getStatus(), 302)
        newpath = response.getHeader('location')
        proto, host, path, query, fragment = urlparse.urlsplit(newpath)
        # Let's follow it
        response = self.publish(path)
        # And we are forbidden
        self.assertEqual(response.getStatus(), 401)  # Unauthorized

    def testUnauthorizedToViewEditFormOfNonFactoryObject(self):
        # Anonymous should not be able to see newsitem_edit_form
        response = self.publish(self.folder_path +
                                '/createObject?type_name=News%20Item',
                                )  # No basic out info

        self.assertEqual(response.getStatus(), 401)  # Unauthorized


class TestPortalFactoryTraverseByURL(PloneTestCase.FunctionalTestCase):
    '''Weeee, functional tests'''

    def afterSetUp(self):
        self.folder_url = self.folder.absolute_url()
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.basic_auth = '%s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD)
        # We want 401 responses, not redirects to a login page
        plugins = self.portal.acl_users.plugins
        try:
            plugins.deactivatePlugin(IChallengePlugin,
                                     'credentials_cookie_auth')
        except KeyError:
            pass

        # Enable portal_factory for Document type
        self.factory = self.portal.portal_factory
        self.factory.manage_setPortalFactoryTypes(listOfTypeIds=['Document'])

        # setup a temp object
        response = self.publish(self.folder_path +
                                '/createObject?type_name=Document',
                                self.basic_auth
                                )
        # We got redirected to the factory
        self.assertEqual(response.getStatus(), 302)
        newpath = response.getHeader('location')
        proto, host, path, query, fragment = urlparse.urlsplit(newpath)

        self.tmp_obj_path = path.replace('/edit', '')

    def testFSImage(self):
        path = "%s/logo.png" % self.tmp_obj_path
        data = self.publish(path)
        self.assertEqual(data.getHeader('Content-Type'), 'image/png')

    def testBrowserResource(self):
        path = "%s/++resource++plone-logo.png" % self.tmp_obj_path
        data = self.publish(path)
        self.assertEqual(data.getHeader('Content-Type'), 'image/png')
