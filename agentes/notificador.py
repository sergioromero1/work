from decoradores.loop import loop
from .conectar import Connection
from utils.color import Color

import csv
import datetime
import requests
import time
import re

class Notificador:

    def __init__(self, bot_token,currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador):

        self.bot_token = bot_token
        self.currency = currency
        self.id_ad = id_ad
        self.key = key
        self.secret = secret
        self.sleep_time = sleep_time
        self.receptor = receptor
        self.receptores = receptores
        self.verificador = verificador

    def get_atributos(self, *nombres: str):
        """Retorna los atributos solicitados como una tupla"""

        return (self.__dict__[nombre] for nombre in nombres)

    def atender_final_venta(self, notificacion, conn):

        """Actua después de haber liberado los btc,
            envia un mensaje al cliente y escribe en el log
        """
        currency, = self.get_atributos('currency')
        mensaje = self.get_message_btc_liberados()

        enviado = False

        contact_id = notificacion['contact_id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']

        for message in contact_messages:
            if message['msg'][0:13] == mensaje[0:13]:
                enviado = True
        
        if not enviado:
            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})        
            print(enviar_mensaje.json(), ' Mensaje Final de venta enviado')
            fiat = contact_info['amount']
            btc = float(contact_info['amount_btc']) + float(contact_info['fee_btc'])
            self.escribir_log(fiat, btc)
            print(self.con_color(f'Se escribió en el log venta de {btc} por {fiat} {currency}'))

    def atender_nuevo_comercio(self, notificacion, conn):

        """Atiende la notificacion de 'tiene un nuevo comercio'"""

        mensaje = self.get_message_nuevo_comercio()
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida Nuevo comercio')
        
        if self.is_afternoon():
            saludo = 'Buenas tardes \n'
        else:
            saludo = 'Buenos días \n'

        enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{saludo} {mensaje}'})
                    
        print(enviar_mensaje.json(), ' Mensaje nuevo comercio enviado')

    def atender_marcado_como_pagado(self,notificacion, conn):

        """Atiende la notificacion de marcado como pagado"""
        currency, receptor = self.get_atributos('currency', 'receptor')
        mensaje = self.get_message_venta_completada()

        attachment = False
        enviado = False
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
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

            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(f'Revisa {amount} en la cuenta de {receptor}')
            print(enviado_telegram, self.con_color(f' Mensaje para revisar enviado a {currency[0:2]} ')        )

    def atender_nuevo_mensaje(self, notificacion, conn):

        """Atiende un mensaje nuevo"""
        currency,receptor = self.get_atributos('currency', 'receptor')
        mensaje = self.get_message_venta_completada()

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
            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(f'Revisa {amount} en la cuenta de {receptor}')
            print(enviado_telegram, self.con_color(f' Mensaje para revisar enviado a {currency[0:2]}'))

    def escribir_log(self, fiat, btc):

        """Escribe los valores de fiat y btc al log"""

        currency, = self.get_atributos("currency")

        with open(f'logs/V-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([fiat,btc])

    def con_color(self, string):
        return Color.BLUE + string + Color.END

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

    def get_message_btc_liberados(self):
        """Devuelve el mensaje después de liberar los BTC"""
        
        mensaje = 'Liberados gracias por tu compra y por calificar. \n' \
        'Si ya calificaste ha sido un placer negociar contigo de nuevo.'
        
        return  mensaje

    def get_message_venta_completada(self):

        """Devuelve el mensaje para venta completada
            al cambiar el msj cambiar atender marcado como pagado.
        """
        
        mensaje = 'Gracias, comprobante recibido,\n '\
                'procedo a verificar el pago.'
        
        return  mensaje

    def format_time(self,sec):

        """Cambia el formato de tiempo"""

        mins = sec // 60
        sec = sec % 60
        hours = mins // 60
        mins = mins % 60
        return "Duración = {0}:{1}:{2}".format(int(hours),int(mins),round(sec,2))

    def identificar_ad_id(self, notificacion, conn):
        
        contact_id = notificacion['contact_id']
        contact_info = conn.call(method='GET', url= f'/api/contact_info/{contact_id}/')
        ad_id = contact_info.json()['data']['advertisement']['id']
        
        return str(ad_id)

    @loop
    def iniciar(self):

        sleep_time = int(self.sleep_time)

        while True:
            self.respond_notifications()
            time.sleep(sleep_time)

    def is_afternoon(self):

        """Devuelve True si es en la tarde"""
        
        return datetime.datetime.now().time() > datetime.time(12,0)

    def notification_time(self, notificacion):
        
        created_at_str = notificacion['created_at'][0:10] + ' ' + notificacion['created_at'][11:19]

        created_at = datetime.datetime.strptime(created_at_str,'%Y-%m-%d %H:%M:%S').timestamp()

        now = datetime.datetime.utcnow().timestamp()

        return now - created_at

    def respond_notifications(self):

        """Atiende las notificaciones"""

        id_ad, currency = self.get_atributos("id_ad", "currency")
        print(self.con_color(f'Revisando notificaciones...{currency[0:2]}'))
        start_time = time.time()
        conn = self.conectar()
        response = conn.call(method='GET', url='/api/notifications/')

        notificaciones = response.json()['data']

        for notificacion in notificaciones:

            if notificacion['url'][9:27] == 'online_sell_seller':

                notif_time = self.notification_time(notificacion)
        
                if not notificacion['read'] and notificacion['msg'][0:6] == '¡Tiene':

                    ad_id = self.identificar_ad_id(notificacion, conn)
                    if ad_id==id_ad:
                        self.atender_nuevo_comercio(notificacion, conn)
                    
                    continue

                if not notificacion['read'] and notificacion['msg'][0:11] == 'El contacto':
                    
                    ad_id = self.identificar_ad_id(notificacion, conn)
                    if ad_id==id_ad:
                        self.atender_marcado_como_pagado(notificacion, conn)

                    continue

                if not notificacion['read'] and notificacion['msg'][0:13] == 'Nuevo mensaje':

                    ad_id = self.identificar_ad_id(notificacion, conn)
                    if ad_id==id_ad:
                        self.atender_nuevo_mensaje(notificacion, conn)

                    continue

                if notif_time < 60 and notificacion['msg'][0:12] == 'Ha realizado':
                    
                    ad_id = self.identificar_ad_id(notificacion, conn)
                    if ad_id==id_ad:
                        self.atender_final_venta(notificacion, conn)

        end_time = time.time()
        duracion = end_time - start_time    
        print(self.format_time(duracion))

    def sendtext(self, bot_message):

        bot_token ,receptor, verificador = self.get_atributos("bot_token", "receptor","verificador")

        sergio_id = '333685986'
        persona_id = sergio_id
        if receptor != 'sergio':
            persona_id = verificador

        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + persona_id + '&parse_mode=Markdown&text=' + bot_message

        response = requests.post(send_text)

        return response.json()['ok']

class NotificadorCompra(Notificador):

    def atender_final_compra(self, notificacion, conn):
        
        mensaje = self.get_message_btc_liberados()
        currency, = self.get_atributos("currency")

        enviado = False

        contact_id = notificacion['contact_id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        
        for message in contact_messages:
            if message['msg'][0:13] == mensaje[0:13]:
                enviado = True
        
        if not enviado:
            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})        
            print(enviar_mensaje.json(), ' Mensaje Final de venta enviado')
            fiat = contact_info['amount']
            btc = float(contact_info['amount_btc']) - float(contact_info['fee_btc'])
            self.escribir_log(fiat, btc)
            print(self.con_color(f'Se escribió en el log compra de {btc} por {fiat} {currency}'))

    def atender_nuevo_comercio(self, notificacion, conn):

        """Atiende la notificacion de 'tiene un nuevo comercio'"""

        num_cuenta = False
        
        mensaje_cuenta_ident = self.get_message_cuenta_identificada()
        mensaje = self.get_message_nuevo_comercio()
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida Nuevo comercio de compra')
        
        if self.is_afternoon():
            saludo = 'Buenas tardes \n'
        else:
            saludo = 'Buenos días \n'

        for message in contact_messages:
            cuenta1 = re.search(r'\d{11}', message['msg'])
            cuenta2 = re.search(r'\d{2,6}[-\s]+\d{2,6}[-\s]+\d{2,6}[-\s]?\d*', message['msg'])
            if cuenta1:
                num_cuenta = True
                cuenta = cuenta1
            if cuenta2:
                num_cuenta = True
                cuenta = cuenta2

        if num_cuenta:

            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje_cuenta_ident}'})
            print(enviar_mensaje.json(), self.con_color(' Mensaje de cuenta identificada enviado'))
            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(f'ahoros {cuenta[0]}\n {amount}')
            print(enviado_telegram, ' Mensaje de compra enviado a telegram ')

        else:

            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{saludo} {mensaje}'})
            print(enviar_mensaje.json(), 'Compra Mensaje nuevo comercio enviado')

    def atender_nuevo_mensaje(self, notificacion, conn):

        """Atiende un mensaje nuevo"""

        mensaje = self.get_message_cuenta_identificada()

        num_cuenta = False
        enviado = False
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida nuevo mensaje o comprobante')
        
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

        if num_cuenta and not enviado:
            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})
            print(enviar_mensaje.json(), ' Mensaje de cuenta identificada enviado')

            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(f'ahoros {cuenta[0]}\n {amount}')
            print(enviado_telegram, self.con_color(' Mensaje de compra enviado a telegram '))

    def escribir_log(self, fiat, btc):

        """Escribe los valores de fiat y btc al log"""

        currency, = self.get_atributos("currency")

        with open(f'logs/C-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([fiat,btc])

    def get_message_btc_liberados(self):

        """Devuelve el mensaje después de comprar los BTC"""
        
        mensaje = 'Gracias agradezco tu calificación, procedo a hacer lo mismo.'
        
        return  mensaje

    def get_message_cuenta_identificada(self):

        """Devuelve el mensaje cuando identifica la cuenta a consignar"""

        return 'Procedo teniendo en cuenta que has leido los terminos del comercio'

    def get_message_nuevo_comercio(self):
        
        """Devuelve el mensaje para nuevo comercio"""

        return 'Hola cuales son los datos de cuenta para transferir?'

    def respond_notifications(self):

    
        """Atiende las notificaciones"""

        id_ad, currency = self.get_atributos("id_ad", "currency")
        print(self.con_color(f'Revisando notificaciones...{currency[0:2]}'))
        start_time = time.time()
        conn = self.conectar()
        response = conn.call(method='GET', url='/api/notifications/')

        notificaciones = response.json()['data']

        for notificacion in notificaciones:
                                            
            if notificacion['url'][32:48] == 'online_buy_buyer':

                notif_time = self.notification_time(notificacion)
        
                if not notificacion['read'] and notificacion['msg'][0:6] == '¡Tiene':

                    ad_id = self.identificar_ad_id(notificacion, conn)
                    if ad_id==id_ad:
                        self.atender_nuevo_comercio(notificacion, conn)
                    
                    continue

                if not notificacion['read'] and notificacion['msg'][0:13] == 'Nuevo mensaje':

                    ad_id = self.identificar_ad_id(notificacion, conn)
                    if ad_id==id_ad:
                        self.atender_nuevo_mensaje(notificacion, conn)

                    continue

                if notif_time < 120 and notificacion['msg'][0:12] == 'Ha realizado':

                    ad_id = self.identificar_ad_id(notificacion, conn)
                    if ad_id==id_ad:
                        self.atender_final_compra(notificacion, conn)

        end_time = time.time()
        duracion = end_time - start_time    
        print(self.format_time(duracion))

    def sendtext(self, bot_message):

        bot_token, verificador = self.get_atributos("bot_token","verificador")
        persona_id = verificador

        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + persona_id + '&parse_mode=Markdown&text=' + bot_message

        response = requests.post(send_text)

        return response.json()['ok']

class NotificadorCompraCostaRica(NotificadorCompra):

    def atender_nuevo_comercio(self, notificacion, conn):

        """Atiende la notificacion de 'tiene un nuevo comercio'"""

        num_cuenta = False
        
        mensaje_cuenta_ident = self.get_message_cuenta_identificada()
        mensaje = self.get_message_nuevo_comercio()
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida Nuevo comercio de compra')
        
        if self.is_afternoon():
            saludo = 'Buenas tardes \n'
        else:
            saludo = 'Buenos días \n'

        cuenta1 = ''
        cuenta2 = ''
        cuenta3 = ''

        for message in contact_messages:
            sinpe = re.search(r'\D\D\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d\s\D', message['msg'])
            iban = re.search(r'CR([-\s]?\d{4}){5}', message['msg'])
            bac = re.search(r'\D\D\d[-\s]?\d[-\s]?d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d\s\D', message['msg'])

            if sinpe:
                num_cuenta = True
                cuenta1 = 'SINPE ' + sinpe[0]
            if iban:
                num_cuenta = True
                cuenta2 = 'IBAN ' + iban[0]
            if bac:
                num_cuenta = True
                cuenta3 = 'BAC ' + bac[0]

        if num_cuenta:

            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje_cuenta_ident}'})
            print(enviar_mensaje.json(), self.con_color(' Mensaje de cuenta identificada enviado'))
            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}')
            print(enviado_telegram, ' Mensaje de compra enviado a telegram ')

        else:

            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{saludo} {mensaje}'})
            print(enviar_mensaje.json(), 'Compra Mensaje nuevo comercio enviado')

    def atender_nuevo_mensaje(self, notificacion, conn):

        """Atiende un mensaje nuevo"""

        mensaje = self.get_message_cuenta_identificada()

        num_cuenta = False
        enviado = False
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida nuevo mensaje o comprobante')

        cuenta1 = ''
        cuenta2 = ''
        cuenta3 = ''
        
        for message in contact_messages:
            if message['msg'][0:4] == mensaje[0:4]:
                enviado = True
            sinpe = re.search(r'\D\D\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d\s\D', message['msg'])
            iban = re.search(r'CR([-\s]?\d{4}){5}', message['msg'])
            bac = re.search(r'(\d[-\s]?){9}', message['msg'])

            if sinpe:
                num_cuenta = True
                cuenta1 = 'SINPE ' + sinpe[0]
            if iban:
                num_cuenta = True
                cuenta2 = 'IBAN ' + iban[0]
            if bac:
                num_cuenta = True
                cuenta3 = 'BAC ' + bac[0]

        if num_cuenta and not enviado:
            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})
            print(enviar_mensaje.json(), ' Mensaje de cuenta identificada enviado')

            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}')
            print(enviado_telegram, self.con_color(' Mensaje de compra enviado a telegram '))