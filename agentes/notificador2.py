from decoradores.loop import loop
from .conectar import Connection

import csv
import datetime
import pytz
import requests
import time

class Notificador:

    def __init__(self, bot_token,currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador,administrador, enviar_mensaje, verificador2):

        self.administrador = administrador
        self.bot_token = bot_token
        self.currency = currency
        self.enviar_mensaje = enviar_mensaje
        self.id_ad = id_ad
        self.key = key
        self.secret = secret
        self.sleep_time = sleep_time
        self.receptor = receptor
        self.receptores = receptores
        self.verificador = verificador
        self.verificador2 = verificador2

    def get_atributos(self, *nombres: str):
        """Retorna los atributos solicitados como una tupla"""

        return (self.__dict__[nombre] for nombre in nombres)

    def atender_nuevo_comercio(self, notificacion, conn):

        """Atiende la notificacion de 'Tiene un nuevo comercio'"""

        mensaje_nuevo_comercio = self.get_message_nuevo_comercio()

        contact_id = notificacion['contact_id']

        self.send_msg_contact(conn, contact_id, mensaje_nuevo_comercio, f'Mensaje de nuevo comercio enviado #{contact_id}', verbose=True)
        
        self.marcar_notificacion_como_leida(conn,notificacion,f'Nuevo comercio #{contact_id}')
            
    def conectar(self,server='https://localbitcoins.com'):

        """Se conecta a local bitcoins"""

        key, secret = self.get_atributos("key", "secret")
        conn = Connection()
        conn._set_hmac(server, key, secret)
        
        return conn

    def get_message_nuevo_comercio(self):
        
        receptor, receptores = self.get_atributos("receptor","receptores")

        """Devuelve el mensaje para nuevo comercio"""

        return receptores[receptor]

    def identificar_ad_id(self, notificacion, conn):
        
        contact_id = notificacion['contact_id']
        contact_info = self.get_contact_info(conn, contact_id)
        ad_id = contact_info['advertisement']['id']
        
        return str(ad_id)

    #@loop
    def iniciar(self):

        sleep_time = int(self.sleep_time)

        while True:
            self.respond_notifications()
            time.sleep(sleep_time)

    def marcar_notificacion_como_leida(self,conn, notificacion, descripcion):

        administrador, = self.get_atributos('administrador')

        notification_id = notificacion['id']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(
            marcar_como_leida.json(), 
            f' Notif leida de {descripcion} ',
            {str(datetime.datetime.now(pytz.timezone('America/Bogota')))[:19]},
            flush=True)
        self.send_text([administrador],f'Se marcó notificacion {descripcion} como leida ',verbose=False)
        
    def respond_notifications(self):

        """Atiende las notificaciones"""

        id_ad, currency = self.get_atributos("id_ad", "currency")
        print(f'Revisando notificaciones...{currency[0:2]}', flush=True)
        conn = self.conectar()
        response = conn.call(method='GET', url='/api/notifications/')
        notificaciones = []
        try:
            notificaciones = response.json()['data']
        except ValueError:
            print(f"Empty response at {str(datetime.datetime.now(pytz.timezone('America/Bogota')))[:19]}", flush=True)

        for notificacion in notificaciones:

            if notificacion['url'][9:27] == 'online_sell_seller':
        
                if not notificacion['read'] and notificacion['msg'][0:6] == '¡Tiene':

                    ad_id = self.identificar_ad_id(notificacion, conn)
                    if ad_id==id_ad:
                        self.atender_nuevo_comercio(notificacion, conn)

    def send_msg_contact(self,conn, contact_id, mensaje, descripcion, verbose=False):

        administrador, = self.get_atributos('administrador')

        hora = str(datetime.datetime.now(pytz.timezone('America/Bogota')))[:19]

        """Envia un mensaje a un contact_id"""
        try:
            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})
        except ValueError:
            print(f"send_msg_contact error at {hora}", flush=True)
            self.send_text([administrador], f'send_msg to contact error at {hora}')

        if enviar_mensaje:
            self.send_text([administrador], 'Se ha enviado mensaje a nuevo comercio indicando la cuenta a consignar')

        if verbose == True:
            print(
                enviar_mensaje.json(), 
                f'{descripcion}',
                f'{hora}',
                flush=True)

    def send_text(self, receptores, bot_message, verbose=False):

        """Envia un mensaje a a la lista 'receptores' en telegram"""
        
        bot_token, enviar_mensaje = self.get_atributos("bot_token", "enviar_mensaje")

        if enviar_mensaje:
            for receptor in receptores:
                send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + receptor + '&parse_mode=Markdown&text=' + bot_message
                response = requests.post(send_text)
            if verbose == True:
                print(bot_message,response, flush=True)

        else:
            print('Envio de mensajes desactivado')
        




