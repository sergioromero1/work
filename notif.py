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
    return "Duración = {0}:{1}:{2}".format(int(hours),int(mins),round(sec,2))

def get_message_nuevo_comercio(verificador):
    
    """Devuelve el mensaje para nuevo comercio"""

    if verificador == 'cristina':
        return 'BANAMEX \n Cristina Nolasco \n\n Para pago en oxxo \n 5206 9496 3512 8290  \n\n Para Transferencia SPEI \n '\
                        '002180701431343757'
    
    if verificador == 'bbva':
        return 'BBVA Bancomer \n Cristina Nolasco \n\n Para pago en oxxo \n 4152 3135 9796 3326  \n\n Para Transferencia SPEI \n '\
                        '012180015420804899'

    if verificador == 'sergio':
        return 'HSBC \n Sergio Romero Romero \n\n Para pago en oxxo \n 4830 3031 5122 5386  \n\n Para Transferencia SPEI \n '\
                        '021180040645026366'

    if verificador == 'edgar':
        return 'HSBC \n Edgar Rivas Nolasco \n\n Para pago en oxxo \n 4830 3031 5121 4612  \n\n Para Transferencia SPEI \n '\
                        '021180040645025781'

    if verificador == 'perfiles':
        return 'BANAMEX \n Cristina Nolasco \n\n Para pago en oxxo \n 5204 1651 7729 2392  \n\n Para Transferencia SPEI \n '\
                        '002180700913724772'

def get_message_venta_completada():

    """Devuelve el mensaje para venta completada
        al cambiar el msj cambiar atender marcado como pagado.
    """
    
    mensaje = 'Gracias, comprobante recibido,\n '\
            'procedo a verificar el pago.'
    
    return  mensaje

def get_message_btc_liberados():
    """Devuelve el mensaje después de liberar los BTC"""
    
    mensaje = 'Liberados gracias por tu compra y por calificar'
    
    return  mensaje

def atender_final_venta(notificacion, conn):
    
    mensaje = get_message_btc_liberados()

    enviado = False

    contact_id = notificacion['contact_id']
    contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
    
    for message in contact_messages:
        if message['msg'][0:13] == mensaje[0:13]:
            enviado = True
    
    if not enviado:
        enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})        
        print(enviar_mensaje.json(), ' Mensaje Final de venta enviado')

def atender_nuevo_comercio(verificador, notificacion, conn):

    """Atiende la notificacion de 'tiene un nuevo comercio'"""

    mensaje = get_message_nuevo_comercio(verificador)
    contact_id = notificacion['contact_id']
    notification_id = notificacion['id']
    marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
    print(marcar_como_leida.json(), ' Notif leida Nuevo comercio')
    
    if is_afternoon():
        saludo = 'Buenas tardes \n'
    else:
        saludo = 'Buenos días \n'

    enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{saludo} {mensaje}'})
                
    print(enviar_mensaje.json(), ' Mensaje nuevo comercio enviado')

def atender_marcado_como_pagado(notificacion, conn):

    """Atiende la notificacion de marcado como pagado"""

    mensaje = get_message_venta_completada()

    attachment = False
    enviado = False
    contact_id = notificacion['contact_id']
    notification_id = notificacion['id']
    contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
    marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
    print(marcar_como_leida.json(), ' Notif leida marcado como pagado')

    for message in contact_messages:
        if 'attachment_type' in message:
            attachment = True

        if message['msg'][0:13] == mensaje[0:13]:
            enviado = True

    if attachment and not enviado:
        enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})
        print(enviar_mensaje.json(), ' Mensaje de venta completada enviado')

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
    print(marcar_como_leida.json(), ' Notif leida nuevo mensaje o comprobante')

    for message in contact_messages:
        if 'attachment_type' in message:
            attachment = True
        if message['msg'][0:13] == mensaje[0:13]:
            enviado = True
                            
    if contact_info['payment_completed_at'] is not None:
        payed = True
                    
    if attachment and payed and not enviado:
        enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})
        print(enviar_mensaje.json(), ' Mensaje de venta completada enviado')

def identificar_ad_id(notificacion, conn):
    
    contact_id = notificacion['contact_id']
    contact_info = conn.call(method='GET', url= f'/api/contact_info/{contact_id}/')
    ad_id = contact_info.json()['data']['advertisement']['id']
    
    return str(ad_id)

def notification_time(notificacion):
    
    created_at_str = notificacion['created_at'][0:10] + ' ' + notificacion['created_at'][11:19]

    created_at = datetime.datetime.strptime(created_at_str,'%Y-%m-%d %H:%M:%S').timestamp()

    now = datetime.datetime.utcnow().timestamp()

    return now - created_at

def respond_notification(verificador):

    """Atiende las notificaciones"""
    
    start_time = time.time()
    hmac_key = '7d95930f7cef535c7e8c16311dc9aa3f'
    hmac_secret = '760373e5a8cbc7a615a86b193cc48767583901080d223931a24235c0f48f4163'
    conn = hmac(hmac_key, hmac_secret)
    response = conn.call(method='GET', url='/api/notifications/')
    id_ad = '1261529'

    notificaciones = response.json()['data']

    for notificacion in notificaciones:

        if notificacion['url'][9:27] == 'online_sell_seller':

            notif_time = notification_time(notificacion)
    
            if not notificacion['read'] and notificacion['msg'][0:6] == '¡Tiene':

                ad_id = identificar_ad_id(notificacion, conn)
                if ad_id==id_ad:
                    atender_nuevo_comercio(verificador, notificacion, conn)
                
                continue

            if not notificacion['read'] and notificacion['msg'][0:11] == 'El contacto':
                
                ad_id = identificar_ad_id(notificacion, conn)
                if ad_id==id_ad:
                    atender_marcado_como_pagado(notificacion, conn)

                continue

            if not notificacion['read'] and notificacion['msg'][0:13] == 'Nuevo mensaje':

                ad_id = identificar_ad_id(notificacion, conn)
                if ad_id==id_ad:
                    atender_nuevo_mensaje(notificacion, conn)

                continue

            if notif_time < 60 and notificacion['msg'][0:12] == 'Ha realizado':

                ad_id = identificar_ad_id(notificacion, conn)
                if ad_id==id_ad:
                    atender_final_venta(notificacion, conn)

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
        verificador = sys.argv[1]
        respond_notification(verificador)
        time.sleep(20)



