"""
   A client application to access the available services
"""
from wsgiref import simple_server
import cgi
import fnmatch
from suds.client import Client
from server import Topic
from array import array
from soaplib.serializers.primitive import String, Integer
from soaplib.serializers.clazz import Array,ClassSerializer
from sqlite3 import dbapi2 as sqlite
from suds.sax.element import Element
from suds.wsse import *
import xmlrpclib
from flask_jsonrpc.proxy import ServiceProxy


login_page ="""<html>
  <body>
   <h1>Login Page </h1>
   <form action = "/form/login_data">
   UserName : <input type="text" name="userid"></br>
   Password : <input type="text" name="pwd"></br>
   <input type="submit" value="login">
   <div>
   <p><a href="/signup.html">Create new account </a></p>
   </div>
   </form>
   </body>
   </html>
"""

signup_page = """<html>
  <body>
   <h1>Login Page </h1>
   <form action = "/form/signup_data">
   First name:<input type="text" name="fname"></br>
   Last name:<input type="text" name="lname"></br>
   UserName : <input type="text" name="user"></br>
   Password : <input type="text" name="pass"></br>
   <input type="submit" value="create">
   </form>
   </body>
   </html>
"""


home_page = """<html>
 <body>
   <h1>Home Page</h1>   
   <p>Welcome user!</p>
   <p>Available web services</p>
   <p><a href="/weather.html">Global Weather</a></p>
   <p><a href="/news.html"> Guardian Headlines</a></p>
   <p><a href="/tweet.html">Twitter Search</a></p>
   <p><a href="/stock.html">Get Stock Quote</a></p>
   <p><a href="/event.html">Add an Event</a></p>
 </body>
 </html>
"""

weather_page = """<html>
 
 <body>
 <form method="get" action="/form/weather_data">
 Enter city:<input type="text" name="city"><br/>
 Enter country: <input type = "text" name ="country"><br/>
 <input type="submit" value="submit">
 </form>
 <div>
   <a href="/index.html">Home</a>
 </div>
 </body>
</html>"""

news_page = """<html>

 <body>
 <form method="get" action="/form/news_data">
 Enter filter: <input type = "text" name ="filter"><br/>
 <input type="submit" value="submit">
 </form>
 <div>
   <a href="/index.html">Home</a>
 </div>
 </body>
</html>
"""

tweet_page = """<html>
 <body>
 <form method="get" action="/form/tweet_data">
 <h1>Twitter page !</h1>
 <h2>Here you can retrieve the statuses of the given user </h2>
 Enter Screen name of the user : <input type = "text" name ="scname"><br/>
 <input type="submit" value="submit">
 </form>
 <div>
   <a href="/index.html">Home</a>
 </div>
 </body>
</html>
"""
event_page = """<html>

 <body>
 <h1>Add an event </h1>
 <form method="get" action="/form/event_data">
 Name of the event: <input type = "text" name ="event"><br/>
 Date :  <input type = "date" name ="dt"><br/>
 <input type="submit" value="create">
 </form>
 <p><a href="/getevents.html">See Added Events</a></p>
 <div>
   <a href="/index.html">Home</a>
 </div>
 </body>
</html>
"""

stock_page = """<html>

 <body>
 <h1>Get Stock value  </h1>
 <form method="get" action="/form/stock_data">
 Name of the quote: <input type = "text" name ="quote">
 <input type="submit" value="GetValue">
 </form>
 <div>
   <a href="/index.html">Home</a>
 </div>
 </body>
</html>
"""



class Topic(ClassSerializer):
        __namespace__ = "ns1"
        tid =Integer
        sectionid = String
        webtitle = String


def index(eviron,start_response):
    start_response('200 OK', [('content-type','text/html')])
    return [home_page,]


def application(environ, start_response):
    for path, app in routes: 
        if fnmatch.fnmatch(environ['PATH_INFO'], path): 
            return app(environ, start_response)
    return not_found(environ, start_response)

