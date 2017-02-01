"""
    Demo of the widget
"""
from five import grok

from zope.interface import Interface
from zope.interface import implements
from zope import schema

from z3c.form import field, button
from z3c.form.interfaces import DISPLAY_MODE, HIDDEN_MODE

from plone.directives import form
from Products.CMFCore.interfaces import ISiteRoot

from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow

from ex.nba import ORMBase
import sqlalchemy.types
import sqlalchemy.schema

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize

from zope.component import getUtility
from z3c.saconfig import Session

import logging
logger = logging.getLogger("bio form")

class IPlant(Interface):
    plant_type = schema.TextLine(
        title = u'Plant Type', required=True)
    local_name = schema.TextLine(
        title = u'Local Name', required=True)
    scientific_name = schema.TextLine(
        title = u'Scientific Name', required=True)
    habit = schema.TextLine(
        title = u'Habit', required=True)
    habitat = schema.TextLine(
        title = u'Habitat', required=True)
    local_status = schema.Choice(
        title = u'Local Status', required=True,
         values=[u'Past', u'Present'])
    use1 = schema.TextLine(
        title = u'Commercial / Own use', required=True)
    part = schema.TextLine(
        title = u'Part Collected', required=True)
    tk = schema.TextLine(
        title=u'Associated TK', required=True)
    other = schema.TextLine(
        title=u'other', required=True)
    knowledge = schema.TextLine(
        title = u'community knowledge holder', required=True)

class Plant(ORMBase):
    """ databased back bio """
    grok.implements(IPlant)
    __tablename__ = 'bio'
    __table_args__ = {'extend_existing': True}
    plant_type = sqlalchemy.schema.Column(
        sqlalchemy.types.String(20)
        )
    local_name = sqlalchemy.schema.Column(
        sqlalchemy.types.String(20))
    scientific_name = sqlalchemy.schema.Column(
        sqlalchemy.types.String(20))
    habit = sqlalchemy.schema.Column(
        sqlalchemy.types.String(20))
    habitat = sqlalchemy.schema.Column(
        sqlalchemy.types.String(20))
    local_status = sqlalchemy.schema.Column(
        sqlalchemy.types.String(20))
    use1 = sqlalchemy. schema.Column(
        sqlalchemy.types.String(20))
    part = sqlalchemy.schema.Column(
        sqlalchemy.types.String(20))
    tk = sqlalchemy.schema.Column(
        sqlalchemy.types.Integer(),primary_key=True)
    other = sqlalchemy.schema.Column(
        sqlalchemy.types.String(20))
    knowledge = sqlalchemy.schema.Column(
        sqlalchemy.types.String(20))

class IAddPlant(Interface):
    """ a utility """
    def __call__(plant2):
        """ Add records """

class AddPlant(grok.GlobalUtility):
    """ A utility """
    implements(IAddPlant)

    def __call__(self, plant2):   
        """ Add records """
        Session.add(plant2)

class Irecord(Interface):
    """ A utility """
    def __call__(tk1):
        """ search records """

class record(grok.GlobalUtility):
    """ A search utility """
    implements(Irecord)

    def __call__(self,tk1):
        """ search records """
        r=Session.query(Plant)
        r1=[dict(plant_type=row.plant_type,local_name=row.local_name,scientific_name=row.scientific_name,habit=row.habit,habitat=row.habitat,local_status=row.local_status,use1=row.use1,part=row.part,tk=row.tk,other=row.other,knowledge=row.knowledge) for row in r.all()]
        return r1  



# Note: when using a dict, it is still an object - A schema.Dict would be
#       expected to contain some schemas. We are using an object implemented
#       as a dict

class IPlantdetails(Interface):
#    name = schema.TextLine(title=u'Name', required=True)
    plant = schema.List(title=u'Plants, shrubs ....',
        value_type=DictRow(title=u'plant', schema=IPlant),
        required=True)

TESTDATA = {
    'name': 'MY NAME',
    'plant': [
           {'plant_type': 'acacia',
            'local_name': 'curry leaf',
            'scientific_name': 'acacia indica',
            'habit': 'fertile land',
            'habitat': 'plains',
	    'local_status': 'Present',
            'use1': 'Commercial',
            'part': 'leaf',
            'tk': 'tk',
            'other': 'nil',
            'knowledge': 'no' 
		}
           ]}

class EditForm(form.EditForm):
    label = u'Simple Form'

    grok.context(Interface)
    grok.name('bio')
#    grok.require('ex.nba:mypermission')

    fields = field.Fields(IPlantdetails)
    fields['plant'].widgetFactory = DataGridFieldFactory

    def getContent(self):
        return {}

    @button.buttonAndHandler(u'Save', name='save')
    def handleSave(self, action):

        data, errors = self.extractData()
        add_plant=getUtility(IAddPlant)
        for i in data['plant']:
            p=Plant(plant_type=i['plant_type'],
                    local_name=i['local_name'],
                    scientific_name=i['scientific_name'],
                    habit=i['habit'],
                    habitat=i['habitat'],
                    local_status=i['local_status'],
                    use1=i['use1'],
                    tk=i['tk'],
                    other=['other'],
                    knowledge=['knowledge'])
            add_plant(p)          


        if errors:
            self.status = self.formErrorsMessage
            return
        
        
    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self,action):
        pass

class View(grok.View):
    """ report View """
    grok.context(ISiteRoot)
#    grok.require('ex.nba:mypermission')
    grok.name('bioreport')

    template=ViewPageTemplateFile('templates/bio.pt')

    def render(self):
        return self.template()

    def __call__(self):
        return self.render()

    @memoize
    def displayrecords(self):
        l=getUtility(Irecord)
        logger.info(l(1))
        return l(1)

