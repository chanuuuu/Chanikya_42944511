"""
   An xmlrpc implementation of the service to get the list of all events
   The srevice allows the consumer of the service to make an xml rpc to the service 
"""
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from sqlite3 import dbapi2 as sqlite

def get_events():
    
    conn = sqlite.connect("event.db")
    cur = conn.cursor()
    cur.execute("select * from event order by date")
    dic={}
    html = "<ul>"
    for row in cur.fetchall():
        html +="<li>"+row[0]+"  scheduled on   " + row[1] + "</li>"
    html +="</ul>"

    return html

server = SimpleXMLRPCServer(("localhost", 8000))
print "Listening on port 8000..."
server.register_function(get_events)
server.serve_forever()