def not_found(environ, start_response):
    start_response('404 Not Found', [('content-type','text/html')])
    return ["""<html><h1>Page not Found</h1><p>That page is unknown. Return to the <a href="/">home page</a></p></html>""",]  

def news(environ, start_response):
    start_response('200 OK', [('content-type','text/html')])
    return [news_page,]

def weather(environ, start_response):
    start_response('200 OK', [('content-type','text/html')])
    return [weather_page,]

def twitter(environ, start_response):
    start_response('200 OK', [('content-type','text/html')])
    return [tweet_page,]

def event(environ, start_response):
    start_response('200 OK', [('content-type','text/html')])
    return [event_page,] 


"""
   gets data from weather service using suds and returns an html page 
"""
def weather_data(environ, start_response):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    city_name = str(form.getvalue("city"))
    country_name = str(form.getvalue("country"))

    hello_client = Client('http://localhost:7785/?wsdl')
    result = hello_client.service.weather(city_name, country_name)
    start_response("200 OK", [('content-type','text/html')])
    h = "<h1>Weather Forecast of " + city_name + "</h1>"
    home_header = "<div><a href='/index.html'>Home</a></div>"
    return ["<html><body>", h , str(result),home_header, "</body></html>"]


"""
   Retrieves data from news service using suds 
"""
def news_data(environ, start_response):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    #city_name = str(form.getvalue("topic"))
    search = str(form.getvalue("filter"))
    t = Topic()
    dic = {}
    hello_client = Client('http://localhost:7785/?wsdl')
    result = hello_client.service.news(search)
    print type(result)
    # Iterating over TopicArray
    for topic in result:
            for t in topic[1]:
                    link = "<a href=" +t.sectionid +">" + t.sectionid + "</a>"
                    dic[t.webtitle] = link      
                    #print dic[t.sectionid]
                    #print t.sectionid,t.webtitle
    start_response("200 OK", [('content-type','text/html')])
    html = "<ul>"
    for key in dic.keys():
        html += "<li><strong>"+key+"</strong> "+dic[key]+"</li>"
    html += "</ul>"
    h=html.encode('ascii', 'ignore')

    home_header = "<div><a href='/index.html'>Home</a></div>"
    header = "<h1>Guardian News </h1>"
    return ["<html><body>",header, h,home_header, "</body></html>"]


"""
   Retrieves data from tweetSearch service using suds
"""
def tweet_data(environ,start_response):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    name = str(form.getvalue("scname"))


    hello_client = Client('http://localhost:7785/?wsdl')
    result = hello_client.service.tweetSearch(name)

    # Ignoring the foreign unicode characters 
    r = result.encode('ascii','ignore')

    header = "<h1>Top 15 latest tweets of the " + name + "</h1>"
    home_header = "<div><a href='/index.html'>Home</a></div>"
                   
    start_response("200 OK", [('content-type','text/html')])
    return ["<html><body>", header , r ,home_header, "</body></html>"]

"""
   creates an event by passing the form details to eventScheduler service
   Uses WSAddressing to specify the destination address,source address and call back address
"""
def event_data(environ,start_response):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    event_name = str(form.getvalue("event"))
    event_date = str(form.getvalue("dt"))
    
    client = Client('http://localhost:7786/?wsdl')

    wsans = ('wsa', 'http://namespaces/sessionid')
    wsa = Element('wsa', ns=wsans)
    to_elem = Element('To', ns=wsans).setText('http://localhost:7786/?wsdl')
    from_elem = Element('From', ns=wsans).setText('http://localhost:8080/?wsdl')
    replyto_elem = Element('ReplyTo', ns=wsans).setText('http://localhost:7785/?wsdl')
    wsa.append(to_elem)
    wsa.append(from_elem)
    wsa.append(replyto_elem)
    client.set_options(soapheaders=wsa)  # Adding the created WSAddr headers to the soap request
    
    result = client.service.eventScheduler(event_name,event_date)

    #header = "<h1> Available Events </h1>"
    home_header = "<div><a href='/index.html'>Home</a></div>"
    start_response("200 OK", [('content-type','text/html')])
    return ["<html><body>", str(result),home_header, "</body></html>"]

