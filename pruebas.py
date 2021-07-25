import time
import datetime
import hashlib
import hmac as hmac_lib
import requests
import sys
import re
import csv
import os
from settings.settings import MX_KEY, MX_SECRET


from urllib.parse import urlparse

def conectar(server='https://localbitcoins.com'):

    """Se conecta a local bitcoins"""
    
    hmac_key = MX_KEY
    hmac_secret = MX_SECRET
    conn = Connection()
    conn._set_hmac(server, hmac_key, hmac_secret)
    
    return conn

def escribir_log(fiat, btc):

    with open(f'logs/{str(datetime.datetime.now().date())}.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([fiat,btc])

def leer_log():
    total_fiat = 0
    total_btc = 0
    with open(f'logs/{str(datetime.datetime.now().date())}.csv', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            total_fiat += float(row[0])
            total_btc += float(row[1])
    
    return total_fiat, round(total_btc,8)

def crear_log():

    if os.path.isfile('logs/año-mes-dia.csv'):
        print('gg')

    total_btc = 0
    total_btc = round(total_btc,8) if total_btc !=0 else 1
    print( total_btc)

def country_codes():

    conn = conectar()
    # response = conn.call(method='POST', url= f'/api/ad-equation/{ad_id}/', params={'price_equation': f'{nuevo_precio}'})

    # response = conn.call(method='GET', url= f'/api/payment_methods/')
    # response = conn.call(method='GET', url= f'/api/countrycodes/')

    # response = conn.call(method='GET',url= f'/buy-bitcoins-online/MXN/.json')
    # response = conn.call(method='GET', url='/api/notifications/')

    # notificaciones = response.json()['data']
    # print(response.json())
    # response = conn.call(method='GET',url= f'/buy-bitcoins-online/CRC/.json')
    # ad = response.json()['data']['ad_list']

    # response = conn.call(method='GET',url= f'/api/wallet-balance/')
    response = conn.call(method='GET',url= f'/api/dashboard/')

    
    print(response.json())

def respond_notification():

    """Atiende las notificaciones"""
    
    conn = conectar()
    response = conn.call(method='GET', url='/api/notifications/')
    

    notificaciones = response.json()['data']
    print(notificaciones)

    for notificacion in notificaciones:

        if notificacion['url'][32:48] == 'online_buy_buyer':
            print('hola')
            contact_id = notificacion['contact_id']
            contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
            for message in contact_messages:

                cuenta = re.search(r'\d{11}', message['msg'])
                if cuenta:
                    print(cuenta[0])

def prueba_rapida():
    conn = conectar()

    # response = conn.call(method='GET',url= f'/buy-bitcoins-online/CRC/.json')
    # response = conn.call(method='GET',url= f'/bitcoincharts/CRC/orderbook.json')
    # response = conn.call(method='GET',url= f'/bitcoincharts/CRC/trades.json')
    response = conn.call(method='GET',url= f'/api/fees/')
    mensaje = 'Procedo'
    contact_messages = conn.call(method='GET', url=f'/api/contact_messages/74660722/').json()['data']['message_list']

    for message in contact_messages:
        if message['msg'][0:4] == mensaje[0:4]:
            enviado = True
        cuenta1 = re.search(r'\d{11}', message['msg'])
        cuenta2 = re.search(r'\d{2,6}[-\s]+\d{2,6}[-\s]+\d{2,6}[-\s]?\d*', message['msg'])
        if cuenta1:
            num_cuenta = True
            cuenta = cuenta1
        if cuenta2:
            num_cuenta = True
            cuenta = cuenta2

    if num_cuenta:
        print(f'hola {cuenta[0]}')

def get_btc_en_scrow(currency):
    
    num_contactos = 1
    info = {'MX': 0, 'CR': 0}  #SUJETO A REVISION Y CAMBIO POR MAS PAISES

    if num_contactos != 0:
        for contacto in range(num_contactos):

            currency_low = 'CRC'
            amount_btc = 0.02158956
            fee_btc = 0.00021584

            info[f'{currency_low[0:2]}'] += float(amount_btc) + float(fee_btc)

        return round(info[f'{currency[0:2]}'],8) if info[f'{currency[0:2]}'] !=0 else 0

    return info[f'{currency[0:2]}']


class Connection():

    def __init__(self):
        self.server = None

        # HMAC stuff
        self.hmac_key = None
        self.hmac_secret = None

    def call(self, method, url, params=None, stream=False, files=None):
        method = method.upper()
        if method not in ['GET', 'POST']:
            raise Exception(u'Invalid method {}!'.format(method))

        if method == 'GET' and files:
            raise Exception(u'You cannot send files with GET method!')

        if files and not isinstance(files, dict):
            raise Exception(u'"files" must be a dict of file objects or file contents!')

        # If URL is absolute, then convert it
        if url.startswith(self.server):
            url = url[len(self.server):]

        # If HMAC
        if self.hmac_key:

            # If nonce fails, retry several times, then give up
            for retry in range(10):

                nonce = str(int(time.time() * 1000)).encode('ascii')

                # Prepare request based on method.
                if method == 'POST':
                    api_request = requests.Request('POST', self.server + url, data=params, files=files).prepare()
                    params_encoded = api_request.body

                # GET method
                else:
                    api_request = requests.Request('GET', self.server + url, params=params).prepare()
                    params_encoded = urlparse(api_request.url).query

                # Calculate signature
                message = nonce + self.hmac_key + url.encode('ascii')
                if params_encoded:
                    if sys.version_info >= (3, 0) and isinstance(params_encoded, str):
                        message += params_encoded.encode('ascii')
                    else:
                        message += params_encoded
                        
                signature = hmac_lib.new(self.hmac_secret, msg=message, digestmod=hashlib.sha256).hexdigest().upper()
                
                # Store signature and other stuff to headers
                api_request.headers['Apiauth-Key'] = self.hmac_key
                api_request.headers['Apiauth-Nonce'] = nonce
                api_request.headers['Apiauth-Signature'] = signature

                # Send request
                session = requests.Session()
                response = session.send(api_request, stream=stream)
                
                # If HMAC Nonce is already used, then wait a little and try again
                try:
                    response_json = response.json()
                    if int(response_json.get('error', {}).get('error_code')) == 42:
                        time.sleep(0.1)
                        continue
                    if response_json.get('error', {}).get('message'):
                        print(response_json.get('error', {}).get('message'))
                        print(response_json.get('error', {}).get('error_code'))
                        time.sleep(30)
                        continue
                except:
                    # No JSONic response, or interrupt, better just give up
                    pass

                return response
                
            raise Exception(u'Nonce is too small!')

        raise Exception(u'No  HMAC connection initialized!')

    def _set_hmac(self, server, hmac_key, hmac_secret):
        self.server = server
        self.client_id = None
        self.client_secret = None
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        self.hmac_key = hmac_key.encode('ascii')
        self.hmac_secret = hmac_secret.encode('ascii')

if __name__ == "__main__":

    entrada = get_btc_en_scrow('CRC')
    print(entrada)
