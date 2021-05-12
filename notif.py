import time
import datetime
import hashlib
import hmac as hmac_lib
import requests
import sys
from urllib.parse import urlparse

def hmac(hmac_key, hmac_secret, server='https://localbitcoins.com'):
    conn = Connection()
    conn._set_hmac(server, hmac_key, hmac_secret)
    return conn

def is_afternoon():

    """Devuelve True si es en la tarde"""
    
    return datetime.datetime.now().time() > datetime.time(12,0)

def format_time(sec):

    """Cambia el formato de tiempo"""

    mins = sec // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60
    return "Duración = {0}:{1}:{2}".format(int(hours),int(mins),sec)

def get_message_nuevo_comercio(numero):
    
    """Devuelve el mensaje para nuevo comercio"""

    if numero == '1':
        return 'BANAMEX \n Para pago en oxxo \n 5206 9496 3512 8290 \n Cristina Nolasco \n\n Transferencia SPEI \n '\
                        '002180701431343757'
    
    if numero == '2':
        return 'BBVA Bancomer \n Para pago en oxxo \n 4152 3135 9796 3326 \n Cristina Nolasco \n\n Transferencia SPEI \n '\
                        '012180015420804899'

    if numero == '3':
        return 'HSBC \n Para pago en oxxo \n 4830 3031 5122 5386 \n Sergio Romero \n\n Transferencia SPEI \n '\
                        '021180040645026366'

    if numero == '4':
        return 'HSBC \n Para pago en oxxo \n 4830 3031 5121 4612 \n Edgar Rivas \n\n Transferencia SPEI \n '\
                        '021180040645025781'

    if numero == '5':
        return 'BANAMEX \n Para pago en oxxo \n 5204 1651 7729 2392 \n Cristina Nolasco \n\n Transferencia SPEI \n '\
                        '002180700913724772'

def get_message_venta_completada():

    """Devuelve el mensaje para venta completada"""
    
    mensaje = 'Comprobante recibido amig@,\n '\
            'procedo a verificar el pago y a liberar. \n Gracias por tu compra.'
    
    return  mensaje

def atender_nuevo_comercio(notificacion, conn):

    """Atiende la notificacion de 'tiene un nuevo comercio'"""

    mensaje = get_message_nuevo_comercio('4')

    contact_id = notificacion['contact_id']
    notification_id = notificacion['id']
    marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
    print(marcar_como_leida.json())
    
    if is_afternoon():
        saludo = 'Buenas tardes \n'
    else:
        saludo = 'Buenos días \n'

    enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{saludo} {mensaje}'})
                
    print(enviar_mensaje.json())

def atender_marcado_como_pagado(notificacion, conn):

    """Atiende la notificacion de marcado como pagado"""

    mensaje = get_message_venta_completada()

    attachment = False
    enviado = False
    contact_id = notificacion['contact_id']
    notification_id = notificacion['id']
    contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
    marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
    print(marcar_como_leida.json())

    for message in contact_messages:
        if 'attachment_type' in message:
            attachment = True

        if message['msg'][0:13] == 'Pago recibido':
            enviado = True

    if attachment and not enviado:
        enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})
        print(enviar_mensaje.json())

def atender_nuevo_mensaje(notificacion, conn):

    """Atiende un mensaje nuevo"""

    mensaje = get_message_venta_completada()

    attachment = False
    payed = False
    enviado = False
    contact_id = notificacion['contact_id']
    notification_id = notificacion['id']
    contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
    contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
    marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
    print(marcar_como_leida.json())

    for message in contact_messages:
        if 'attachment_type' in message:
            attachment = True
        if message['msg'][0:11] == 'Comprobante':
            enviado = True
                            
    if contact_info['payment_completed_at'] is not None:
        payed = True
                    
    if attachment and payed and not enviado:
        enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})
        print(enviar_mensaje.json())

def respond_notification():

    """Atiende las notificaciones"""
    
    start_time = time.time()
    hmac_key = '7d95930f7cef535c7e8c16311dc9aa3f'
    hmac_secret = '760373e5a8cbc7a615a86b193cc48767583901080d223931a24235c0f48f4163'
    conn = hmac(hmac_key, hmac_secret)
    response = conn.call(method='GET', url='/api/notifications/')

    notificaciones = response.json()['data']

    for notificacion in notificaciones:

        if notificacion['url'][9:27] == 'online_sell_seller':
    
            if not notificacion['read'] and notificacion['msg'][0:6] == '¡Tiene':

                atender_nuevo_comercio(notificacion, conn)
                
                continue

            if not notificacion['read'] and notificacion['msg'][0:11] == 'El contacto':

                atender_marcado_como_pagado(notificacion, conn)

                continue

            if not notificacion['read'] and notificacion['msg'][0:13] == 'Nuevo mensaje':

                atender_nuevo_mensaje(notificacion, conn)

    end_time = time.time()
    duracion = end_time - start_time    
    print(format_time(duracion))

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
        
    while True:
        print('Revisando notificaciones...')
        respond_notification()
        time.sleep(20)



