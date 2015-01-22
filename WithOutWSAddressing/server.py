"""
   Implementation of the  web services
"""

import requests
from suds.client import Client
from soaplib.service import DefinitionBase
from soaplib.service import rpc
from soaplib.serializers.primitive import String, Integer
from soaplib.serializers.clazz import Array,ClassSerializer
from soaplib.wsgi import Application
from lxml import etree
import xml.etree.ElementTree as ET
from sqlite3 import dbapi2 as sqlite
from flask import Flask
import json
import xmlrpclib


news_database = {}
topicid_seq = 1
#app = Flask(__name__)

class Topic(ClassSerializer):
        __namespace__ = "ns1"
        tid =Integer
        sectionid = String
        webtitle = String

class NameToken(ClassSerializer):
        __namespace__ = "fts"
        Username = String
        Password = String

"""
   Class to deserialize the WS-Security Headers
"""
class WSSecurityHeader(ClassSerializer):
	__namespace__ = "tns"
	
	UsernameToken = NameToken
	


class WeatherService(DefinitionBase):


    """
       Gives the weather details of the given city in a given country
       Depends on public web service GetWeather of http://www.webservicex.net
    """
    @rpc(String,String,_returns=String)
    def weather(self,city,country):

        
        hello_client = Client('http://www.webservicex.net/globalweather.asmx?WSDL')
        result = hello_client.service.GetWeather(city,country)

        result = result.encode("utf-16")
        tree=etree.fromstring(result)
        r = tree.xpath('/CurrentWeather')
        root = tree.xpath('/CurrentWeather/Location')
        time = tree.xpath('/CurrentWeather/Time')
        Wind = tree.xpath('/CurrentWeather/Wind')
        visibility = tree.xpath('/CurrentWeather/Visibiltiy')
        Sky = tree.xpath('/CurrentWeather/SkyConditions')
        Temp = tree.xpath('/CurrentWeather/Temperature')
        Dew = tree.xpath('CurrentWeather/DewPoint')
        Humidity = tree.xpath('/CurrentWeather/RelativeHumidity')
        pressure = tree.xpath('/CurrentWeather/Pressure')
        ls = "Location=" + root[0].text + ", Time =" + time[0].text +  ", Temp=" +Temp[0].text + ", Humidity= " + Humidity[0].text

        html = "<ul>"
        for a in range(len(r)):

               html+="<li>"+"Location :" + root[a].text + "</li><li> Time : " + time[a].text +  "</li><li> Temp : " +Temp[a].text + "</li><li> Humidity : " + Humidity[a].text+"</li>"

               """                
               a1="<li>"+"Location=" + root[a].text + "</li><li> Time =" + time[a].text +  "</li>"
               b="<li> Temp=" +Temp[a].text + "</li><li> Humidity= " + Humidity[a].text+"</li>"
               c="<li>Sky=" + Sky[a].text + "</li><li>Visibility =" + visibility[a].text + "</li>"
               d="<li>Dew = " + Dew[a].text + "</li><li>Wind =" + Wind[a].text + "</li><li>pressure="+pressure[a].text+"</li>"
               html+=a1+b+c+d"""
               
        html +="</ul>"
        return html


        #return ls


    """
       Retrieves headlines from the Guardian news based on the content search
       Depends on public rest api of Guardian 
    """
    @rpc(String,_returns=Array(Topic))
    def news(self,section):
        
        r = requests.get('http://content.guardianapis.com/search?q={}&format=xml'.format(section))
        #r = r.encode("utf-16")
        tree = etree.fromstring(r.content)
        root1 = tree.xpath('/response/results/content')

        global news_database
        global topicid_seq
                 
        for i in range(len(root1)):

                 topic = Topic()

                 topic.tid = topicid_seq
                 topicid_seq = topicid_seq + 1
                 news_database[topic.tid] = topic
                 
                 attributes=root1[i].attrib

                 topic.sectionid = attributes.get("web-url")
                 topic.webtitle =  attributes.get("web-title") 

        return [v for k,v in news_database.items()]


        
    """
       This service retrieves lastest 15 statuses of the user
       Depends on public rest api of Twitter Inc
    """
    @rpc(String,_returns=String)
    def tweetSearch(self,name):

        # Making rest call to the twitter rest api using requests 
        r = requests.get('https://api.twitter.com/1/statuses/user_timeline.xml?include_entities=true&include_rts=true&screen_name={}&count=15'.format(name))

        # parsing xml string from the response using lxml
        tree = etree.fromstring(r.content)
        root = tree.xpath('/statuses/status')
        seq = 1
        d = {}

        for i in range(len(root)):
                s = tree.xpath('/statuses/status/text')
                d[i] = s[i].text


        html = "<ul>"
        for a in d.keys():
               html +="<li>"+d[a]+"</li>"
        html +="</ul>"
        return html

    """
       Checks the user authentication by making the user provided data with the entries in database
       Uses WS-Security headers to get the user provided credentials
    """

    @rpc(_returns=String,_in_header=WSSecurityHeader)
    def userAuth(self):
       print "Username:", self.soap_in_header.UsernameToken.Username

       user = self.soap_in_header.UsernameToken.Username
       password = self.soap_in_header.UsernameToken.Password

       conn = sqlite.connect("user.db")
       cur = conn.cursor()
       
       cur.execute("select * from  user where name = '{}'".format(user)) #checking user credentials with entries in database
       for row in cur.fetchall():
           if password ==row[1]:
                return "ok"
       return "fail"

    """
       Makes an xmlrpc call to the get_events of the server running on port no 8000 to get the list of all events
    """
       
    @rpc(_returns=String)
    def getEvents(self):
        client = xmlrpclib.ServerProxy("http://localhost:8000/")   #making an xmlrpc using xmlrpclib
        result = client.get_events()

        header = "<h1> Available Events </h1>"
        return "<html><body>" + header + str(result) + "</body></html>"
    
if __name__=='__main__':
    try:
        from wsgiref.simple_server import make_server
        server = make_server('localhost', 7785, Application([WeatherService], 'tns'))
        server.serve_forever()
    except ImportError:
        print "Error: example server code requires Python >= 2.5"
