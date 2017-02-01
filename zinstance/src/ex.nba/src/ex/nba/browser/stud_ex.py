from five import grok
from zope import schema

import sqlalchemy.types
import sqlalchemy.schema

from z3c.saconfig import Session

from zope.interface import Interface
from zope.interface import implements

from zope.site.hooks import getSite
from Products.CMFCore.interfaces import ISiteRoot

from Products.CMFCore.utils import getToolByName
from plone.memoize.view import memoize


#from ex.nba import MessageFactory as _
from ex.nba import _ as _
from ex.nba import ORMBase
from plone.directives import dexterity, form

from z3c.form import group, field, button
from zope.component import getUtility
import logging
from z3c.saconfig import Session
from Products.Five.browser import BrowserView

from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize

logger = logging.getLogger("alert form")




class IStud2(Interface):
    """ A stud2"""

    stud_id = schema.Int(
       title=_(u"Student Id"),required=True        
       )
    name = schema.TextLine(
        title=_(u"student name"),required=True
       )
    marks = schema.Int(
        title=_(u"marks"),required=True
       )

class Stud2(ORMBase):
    """ databased back stud2 """
    grok.implements(IStud2)
    __tablename__ = 'student'
    __table_args__ = {'extend_existing': True}

    stud_id = sqlalchemy.schema.Column(
        sqlalchemy.types.Integer(),
        primary_key = True,
        autoincrement=True,
        nullable=False,
       )
    name = sqlalchemy.schema.Column(
        sqlalchemy.types.String(4),
        nullable=False,
       )
    marks = sqlalchemy.schema.Column(
        sqlalchemy.types.Integer(),
        nullable=False,
       )

class IStud2details(Interface):
    student = schema.List(title=u'students', 
        value_type=DictRow(title=u'student', schema=IStud2),
        required=True)

                

class IAddStud2(Interface):
    """ A utility """
    def __call__(stud2):
        """ Add records """



class AddStud2(grok.GlobalUtility):
    """ A utility """
    implements(IAddStud2)
 
    def __call__(self, stud2):
        """ Add records """
        Session.add(stud2) 


class Irecord(Interface):
    """ A utility """
    def __call__(id1):
        """ search records """

class record(grok.GlobalUtility):
    """ A search utility """
    implements(Irecord)

    def __call__(self,id1):
        """ search records """
#        r=Session.query(Stud2).filter(Stud2.stud_id == 2)        
        r=Session.query(Stud2)  
        r1=[dict(id=row.stud_id,name=row.name,marks=row.marks) for row in r.all()]
        

        return r1



class EditStud2(form.EditForm):
    """ View class """
    grok.context(Interface)
    grok.name('edit-stud2')
#    grok.require('zope2.View')
#    grok.context(ISiteRoot)
#    grok.context(Interface)
 
#    schema = IStud2details
#    ignoreContext = True
     
    
    fields = field.Fields(IStud2details)
    fields['student'].widgetFactory = DataGridFieldFactory    
   
    def getContent(self):
        return {} 


#    id = None

#    session = Session()
#    session.add(stud)
##    @memoize
##    def getContent(self):
##        self.id = self.request.get('id', None)
##        if self.id:
##            return Session.query(stud).filter(stud.stud_id == self.id).one()

#    @button.buttonAndHandler(u'Submit')
#    def handleOk(self, action):
    @button.buttonAndHandler(u'Save', name='save')
    def handleSavve(self, action):    
        logger.info("hi")
        data, errors = self.extractData()
        logger.info(data)
        add_stud=getUtility(IAddStud2)
#        s=Stud2(stud_id=self.stud_id,
#                name=self.name,
#                marks=self.marks)

        for i in data['student']:           
            s=Stud2(stud_id=i['stud_id'],
                name=i['name'],
                marks=i['marks'])
            add_stud(s)


    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        #redirect user
        pass

#    def updateActions(self):
#        super(form.EditForm, self).updateActions()


class View(grok.View):
    """ report view """
    grok.context(ISiteRoot)            
    grok.require('zope2.View')
    grok.name('report')

    template=ViewPageTemplateFile('templates/stud2.pt')

    def render(self):
        return self.template()

    def __call__(self):
        return self.render()               


    @memoize
    def displayrecords(self):
        l=getUtility(Irecord)
        logger.info(l(1))
        return l(1)


