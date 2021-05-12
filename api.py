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

def format_time(sec):

    """ Cambia el formato de tiempo"""

    mins = sec // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60
    return "Duración = {0}:{1}:{2}".format(int(hours),int(mins),sec)

def informacion_comerciantes(conn):
    
    """Retorna los precios de los 4 primeros anuncios"""

    currency = 'MXN'
    response = conn.call(method='GET',url= f'/buy-bitcoins-online/{currency}/.json')
    ad = response.json()['data']['ad_list']
    info = {'primero':{}, 'segundo':{}, 'tercero':{}, 'cuarto':{}}
    position = 0

    for inside_dict in info.values():
        
        inside_dict['price'] = float(ad[position]['data']['temp_price'])

        position += 1

    return info

def precio_actual(conn):

    """Devuelve el precio actual del anuncio"""
    
    ad_id = '1261529'
    response = conn.call(method='GET', url= f'/api/ad-get/', params={'ads': {ad_id}})
    ad = response.json()['data']['ad_list'][0]['data']
    precio_actual = float(ad['temp_price'])
    
    return precio_actual

def adelantar(precio_del_otro, conn, ad_id):

    """Adelanta un precio(se pone por debajo)"""

    nuevo_precio = round(precio_del_otro - 10)
    print(f'El precio a mejorar es {precio_del_otro} MXN')
    response = conn.call(method='POST', url= f'/api/ad-equation/{ad_id}/', params={'price_equation': f'{nuevo_precio}'})
    print(response.json())
    mi_nuevo_precio = precio_actual(conn)
    print(f'Mi nuevo precio es {mi_nuevo_precio} MXN')

def fijar(precio_limite, conn, ad_id):

    """Fija el anuncion en un precio determinado"""

    nuevo_precio = precio_limite
    response = conn.call(method='POST', url= f'/api/ad-equation/{ad_id}/', params={'price_equation':f'{nuevo_precio}'})
    print(response.json())
    mi_nuevo_precio = precio_actual(conn)
    print(f'Mi precio estabilizado por 15 min es {mi_nuevo_precio} MXN')
    
def update_price():

    """Actualiza el precio teniendo en cuenta un precio limite 
        total y posicion deseada. Cuando hay un cambio abrubto
        de mas de 300 MXN descansa por unos minutos.
    """
    
    precio_limite_total = float(input('Precio limite: '))
    posicion = str(input('Posicion: '))
    conn = conectar()
    ad_id = '1261529'

    while True:

        print('\nrunning...\n')
        mi_precio = precio_actual(conn)
        info = informacion_comerciantes(conn)
        precio_primero = info['primero']['price']
        precio_segundo = info['segundo']['price']
        precio_tercero = info['tercero']['price']
        precio_cuarto = info['cuarto']['price']

        if posicion == '1':

            precio_a_adelantar = precio_primero
            precio_a_ajustar = precio_segundo

        elif posicion == '2':

            precio_a_adelantar = precio_segundo
            precio_a_ajustar = precio_tercero

        elif posicion == '3':

            precio_a_adelantar = precio_tercero
            precio_a_ajustar = precio_cuarto
     
        if mi_precio > precio_a_adelantar:
            adelantar(precio_a_adelantar, conn, ad_id)
            precio_de_inicio = round(precio_a_adelantar - 10)
            print(f'Precio de inicio fue = {precio_de_inicio} MXN')
        
        else:
            adelantar(precio_a_ajustar, conn, ad_id)
            precio_de_inicio = round(precio_a_ajustar - 10)
            print(f'Precio de inicio fue = {precio_de_inicio} MXN')

        
        if precio_de_inicio < precio_limite_total:

            print(f'Precio limite total de {precio_limite_total} MXN alcanzado')
            fijar(precio_limite_total + 1, conn, ad_id)
            time.sleep(900)
            continue
        
        delta_de_precio = 0

        while delta_de_precio < 300:
            start_time = time.time()
            print('\nrunning...combat\n')
            mi_precio = precio_actual(conn)
            info = informacion_comerciantes(conn)
            precio_primero = info['primero']['price']
            precio_segundo = info['segundo']['price']
            precio_tercero = info['tercero']['price']
            precio_cuarto = info['cuarto']['price']
            print(f'primero = {precio_primero} MXN, segundo = {precio_segundo} MXN, tercero = {precio_tercero} MXN, cuarto = {precio_cuarto} MXN')

            if posicion == '1':

                precio_a_adelantar = precio_primero
                precio_a_ajustar = precio_segundo

            elif posicion == '2':

                precio_a_adelantar = precio_segundo
                precio_a_ajustar = precio_tercero

            elif posicion == '3':

                precio_a_adelantar = precio_tercero
                precio_a_ajustar = precio_cuarto

            if mi_precio > precio_limite_total:

                if mi_precio > precio_a_adelantar:
                    adelantar(precio_a_adelantar, conn, ad_id)
                
                else:
                    adelantar(precio_a_ajustar, conn, ad_id)

            else:
                print(f'Precio limite total de {precio_limite_total} MXN alcanzado')
                fijar(precio_limite_total + 1, conn, ad_id)
                time.sleep(900)

            mi_nuevo_precio = precio_actual(conn)

            delta_de_precio = precio_de_inicio - mi_nuevo_precio
            print(f'El delta de precio es: {delta_de_precio}')
            end_time = time.time()
            duracion = end_time - start_time    
            print(format_time(duracion))
            time.sleep(8)

        else:
            info = informacion_comerciantes(conn)
            precio_cuarto = info['cuarto']['price']
            adelantar(precio_cuarto, conn, ad_id)
            print('\nresting...\n')
            time.sleep(420)

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

    update_price()
    


    
    

