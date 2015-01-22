"""
   Implements the service which creates events by preforming the transaction based inserts into the sqlite database
   Uses WSAddressing to identify the sender of the request and call back address of the request
"""
import requests
from suds.client import Client
from soaplib.service import DefinitionBase
from soaplib.service import rpc
from soaplib.serializers.primitive import String, Integer
from soaplib.serializers.clazz import Array,ClassSerializer
from soaplib.wsgi import Application
from sqlite3 import dbapi2 as sqlite


"""
   Class to deserialize the WSAddressing headers 
"""
class WSAddrHeader(ClassSerializer):
	__namespace__ = "fbi"
	To = String
	From = String
	ReplyTo = String

class EventService(DefinitionBase):
    

            
    """
       creates  an event by performing a transaction based insert into the sqlite database
       Uses WSAddressing to get the list of events from  ReplyTo address
    """

    @rpc(String,String,_returns=String)
    def eventScheduler(self,name,d):


        #ToAddr = self.soap_in_header.To
        #FromAddr = self.soap_in_header.From
        #print "Adding event from:", self.soap_in_header.From
        #print "ReplyTo:", self.soap_in_header.ReplyTo
        
        conn = sqlite.connect("event.db")

        conn.isolation_level = None
        cur = conn.cursor()

        cur.execute('begin')
        
        #try:
            
        cur.execute("""
         CREATE TABLE IF NOT EXISTS event (
         name varchar,date varchar
         )
         """)
        cur.execute("insert into event values (?,?)", [name,d])

        conn.commit()

        #cb_client = Client(self.soap_in_header.ReplyTo)          # using ReplyTo address in WSAddr header to call the callback

	#result = cb_client.service.getEvents()
	#return str(result)

        
        
        cur.execute("select * from event order by date")

        dic={}
        html = "<ul>"
        for row in cur.fetchall():
                html +="<li>"+row[0]+"scheduled on " + row[1] + "</li>"
        html +="</ul>"

        return html

    
if __name__=='__main__':
    try:
        from wsgiref.simple_server import make_server
        server = make_server('localhost', 7786, Application([EventService], 'tns'))
        server.serve_forever()
    except ImportError:
        print "Error: example server code requires Python >= 2.5"
