"""
   A flask jsonrpc implementation of a stock quote service.The service returns a dictionary with a value key containing stock quote value
"""
from flask import Flask
from flask_jsonrpc import JSONRPC
from lxml import etree
from suds.client import Client
from flask_jsonrpc.types import Object, Number, Boolean, String, Array, Nil, Any, Type

class Room:
    symbol = String

app = Flask(__name__)
jsonrpc = JSONRPC(app, '/api')

@jsonrpc.method('app.getStockQuote')
def getStockQuote(symbol):

        client = Client('http://www.webservicex.net/stockquote.asmx?WSDL')  #Accessing the getQuote service of webserviceX.net using suds
        result = client.service.GetQuote(symbol)

        result = result.encode("utf-16")                                    # encoding the utf-8 format data to utf-16
        tree=etree.fromstring(result)
        Name = tree.xpath('/StockQuotes/Stock/Name')                        # using xpath to access elements of the xml string
        r = tree.xpath('/StockQuotes/Stock/Last')
        t = tree.xpath('/StockQuotes/Stock/Time')
        d = tree.xpath('/StockQuotes/Stock/Date')
        C = tree.xpath('/StockQuotes/Stock/Change')
        Open = tree.xpath('/StockQuotes/Stock/Open')
        High = tree.xpath('/StockQuotes/Stock/High')
        Low = tree.xpath('/StockQuotes/Stock/Low')
        Cap = tree.xpath('/StockQuotes/Stock/MktCap')
        

        r1 = "Last:" + r[0].text
        #html ="""<ul style="list-style: none;">"""
        html = "<li>Name:"+Name[0].text + "</li><li>Last:" + r[0].text + "</li><li>Time : " + t[0].text + "</li><li>Date:" + d[0].text + "</li><li>Change:"  + C[0].text + "</li>"  
        html += "<li>Open:" + Open[0].text + "</li><li>High: " + High[0].text + "</li><li>Low:" + Low[0].text + "</li><li>Market cap:" + Cap[0].text + "</li>"
        #html +="</ul>"
        #print html

        #html = "<li>Name:"+Name[0].text + "</li><li>Last:" + r[0].text + "</li><li>High: " + High[0].text + "</li><li>Low:" + Low[0].text + "</li>"
        return html


if __name__ == '__main__':
    #app.run()
    app.run(host='0.0.0.0', debug=0)
