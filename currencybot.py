import config
import requests

from datetime import datetime
from urllib import quote

# The main URL for the Telegram API with our bot's token
BASE_URL = "https://api.telegram.org/bot{}".format(config.bot_token)


def parse_conversion_query(query):
    """Convert a NL query to amount, currency_from, current_to components"""
    url_template = "https://api.api.ai/api/query?v=20150910&query={}&lang=en&sessionId={}"
    print(query)
    print(type(query))
    # query = quote(query)
    url = url_template.format(query, datetime.now())
    headers = {"Authorization": config.apiai_bearer}
    response = requests.get(url, headers=headers)
    js = response.json()
    # print(js)
    currency_to = js['result']['parameters']['currency-to']
    currency_from = js['result']['parameters']['currency-from']
    amount = js['result']['parameters']['amount']
    return amount, currency_from, currency_to


def get_rate(frm, to):
    """Get the raw conversion rate between two currencies"""
    url = "http://free.currencyconverterapi.com/api/v4/convert?q={}_{}&compact=ultra".format(frm, to)
    try:
        response = requests.get(url)
        js = response.json()
        key = frm + "_" + to
        rates = js[key]
        return rates
    except Exception as e:
        print(e)
        return 0


def get_conversion(quantity=1, frm="USD", to="GBP"):
    rate = get_rate(frm.upper(), to.upper())
    to_amount = quantity * rate
    return "{} {} = {} {}".format(quantity, frm, to_amount, to)


def receive_message(message):
    """Receive a raw message from Telegram"""
    try:
        text = str(message["message"]["text"])
        chat_id = message["message"]["chat"]["id"]
        return text, chat_id
    except Exception as e:
        print(e)
        print(message)
        return (None, None)
    
 
def handle_message(message):
    """Calculate a reponse to a message"""
    try:
        qty, frm, to = parse_conversion_query(message)
        qty = int(qty)
        response = get_conversion(qty, frm, to)
    except Exception as e:
        print(e)
        response = "I couldn't parse that"
    return response

    
def send_message(message, chat_id):
    """Send a message to the Telegram chat defined by chat_id"""
    data = {"text": message.encode("utf8"), "chat_id": chat_id}
    url = BASE_URL + "/sendMessage"
    try:
        response = requests.post(url, data).content
    except Exception as e:
        print(e)
        

def run(message):
    """Receive a message, handle it, and send a response"""
    try:
        message, chat_id = receive_message(message)
        response = handle_message(message)
        send_message(response, chat_id)
    except Exception as e:
        print(e)
