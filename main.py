import webapp2
import requests

import os
import urllib
import logging

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache

import json
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


def Create_Properties(propertyList):
        #Parse and create the properties in the portal, example propertylist is commented
        #ALSO, need a good way to get the portal ID in here as well

        #propertyList = []
        #propertyList.append(('last_email_clicked', "Last Email Clicked", "Last email someone clicked based on last email name", "emailinformation" ,  1))
        #propertyList.append(('last_email_opened', "Last Email Opened", "Last email someone opened based on last email name","emailinformation" ,  2))


        try:
            #Create a property for each property in fieldnames if they do not already
            for items in fieldnames:
                create_properties_data = """ {
                    "name": "%s",
                    "label": "%s",
                    "description": "%s",
                    "groupName": "%s",
                    "type": "string",
                    "fieldType": "text",
                    "formField": "false",
                    "displayOrder": "%s",
                    "options": [] 
                } """ % (items)

                logging.info(create_properties_data)
                headers = {'content-type': 'application/json'}
                url4 = 'https://api.hubapi.com/contacts/v2/properties?hapikey=%s&portalId=%s' % (HS_KEY, portal_id)
                logging.info(url4)
                req3 = urllib2.Request(url=url4, data=create_properties_data, headers=headers)
                logging.info(req3)
                response = urllib2.urlopen(req3)
                logging.info(response)
                response.close()
        except:
            pass
            #hopefully this means it already exists


class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/homepage.html')
        self.response.write(template.render())

class Authorize(webapp2.RequestHandler):
  #https://app.hubspot.com/auth/authenticate?client_id=32d1475b-20df-11e5-8bdb-532b010dd8d8&portalId=292568&redirect_uri=http://scribedynamics.appspot.com/auth&scope=contacts-rw+offline
    def get(self):
        access_token = self.request.get('access_token')
        refresh_token = self.request.get('refresh_token')
        expires_in = self.request.get('expires_in')

        if refresh_token != None:
            memcache.add('token', access_token, 3600)

        writeout = """
        <!DOCTYPE html>
            <html>
            <body>

            <form action="load_industry" method="post">
              <input type="checkbox" name="industry" value="Agency"> Agency (webinar/events)<br>
              <input type="checkbox" name="industry" value="Reporting"> Attribution<br>
              <input type="checkbox" name="industry" value="Media"> Media (subscriptions)<br>
              <input type="checkbox" name="industry" value="Ecommerce"> Ecommerce (transactional) <br>
              <input type="submit" value="Submit">
            </form>

            </body>
            </html>
        """

        self.response.write(writeout)


class LoadIndustry(webapp2.RequestHandler):
    def post(self):
        #workflow_id = self.request.get('mydropdown')
        #logging.info(workflow_id)
        token = memcache.get('token')
        logging.info(token)

        proplist = []
        Create_Properties(proplist)


        #Next create the workflows, probably need a seperate function?

        payload = """

name: "Update Email clicked EXAMPLE FROM APP",
actions: [
{
type: "COPY_PROPERTY",
sourceProperty: "hs_email_last_email_name",
targetProperty: "last_email_clicked",
targetModel: "CONTACT",
actionId: 2119607,
name: "Copy property",
stepListId: 1358,
stepId: 2110984
}
],
id: 1116257,
type: "DRIP_DELAY",
enabled: false,
portalId: 292568,
onlyExecOnBizDays: false,
nurtureTimeRange: {
enabled: false,
startHour: 9,
stopHour: 10
},
isSegmentBased: true,
listening: false,
internalStartingListId: 1357,
updatedAt: 1455718769218,
insertedAt: 1455716414584,
allowContactToTriggerMultipleTimes: true,
unenrollmentSetting: {
type: "NONE",
excludedWorkflows: [ ]
},
recurringSetting: {
type: "NONE"
},
originalAuthorUserId: 474212,
enrollOnCriteriaUpdate: false,
onlyEnrollsManually: false,
goalCriteriaEnabled: false,
segmentCriteria: [
[
{
withinTimeMode: "PAST",
filterFamily: "PropertyValue",
property: "hs_email_last_click_date",
type: "datetime",
operator: "IS_NOT_EMPTY"
}
]
],
goalCriteria: [ ],
reEnrollmentTriggerSets: [
[
{
name: "Last email click date",
id: "hs_email_last_click_date",
type: "CONTACT_PROPERTY_NAME"
}
]
],
triggerSets: [ ],
suppressionListIds: [ ],
lastUpdatedBy: "bconnaughton@hubspot.com",
metaData: {
triggeredByWorkflowIds: [ ],
succeededListId: 1348
}
}
        """

        headers = {"content-header":"application/json"}
        url = "https://api.hubapi.com/automation/v3/workflows?access_token=%s" % (token)
        r = requests.post(url=url , data=payload , headers=headers)


        self.response.write(r.content)


app = webapp2.WSGIApplication([
    ('/', MainHandler) , ('/auth', Authorize) , ('/load_industry', LoadIndustry)
], debug=True)