"""
   Makes an XmlRpc call to the server running on http://localhost:8000 and gets list of all events
"""

def all_events(environ,start_response):
    client = xmlrpclib.ServerProxy("http://localhost:8000/")  # Using xmlrpclib to make an xmlrpc call
    result = client.get_events()

    header = "<h1> Available Events </h1>"
    home_header = "<div><a href='/index.html'>Home</a></div>"
    start_response("200 OK", [('content-type','text/html')])
    return ["<html><body>", header,str(result), home_header, "</body></html>"]


def login(environ,start_response):
    start_response('200 OK', [('content-type','text/html')])
    return [login_page,]

"""
   Enables users to login by passing the login credentials to the server at http://localhost:7785/ using WSSecurity headers
   and checks the authenticity of the user
"""
def login_check(environ,start_response):
    
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    user_name = str(form.getvalue("userid"))
    password = str(form.getvalue("pwd"))
    
    hello_client = Client('http://localhost:7785/?wsdl')
    security = Security()
    token = UsernameToken(user_name, password)
    security.tokens.append(token)
    hello_client.set_options(wsse=security)   # Adding the WS-Security headers to the soap request
    result = hello_client.service.userAuth()

    start_response("200 OK", [('content-type','text/html')])
    
    if str(result) =="ok":
       return [home_page]
       #start_response('302 Redirect', [('Location', '/index.html')])
    else:
       #start_response('302 Redirect', [('Location', '/signup.html')])"""
       return [login_page]
    
    
def signup(environ,start_response):
    start_response('200 OK', [('content-type','text/html')])
    return [signup_page,]

"""
   Enables the users to create new user accounts
"""
def signup_data(environ,start_response):
        
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    user_name = str(form.getvalue("user"))
    password = str(form.getvalue("pass"))

    conn = sqlite.connect("user.db")
    cur = conn.cursor()
    cur.execute("""
         CREATE TABLE IF NOT EXISTS user (
         name varchar primary key,password varchar
         )
         """)
    cur.execute("insert into user values (?,?)", [user_name,password])

    conn.commit()

    #start_response('302 Redirect', [('Location', '/login.html')])

    start_response("200 OK", [('content-type','text/html')])
    return [login_page]

def get_quote(environ,start_response):
    start_response('200 OK', [('content-type','text/html')])
    return [stock_page,]

"""
   Retrieves stock quote value from the getStockQuote service of the server running at port no 5000 by making a flask jsonrpc call
"""
def getQuoteValue(environ,start_response):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    symbol = str(form.getvalue("quote"))
    
    server = ServiceProxy('http://localhost:5000/api')
    result = server.app.getStockQuote(symbol)
    r ="<ul style=\"list-style : none;\">"
    for key in result.keys():
        if key == "result":                
           r = str(result[key])
    r += "</ul>"
    header = "<h1>Stock Quote for " + symbol + "</h1>"
    home_header = "<div><a href='/index.html'>Home</a></div>"
    start_response('200 OK', [('content-type','text/html')])
    return ["<html><body>", header, r , home_header , "</body></html>"]
    

routes = [('/', login),
          ('/index.html',   index),
          ('/weather.html',weather),
          ('/news.html',news),
          ('/form/weather_data*',weather_data),
          ('/form/news_data*',news_data),
          ('/tweet.html',twitter),
          ('/form/tweet_data*',tweet_data),
          ('/event.html',event),
          ('/form/event_data*',event_data),
          ('/login.html',login),
          ('/form/login_data*',login_check),
          ('/signup.html',signup),
          ('/form/signup_data*',signup_data),
          ('/getevents.html',all_events),
          ('/stock.html',get_quote),
          ('/form/stock_data*',getQuoteValue)
         ]



import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)

if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    print "Listening for requests on http://localhost:8080/"
    server.serve_forever()    
    


