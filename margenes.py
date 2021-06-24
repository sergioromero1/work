import time
import datetime
import hashlib
import hmac as hmac_lib
import requests
import sys
from urllib.parse import urlparse

def conectar(server='https://localbitcoins.com'):

    """Se conecta a local bitcoins"""
    
    hmac_key = 'b32975118459480a9d6b58366e8fd957'
    hmac_secret = '12dfaeb0f082f7706c89313f6b1de9e7b79c3ce582a07bb708196551f5b263f2'
    conn = Connection()
    conn._set_hmac(server, hmac_key, hmac_secret)
    
    return conn

def precio_de_colombia(conn):

    currency = 'COP'
    response = conn.call(method='GET',url= f'/sell-bitcoins-online/{currency}/.json')
    ad = response.json()['data']['ad_list']
    primer_precio = float(ad[0]['data']['temp_price'])

    return primer_precio

def precio_de_colombia_comun(conn):

    currency = 'COP'
    response = conn.call(method='GET',url= f'/buy-bitcoins-online/{currency}/.json')
    ad = response.json()['data']['ad_list']
    primer_precio = float(ad[0]['data']['temp_price'])

    return primer_precio

def margen_costa_rica(conn, precio_compra_CRC):

    """Retorna el margen de Costa Rica"""

    currency = 'CRC'
    response = conn.call(method='GET',url= f'/buy-bitcoins-online/{currency}/.json')
    ad = response.json()['data']['ad_list']
    primer_precio_CRC = float(ad[0]['data']['temp_price'])
    margen = primer_precio_CRC / precio_compra_CRC
    # print(primer_precio_CRC, precio_compra_CRC)
    return margen

def margen_mexico(conn, precio_compra_MXN):

    """Retorna el margen de Mexico"""

    currency = 'MXN'
    response = conn.call(method='GET',url= f'/buy-bitcoins-online/{currency}/.json')
    ad = response.json()['data']['ad_list']
    primer_precio_MXN = float(ad[0]['data']['temp_price'])
    margen = primer_precio_MXN / precio_compra_MXN

    return margen

def margenes():

    """Retorna el valor de los margenes de MEX y CRC
    """
    
    precio_MXN = float(input('Precio MXN: '))
    precio_CRC = float(input('Precio CRC: '))

    conn = conectar()
    precio_colombia = precio_de_colombia(conn)
    precio_colombia_comun = precio_de_colombia_comun(conn)
    print(f'\nPrecio de colombia pulgar = {precio_colombia}\n')
    print(f'\nPrecio de colombia comun = {precio_colombia_comun}\n')
    precio_compra_MXN = precio_colombia / precio_MXN
    precio_compra_CRC = precio_colombia / precio_CRC
    m_mexico = margen_mexico(conn, precio_compra_MXN)
    m_costa_rica = margen_costa_rica(conn, precio_compra_CRC)
    print(f'\nMargen de México = {m_mexico}..\n')
    print(f'\nMargen de CR = {m_costa_rica}..\n')

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

    margenes()
    


    
    

