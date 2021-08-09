import time
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

def informacion_comerciantes(conn, currency):
    
    """Retorna la informacion de los 6 primeros anuncios"""

    response = conn.call(method='GET',url= f'/buy-bitcoins-online/{currency}/.json')
    ad = response.json()['data']['ad_list']
    info = {'primero':{}, 'segundo':{}, 'tercero':{}, 'cuarto':{}, 'quinto':{}, 'sexto':{}}
    position = 0

    for inside_dict in info.values():
        
        inside_dict['name'] = str(ad[position]['data']['profile']['username'])
        inside_dict['price'] = float(ad[position]['data']['temp_price'])
        inside_dict['min_amount'] = float(ad[position]['data']['min_amount']) if ad[position]['data']['min_amount'] is not None else 0
        inside_dict['max_amount'] = float(ad[position]['data']['max_amount_available'])

        position += 1

    return info

def precio_de_colombia(conn):

    currency = 'COP'
    response = conn.call(method='GET',url= f'/sell-bitcoins-online/{currency}/.json')
    ad = response.json()['data']['ad_list']
    primer_precio = float(ad[0]['data']['temp_price'])

    return primer_precio

def margen(conn, precio_compra, currency, mi_max, mi_min):

    """Retorna el margen """

    info = informacion_comerciantes(conn, currency)
    for puesto,datos in info.items():
        if mi_max >= datos['min_amount'] and mi_min <= datos['max_amount'] and datos['name'] != 'sromero':
            puesto_a_superar = str(puesto)
            break
    
    primer_precio = info[f'{puesto_a_superar}']['price']

    margen = primer_precio / precio_compra

    return margen

def margenes(precio_MXN,precio_CRC):

    """Retorna el valor de los margenes de MEX y CRC
    """
    
    mi_min_mx = 100 
    mi_min_cr = 5000
    mi_max_mx = 10000
    mi_max_cr = 160000

    conn = conectar()
    precio_colombia = precio_de_colombia(conn)
    precio_compra_MXN = precio_colombia / precio_MXN
    precio_compra_CRC = precio_colombia / precio_CRC
    m_mexico = margen(conn, precio_compra_MXN, 'MXN',mi_max_mx, mi_min_mx)
    m_costa_rica = margen(conn, precio_compra_CRC, 'CRC',mi_max_cr,mi_min_cr)
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
    precio_MXN= float(sys.argv[1])
    precio_CRC= float(sys.argv[2])
    margenes(precio_MXN, precio_CRC)
    


    
    

