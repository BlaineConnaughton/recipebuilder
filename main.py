import webapp2

import os
import urllib2
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
        template_values = {"host": self.request.host}
        template = JINJA_ENVIRONMENT.get_template('templates/homepage.html')
        self.response.write(template.render(template_values))

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

        #instantiate the payload
        payload_list = []

        #see what they selected for workflows
        workflows_chosen = self.request.get_all('industry')

        #Define the workflows, probably need a seperate function?

        ecomm_wf = open('./workflows/ecommerce.json', 'r').read()
        media_wf = open('./workflows/media.json', 'r').read()
        reporting_wf = open('./workflows/reporting.json', 'r').read()
        agency_wf = open('./workflows/agency.json', 'r').read()


        #for each workflow, add the right one to the payload
        for wf in workflows_chosen:
            if str(wf) == "Media":
                logging.info("A match! Media, from file")
                payload_list.append(media_wf)
            elif str(wf) == "Ecommerce":
                logging.info("A match! Ecommerce, from file")
                payload_list.append(ecomm_wf)
            elif str(wf) == "Reporting":
                logging.info("A match! Reporting, from file")
                payload_list.append(reporting_wf)
            elif str(wf) == "Agency":
                logging.info("A match! Agency, from file")
                payload_list.append(agency_wf)


        proplist = []
        Create_Properties(proplist)


        logging.info(payload_list)

        headers = {"content-type":"application/json"}

        for payload in payload_list:
            url = "https://api.hubapi.com/automation/v3/workflows?access_token=%s" % (token)
            r = urllib2.Request(url=url , data=payload , headers=headers)
            
            response = urllib2.urlopen(r)
            logging.info(response.read())
            response.close()

        self.response.write('heyo')
        
        
        


        


app = webapp2.WSGIApplication([
    ('/', MainHandler) , ('/auth', Authorize) , ('/load_industry', LoadIndustry)
], debug=True)