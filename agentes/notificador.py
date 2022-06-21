from decoradores.loop import loop
from .conectar import Connection
from utils.color import Color
from bs4 import BeautifulSoup

import csv
import datetime
import os
import re
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
            print(enviar_mensaje.json(), ' Mensaje Final de venta enviado', flush=True)
            fiat = contact_info['amount']
            btc = round(float(contact_info['amount_btc']) + float(contact_info['fee_btc']),8)
            self.leer_log(btc, fiat)
            print(self.con_color(f'Se escribió en el log venta de {btc} por {fiat} {currency}'), flush=True)

    def atender_nuevo_comercio(self, notificacion, conn):

        """Atiende la notificacion de 'tiene un nuevo comercio'"""

        mensaje = self.get_message_nuevo_comercio()
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida Nuevo comercio', flush=True)
        
        if self.is_afternoon():
            saludo = 'Buenas tardes \n'
        else:
            saludo = 'Buenos días \n'

        enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{saludo} {mensaje}'})
                    
        print(enviar_mensaje.json(), ' Mensaje nuevo comercio enviado', flush=True)

    def atender_marcado_como_pagado(self,notificacion, conn):

        """Atiende la notificacion de marcado como pagado"""
        administrador, currency, receptor,verificador = self.get_atributos('administrador','currency', 'receptor','verificador')
        mensaje = self.get_message_venta_completada()

        attachment = False
        enviado = False
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        nombre_de_local = contact_info['buyer']['real_name']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida marcado como pagado', flush=True)

        for message in contact_messages:
            if 'attachment_type' in message:
                attachment = True

            if message['msg'][0:13] == mensaje[0:13]:
                enviado = True

        if attachment and not enviado:
            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})
            print(enviar_mensaje.json(), ' Mensaje de venta completada enviado', flush=True)

            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(verificador,f'Revisa {amount} en la cuenta de {str(receptor).upper()}\n{nombre_de_local}')
            self.sendtext(administrador, f'Revisa {amount} en la cuenta de {str(receptor).upper()}\n{nombre_de_local}')
            print(enviado_telegram, self.con_color(f' Mensaje para revisar enviado a {currency[0:2]} '), flush=True)

    def atender_nuevo_mensaje(self, notificacion, conn):

        """Atiende un mensaje nuevo"""
        administrador, currency,receptor,verificador = self.get_atributos('administrador','currency', 'receptor','verificador')
        mensaje = self.get_message_venta_completada()

        attachment = False
        payed = False
        enviado = False
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        nombre_de_local = contact_info['buyer']['real_name']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida nuevo mensaje o comprobante', flush=True)

        for message in contact_messages:
            if 'attachment_type' in message:
                attachment = True
            if message['msg'][0:13] == mensaje[0:13]:
                enviado = True
                                
        if contact_info['payment_completed_at'] is not None:
            payed = True
                        
        if attachment and payed and not enviado:
            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})
            print(enviar_mensaje.json(), ' Mensaje de venta completada enviado', flush=True)
            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(verificador, f'Revisa {amount} en la cuenta de {str(receptor).upper()}\n{nombre_de_local}')
            self.sendtext(administrador, f'Revisa {amount} en la cuenta de {str(receptor).upper()}\n{nombre_de_local}')
            print(enviado_telegram, self.con_color(f' Mensaje para revisar enviado a {currency[0:2]}'), flush=True)

    def escribir_log(self, btc, fiat):

        """Escribe los valores de fiat y btc al log"""

        currency, bot_token = self.get_atributos("currency", "bot_token")

        t='V'
 
        with open(f'logs/{t}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', 'a', newline='') as f:
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
        
        mensaje = 'Liberados, excelente día' # racias por tu compra y por calificar. \n Si ya calificaste ha sido un placer negociar contigo de nuevo.'
        
        return  mensaje

    def get_message_venta_completada(self):

        """Devuelve el mensaje para venta completada
            al cambiar el msj cambiar atender marcado como pagado.
        """
        
        mensaje = 'Gracias, comprobante recibido,\n '\
                'procedo a verificar el pago.'
        
        return  mensaje

    def get_precio_de_cambio(self, currency):

        page = requests.get(f'https://www.x-rates.com/calculator/?from={currency}&to=COP&amount=1')
        soup = BeautifulSoup(page.text, 'html.parser')

        part1 = soup.find(class_="ccOutputTrail").previous_sibling
        part2 = soup.find(class_="ccOutputTrail").get_text(strip=True)
        rate = f"{part1}{part2}"

        return rate

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

    def leer_log(self, btc, fiat):

        """Lee los valores del log"""

        currency, administrador = self.get_atributos("currency", "administrador")

        t='V'
        encontrado = False
        if os.path.isfile(f'logs/{t}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv'):
            with open(f'logs/{t}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if float(btc) == float(row[1]):
                        encontrado = True

        if not encontrado:
            self.escribir_log(btc, fiat)
            self.sendtext(administrador,f'Se escribio en log de venta {currency}, {btc}, {fiat}')

    def notification_time(self, notificacion):
        
        created_at_str = notificacion['created_at'][0:10] + ' ' + notificacion['created_at'][11:19]

        created_at = datetime.datetime.strptime(created_at_str,'%Y-%m-%d %H:%M:%S').timestamp()

        now = datetime.datetime.utcnow().timestamp()

        return now - created_at

    def respond_notifications(self):

        """Atiende las notificaciones"""

        id_ad, currency = self.get_atributos("id_ad", "currency")
        print(self.con_color(f'Revisando notificaciones...{currency[0:2]}'), flush=True)
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

                if notif_time < 150 and notificacion['msg'][0:12] == 'Ha realizado':
                    
                    ad_id = self.identificar_ad_id(notificacion, conn)
                    if ad_id==id_ad:
                        self.atender_final_venta(notificacion, conn)

        end_time = time.time()
        duracion = end_time - start_time    
        print(self.format_time(duracion), flush=True)

    def sendtext(self, receptor, bot_message):

        bot_token, enviar_mensaje = self.get_atributos("bot_token", "enviar_mensaje")
        if enviar_mensaje:
            send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + receptor + '&parse_mode=Markdown&text=' + bot_message
            response = requests.post(send_text)
            
            return response.json()['ok']

        else:
            return 'Envio de mensajes desactivado'

class NotificadorCompra(Notificador):

    """Para mexico estamos comprand en colombia entonces para 'MXN se hace una conversion en el log"""
    def __init__(self, bot_token, currency, id_ad, key, secret, sleep_time, receptor, receptores, verificador, administrador, enviar_mensaje, verificador2,  currency_venta):
        super().__init__(bot_token, currency, id_ad, key, secret, sleep_time, receptor, receptores, verificador,administrador, enviar_mensaje, verificador2)
        self.currency_venta = currency_venta

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
            print(enviar_mensaje.json(), ' Mensaje Final de venta enviado', flush=True)
            fiat = contact_info['amount']
            btc = round(float(contact_info['amount_btc']) - float(contact_info['fee_btc']),8)
            self.leer_log(btc, fiat)
            print(self.con_color(f'Se escribió en el log compra de {btc} por {fiat} {currency}'), flush=True)

    def atender_nuevo_comercio(self, notificacion, conn):

        """Atiende la notificacion de 'tiene un nuevo comercio'"""

        administrador, verificador, verificador2 = self.get_atributos("administrador", "verificador","verificador2")


        num_cuenta = False
        
        mensaje_cuenta_ident = self.get_message_cuenta_identificada()
        mensaje = self.get_message_nuevo_comercio()
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida Nuevo comercio de compra', flush=True)
        
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
            print(enviar_mensaje.json(), self.con_color(' Mensaje de cuenta identificada enviado'), flush=True)
            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(verificador , f'ahoros {cuenta[0]}\n {amount}')
            self.sendtext(administrador , f'ahoros {cuenta[0]}\n {amount}')
            self.sendtext(verificador2 , f'ahoros {cuenta[0]}\n {amount}')
            print(enviado_telegram, ' Mensaje de compra enviado a telegram ', flush=True)

        else:

            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{saludo} {mensaje}'})
            print(enviar_mensaje.json(), 'Compra Mensaje nuevo comercio enviado', flush=True)

    def atender_nuevo_mensaje(self, notificacion, conn):

        """Atiende un mensaje nuevo"""

        administrador, verificador,verificador2 = self.get_atributos("administrador", "verificador", "verificador2")


        mensaje = self.get_message_cuenta_identificada()

        num_cuenta = False
        enviado = False
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida nuevo mensaje o comprobante', flush=True)
        
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
            print(enviar_mensaje.json(), ' Mensaje de cuenta identificada enviado', flush=True)

            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(verificador , f'ahoros {cuenta[0]}\n {amount}')
            self.sendtext(administrador , f'ahoros {cuenta[0]}\n {amount}')
            self.sendtext(verificador2 , f'ahoros {cuenta[0]}\n {amount}')
            print(enviado_telegram, self.con_color(' Mensaje de compra enviado a telegram '), flush=True)

    def escribir_log(self, btc, fiat):

        """Escribe los valores de fiat y btc al log
        si es compra de pesos colombianos, se supone qe es para mex y escribe una
        tercera columna con los cop"""

        administrador, currency, currency_venta  = self.get_atributos("administrador", "currency", "currency_venta")

        if not os.path.isfile(f'logs/C-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv'):
            fiat_saldo_dia_anterior , btc_saldo_dia_anterior = self.get_saldo_dia_anterior()
            with open(f'logs/C-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([fiat_saldo_dia_anterior,btc_saldo_dia_anterior])
        
        if currency == 'COP':
            p_c = self.get_precio_de_cambio(currency_venta)
            fiat2 = float(fiat) / float(p_c)
            with open(f'logs/C-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([fiat2,btc,fiat,currency_venta])
                self.sendtext(administrador, f'se escribio en log de compra {currency}, {btc}, {fiat} para venta en {currency_venta} ')

        else:

            with open(f'logs/C-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([fiat,btc])
                self.sendtext(administrador, f'se escribio en log de de compra {currency}, {btc}, {fiat} para venta en {currency_venta}')

    def get_saldo_dia_anterior(self):
        """Lee y retorna los valores totales de btc sin vender del dia anterior"""
        currency, currency_venta = self.get_atributos("currency", "currency_venta")

        for td in range(1,31):
            total_btc_compra = 0
            if os.path.isfile(f'logs/C-{currency[0:2]}-{str(datetime.datetime.now().date()-datetime.timedelta(days=td))}.csv'):
                with open(f'logs/C-{currency[0:2]}-{str(datetime.datetime.now().date()-datetime.timedelta(days=td))}.csv', newline='') as f:
                    reader = csv.reader(f)
                    if currency == 'COP':
                        for row in reader:
                            if row[3] == currency_venta:
                                total_btc_compra += float(row[1])
                    else:
                        for row in reader:
                            total_btc_compra += float(row[1])

            total_btc_venta = 0
            if os.path.isfile(f'logs/V-{currency_venta[0:2]}-{str(datetime.datetime.now().date()-datetime.timedelta(days=td))}.csv'):
                with open(f'logs/V-{currency_venta[0:2]}-{str(datetime.datetime.now().date()-datetime.timedelta(days=td))}.csv', newline='') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        total_btc_venta += float(row[1])

            precio_de_compra_dia_anterior = 0
            if os.path.isfile(f'logs/C-{currency[0:2]}-{str(datetime.datetime.now().date()-datetime.timedelta(days=td))}.csv'):
                with open(f'logs/C-{currency[0:2]}-{str(datetime.datetime.now().date()-datetime.timedelta(days=td))}.csv', newline='') as f:
                    reader = csv.reader(f)
                    if currency == 'COP':
                        for row in reader:
                            if float(row[1]) != 0:
                                if row[3] == currency_venta:
                                    precio = float(row[0])/float(row[1])
                                    peso = float(row[1]) / total_btc_compra
                                    precio_de_compra_dia_anterior += precio * peso
                    
                    else:
                        for row in reader:
                            if float(row[1]) != 0:
                                    precio = float(row[0])/float(row[1])
                                    peso = float(row[1]) / total_btc_compra
                                    precio_de_compra_dia_anterior += precio * peso
                
                break

        total_btc = total_btc_compra - total_btc_venta
        total_fiat = total_btc * precio_de_compra_dia_anterior
        
        return (round(total_fiat,2), round(total_btc,8)) if total_btc > 0.00007 else (0 , 0)

    def get_message_btc_liberados(self):

        """Devuelve el mensaje después de comprar los BTC"""
        
        mensaje = 'Agradezco tu calificación, procedo a hacer lo mismo. Si ya calificaste fue un placer hacer negocios contigo de nuevo'
        
        return  mensaje

    def get_message_cuenta_identificada(self):

        """Devuelve el mensaje cuando identifica la cuenta a consignar"""

        return 'Procedo teniendo en cuenta que has leido los terminos del comercio'\
            '\n/I proceed on the basis that you have read the terms of trade.'

    def get_message_nuevo_comercio(self):
        
        """Devuelve el mensaje para nuevo comercio"""

        return 'Hola cuales son los datos de cuenta para transferir?'\
            '\nHello, which is the account to transfer?'

    def leer_log(self,btc, fiat):

        """Lee los valores del log"""

        currency, currency_venta = self.get_atributos("currency", "currency_venta")

        t='C'

        encontrado = False
        if os.path.isfile(f'logs/{t}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv'):
            with open(f'logs/{t}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if float(btc) == float(row[1]):
                        encontrado = True

        if not encontrado:
            self.escribir_log(btc, fiat)

    def respond_notifications(self):

    
        """Atiende las notificaciones"""

        id_ad, currency = self.get_atributos("id_ad", "currency")
        print(self.con_color(f'Revisando notificaciones...{currency[0:2]}'), flush=True)
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

                if notif_time < 240 and notificacion['msg'][0:12] == 'Ha realizado':

                    ad_id = self.identificar_ad_id(notificacion, conn)
                    if ad_id==id_ad:
                        self.atender_final_compra(notificacion, conn)

        end_time = time.time()
        duracion = end_time - start_time    
        print(self.format_time(duracion), flush=True)

class NotificadorVentaCostaRica(Notificador):

    def atender_nuevo_comercio(self, notificacion, conn):

        """Atiende la notificacion de 'tiene un nuevo comercio'"""

        mensaje = self.get_message_nuevo_comercio()
        contact_id = notificacion['contact_id']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        if contact_info['buyer']['username'] in ['josedmarin','Djpb0102', 'camedina11', 'elissakmd', 'Ricardo8830', 'EileenArguedasM', 'Ricardo8830', 'ailak', 'grios14', 'cris_sulbaran','nazuaje','ERNESTONE','jevale310879','Andréssanchez20','Hugobttx']:
            mensaje = self.get_despues_de_aceptado()
            
        notification_id = notificacion['id']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida Nuevo comercio', flush=True)
        
        if self.is_afternoon():
            saludo = 'Buenas tardes \n'
        else:
            saludo = 'Buenos días \n'

        enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{saludo} {mensaje}'})
                    
        print(enviar_mensaje.json(), ' Mensaje nuevo comercio enviado', flush=True)

    def get_despues_de_aceptado(self):
        
        receptor, receptores = self.get_atributos("receptor","receptores")

        """Devuelve el mensaje para nuevo comercio"""

        return receptores[receptor]

    def get_message_nuevo_comercio(self):

        mensaje = 'NO SE ADMITEN TRANSFERENCIAS DE TERCEROS\n\n'\
                    'El nombre del titular de la transferencia debe coincidir\n '\
                    'con el titular de la cuenta de localbitcoins para liberar los btc.\n\n'\
                    'Si vas a hacer una remesa \n '\
                    'y tu cuenta de localbitcoins no coincide con\n '\
                    'la cuenta que transfiere el dinero,\n '\
                    'debes enviar una prueba, foto o video de la persona titular de la cuenta\n '\
                    'sosteniendo su cedula y donde se muestre la fecha de hoy y \n '\
                    'diga transferencia de btc a sromero.\n\n '\
                    "Si aceptas los terminos y quieres continuar envia un mensaje diciendo 'Si'\n"\
                    'para enviarte los datos de la cuenta.'

        return mensaje

    def atender_nuevo_mensaje(self, notificacion, conn):

        """Atiende un mensaje nuevo"""
        administrador, currency,receptor, verificador = self.get_atributos('administrador','currency', 'receptor','verificador')

        aceptado = False
        attachment = False
        enviado = False
        enviado_despues_de_aceptado = False
        payed = False
        
        mensaje = self.get_message_venta_completada()
        mensaje_despues_de_aceptado = self.get_despues_de_aceptado()

        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        nombre_de_local = contact_info['buyer']['real_name']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida nuevo mensaje o comprobante', flush=True)

        for message in contact_messages:
            if 'attachment_type' in message:
                attachment = True
            if message['msg'][0:13] == mensaje[0:13]:
                enviado = True
            if message['msg'][-4:] == mensaje_despues_de_aceptado[-4:]:
                enviado_despues_de_aceptado = True
            if 'si' in message['msg'].lower() or 'ok' in message['msg'].lower():
                aceptado = True
                                
        if contact_info['payment_completed_at'] is not None:
            payed = True

        if aceptado and not enviado_despues_de_aceptado:
            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje_despues_de_aceptado}'})
            print(enviar_mensaje.json(), ' Mensaje de cuenta enviado', flush=True)
                        
        if attachment and payed and not enviado:
            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})
            print(enviar_mensaje.json(), ' Mensaje de venta completada enviado', flush=True)
            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(verificador, f'Revisa {amount} en la cuenta de {str(receptor).upper()}\n{nombre_de_local}')
            self.sendtext(administrador, f'Revisa {amount} en la cuenta de {str(receptor).upper()}\n{nombre_de_local}')
            print(enviado_telegram, self.con_color(f' Mensaje para revisar enviado a {currency[0:2]}'), flush=True)

class NotificadorCompraCostaRica(NotificadorCompra):

    def atender_nuevo_comercio(self, notificacion, conn):

        """Atiende la notificacion de 'tiene un nuevo comercio'"""

        administrador, verificador, verificador2 = self.get_atributos("administrador", "verificador", "verificador2")

        num_cuenta = False
        
        mensaje_cuenta_ident = self.get_message_cuenta_identificada()
        mensaje = self.get_message_nuevo_comercio()
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        nombre_de_local = contact_info['seller']['username']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida Nuevo comercio de compra', flush=True)
        
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
            print(enviar_mensaje.json(), self.con_color(' Mensaje de cuenta identificada enviado'), flush=True)
            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(verificador, f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}\n{nombre_de_local}')
            self.sendtext(administrador, f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}\n{nombre_de_local}')
            self.sendtext(verificador2, f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}\n{nombre_de_local}')

            for msj in contact_messages:
                self.sendtext(administrador,msj['msg'])
                self.sendtext(verificador,msj['msg'])
                self.sendtext(verificador2,msj['msg'])


            print(enviado_telegram, ' Mensaje de compra enviado a telegram ', flush=True)

        else:

            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{saludo} {mensaje}'})
            print(enviar_mensaje.json(), 'Compra Mensaje nuevo comercio enviado', flush=True)

    def atender_nuevo_mensaje(self, notificacion, conn):

        """Atiende un mensaje nuevo"""

        administrador, verificador,verificador2 = self.get_atributos("administrador", "verificador","verificador2")

        mensaje = self.get_message_cuenta_identificada()

        num_cuenta = False
        enviado = False
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        nombre_de_local = contact_info['seller']['username']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida nuevo mensaje o comprobante', flush=True)

        cuenta1 = ''
        cuenta2 = ''
        cuenta3 = ''
        
        for message in contact_messages:
            if message['msg'][0:4] == mensaje[0:4]:
                enviado = True
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

        if num_cuenta and not enviado:
            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})
            print(enviar_mensaje.json(), ' Mensaje de cuenta identificada enviado', flush=True)

            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(verificador, f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}\n{nombre_de_local} ')
            self.sendtext(administrador, f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}\n{nombre_de_local} ')
            self.sendtext(verificador2, f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}\n{nombre_de_local} ')


            print(enviado_telegram, self.con_color(' Mensaje de compra enviado a telegram '), flush=True)

class NotificadorCompraTether(NotificadorCompra):

    def atender_nuevo_comercio(self, notificacion, conn):

        """Atiende la notificacion de 'tiene un nuevo comercio'"""

        administrador, verificador,verificador2 = self.get_atributos("administrador", "verificador","verificador2")

        num_cuenta = False
        
        mensaje_cuenta_ident = self.get_message_cuenta_identificada()
        mensaje = self.get_message_nuevo_comercio()
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida Nuevo comercio de compra', flush=True)
        
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
            print(enviar_mensaje.json(), self.con_color(' Mensaje de cuenta identificada enviado'), flush=True)
            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(verificador, f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}')
            self.sendtext(administrador, f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}')
            self.sendtext(verificador2, f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}')

            print(enviado_telegram, ' Mensaje de compra enviado a telegram ', flush=True)

        else:

            enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{saludo} {mensaje}'})
            print(enviar_mensaje.json(), 'Compra Mensaje nuevo comercio enviado', flush=True)

    def atender_nuevo_mensaje(self, notificacion, conn):

        """Atiende un mensaje nuevo"""

        administrador, verificador,verificador2 = self.get_atributos("administrador", "verificador","verificador2")

        mensaje = self.get_message_cuenta_identificada()

        num_cuenta = False
        enviado = False
        contact_id = notificacion['contact_id']
        notification_id = notificacion['id']
        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']
        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), ' Notif leida nuevo mensaje o comprobante', flush=True)

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
            print(enviar_mensaje.json(), ' Mensaje de cuenta identificada enviado', flush=True)

            amount = contact_info['amount'] + ' ' + contact_info['currency']
            enviado_telegram = self.sendtext(verificador, f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}')
            self.sendtext(administrador, f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}')
            self.sendtext(verificador2, f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{cuenta3}')
            print(enviado_telegram, self.con_color(' Mensaje de compra enviado a telegram '), flush=True)