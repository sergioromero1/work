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

    def atender_final_de_comercio(self, notificacion, conn, tipo):

        """Actua después de que sean liberados los btc,
            envia un mensaje al cliente y escribe en el log
        """
        mensaje_btc_liberados = self.get_message_btc_liberados()

        enviado = False

        contact_id = notificacion['contact_id']
        contact_messages = self.get_contact_messages(conn, contact_id)
        for message in contact_messages:
            if message['msg'][0:13] == mensaje_btc_liberados[0:13]:
                enviado = True
        
        if not enviado:
            self.send_msg_contact(conn,contact_id, mensaje_btc_liberados, f'Mensaje Final de venta enviado #{contact_id}',verbose=True)
            
            contact_info = self.get_contact_info(conn, contact_id)
            fiat = contact_info['amount']
            if tipo == 'venta':
                btc = round(float(contact_info['amount_btc']) + float(contact_info['fee_btc']),8)
            if tipo == 'compra':
                btc = round(float(contact_info['amount_btc']) - float(contact_info['fee_btc']),8)

            encontrado = self.revisar_valores_en_log(btc,fiat,tipo=tipo)
            if not encontrado:
                self.escribir_log(btc, fiat,tipo=tipo)

    def atender_nuevo_comercio(self, notificacion, conn):

        """Atiende la notificacion de 'tiene un nuevo comercio'"""

        mensaje_nuevo_comercio = self.get_message_nuevo_comercio()

        contact_id = notificacion['contact_id']

        self.marcar_notificacion_como_leida(conn,notificacion,f'Nuevo comercio #{contact_id}')

        self.send_msg_contact(conn,contact_id, mensaje_nuevo_comercio, f'Mensaje nuevo comercio enviado #{contact_id}',verbose=True)

    def atender_marcado_como_pagado(self,notificacion, conn):

        """Atiende la notificacion de marcado como pagado"""
        administrador, receptor,verificador, verificador2 = self.get_atributos('administrador', 'receptor','verificador','verificador2')
        mensaje_de_venta_completada = self.get_message_venta_completada()

        attachment = False
        enviado = False
        contact_id = notificacion['contact_id']

        self.marcar_notificacion_como_leida(conn,notificacion,descripcion=f'contacto marcado como pagado #{contact_id}')

        contact_messages = self.get_contact_messages(conn, contact_id)
        for message in contact_messages:
            if 'attachment_type' in message:
                attachment = True

            if message['msg'][0:13] == mensaje_de_venta_completada[0:13]:
                enviado = True

        if attachment and not enviado:
            contact_info = self.get_contact_info(conn, contact_id)
            nombre_de_local = contact_info['buyer']['real_name']
            self.send_msg_contact(conn,contact_id, mensaje_de_venta_completada, f'Mensaje de venta completada enviado #{contact_id}',verbose=True)

            amount = contact_info['amount'] + ' ' + contact_info['currency']

            self.send_text([verificador, administrador, verificador2],f'Revisa {amount} en la cuenta de {str(receptor).upper()}\n{nombre_de_local}',verbose=True)

    def atender_nuevo_mensaje(self, notificacion, conn):

        """Atiende un mensaje nuevo"""
        administrador,receptor,verificador,verificador2 = self.get_atributos('administrador','receptor','verificador', 'verificador2')
        mensaje_de_venta_completada = self.get_message_venta_completada()

        attachment = False
        payed = False
        enviado = False
        contact_id = notificacion['contact_id']
        
        self.marcar_notificacion_como_leida(conn,notificacion,descripcion=f'Nuevo mensaje o comprobante #{contact_id}')

        contact_messages = self.get_contact_messages(conn, contact_id)
        for message in contact_messages:
            if 'attachment_type' in message:
                attachment = True
            if message['msg'][0:13] == mensaje_de_venta_completada[0:13]:
                enviado = True

        contact_info = self.get_contact_info(conn, contact_id)
        if contact_info['payment_completed_at'] is not None:
            payed = True
                        
        if attachment and payed and not enviado:
            nombre_de_local = contact_info['buyer']['real_name']
            self.send_msg_contact(conn,contact_id, mensaje_de_venta_completada, f'Mensaje de venta completada enviado #{contact_id}',verbose=True)

            amount = contact_info['amount'] + ' ' + contact_info['currency']

            self.send_text([verificador,administrador,verificador2], f'Revisa {amount} en la cuenta de {str(receptor).upper()}\n{nombre_de_local}',verbose=True)

    def escribir_log(self, btc, fiat, tipo):

        """Escribe los valores de fiat y btc al log de VENTA"""

        currency, administrador = self.get_atributos("currency", "administrador")
 
        with open(f'logs/{tipo.upper()[0]}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([fiat,btc])
            self.send_text([administrador],f'Se escribio en log de {tipo} {currency}, {btc}, {fiat}',verbose=True)
        
    def con_color(self, string):
        return Color.BLUE + string + Color.END

    def conectar(self,server='https://localbitcoins.com'):

        """Se conecta a local bitcoins"""

        key, secret = self.get_atributos("key", "secret")
        conn = Connection()
        conn._set_hmac(server, key, secret)
        
        return conn

    def get_contact_messages(self,conn, contact_id):

        contact_messages = conn.call(method='GET', url=f'/api/contact_messages/{contact_id}/').json()['data']['message_list']

        return contact_messages

    def get_contact_info(self,conn,contact_id):

        contact_info = conn.call(method='GET', url=f'/api/contact_info/{contact_id}/').json()['data']

        return contact_info

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
        contact_info = self.get_contact_info(conn, contact_id)
        ad_id = contact_info['advertisement']['id']
        
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

    def marcar_notificacion_como_leida(self,conn, notificacion, descripcion):

        notification_id = notificacion['id']
        marcar_como_leida = conn.call(method='POST', url= f'/api/notifications/mark_as_read/{notification_id}/')
        print(marcar_como_leida.json(), f' Notif leida de {descripcion}', flush=True)

    def respond_notifications(self):

        """Atiende las notificaciones"""

        id_ad, currency = self.get_atributos("id_ad", "currency")
        # print(self.con_color(f'Revisando notificaciones...{currency[0:2]}'), flush=True)
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
                        self.atender_final_de_comercio(notificacion, conn, tipo='venta')

        end_time = time.time()
        duracion = end_time - start_time    
        # print(self.format_time(duracion), flush=True)

    def revisar_valores_en_log(self,btc,fiat,tipo):

        currency,  = self.get_atributos("currency")

        encontrado = False
        if os.path.isfile(f'logs/{tipo.upper()[0]}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv'):
            with open(f'logs/{tipo.upper()[0]}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if float(btc) == float(row[1]):
                        encontrado = True

        return encontrado

    def send_msg_contact(self,conn, contact_id, mensaje, descripcion, verbose=False):

        """Envia un mensaje a un contact_id"""
        
        enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/{contact_id}/', params={'msg': f'{mensaje}'})

        if verbose == True:
            print(enviar_mensaje.json(), f'{descripcion}', flush=True)

    def send_text(self, receptores, bot_message, verbose=False):

        """Envia un mensaje a a la lista 'receptores' en telegram"""

        bot_token, enviar_mensaje = self.get_atributos("bot_token", "enviar_mensaje")

        if enviar_mensaje:
            for receptor in receptores:
                send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + receptor + '&parse_mode=Markdown&text=' + bot_message
                response = requests.post(send_text)
            if verbose == True:
                print(bot_message, flush=True)

        else:
            print('Envio de mensajes desactivado')

class NotificadorCompra(Notificador):

    """Para mexico estamos comprand en colombia entonces para 'MXN se hace una conversion en el log"""
    def __init__(self, bot_token, currency, id_ad, key, secret, sleep_time, receptor, receptores, verificador, administrador, enviar_mensaje, verificador2,  currency_venta, expresiones_regex):
        super().__init__(bot_token, currency, id_ad, key, secret, sleep_time, receptor, receptores, verificador,administrador, enviar_mensaje, verificador2)
        self.currency_venta = currency_venta
        self.expresiones_regex = expresiones_regex

    def identificar_cuenta(self,notificacion,conn):

        """
        Identifica si hay o no en los mensajes un numero de 
        cuenta para enviar dinero.
        Identifica tambien si ya se envio el msj de 
        cuenta identificada.
        """
        reg_exp, = self.get_atributos("expresiones_regex")
        
        num_cuenta = False

        enviado = False

        mensaje_cuenta_ident = self.get_message_cuenta_identificada()
        
        contact_id = notificacion['contact_id']

        contact_messages = self.get_contact_messages(conn, contact_id)
        
        cuenta1 = ''
        cuenta2 = ''

        for message in contact_messages:
            if message['msg'][0:4] == mensaje_cuenta_ident[0:4]:
                enviado = True
            digit = re.search(r'\d', message['msg'])
            cuenta_uno = re.search(reg_exp[0], message['msg'])
            cuenta_dos = re.search(reg_exp[1], message['msg'])

            if digit:
                num_cuenta = True
            if cuenta_uno:
                cuenta1 = cuenta_uno[0]
            if cuenta_dos:
                cuenta2 = cuenta_dos[0]

        return num_cuenta,cuenta1,cuenta2,enviado

    def notificar_cuenta_identificada(self,notificacion,conn,cuenta1,cuenta2):

        """
        Envía notificacion por telegram una vez
        se le pasan los datos encontrados en 
        self.identificar_cuenta()
        """

        administrador, verificador, verificador2 = self.get_atributos("administrador", "verificador", "verificador2")

        mensaje_cuenta_ident = self.get_message_cuenta_identificada()

        contact_id = notificacion['contact_id']

        contact_info = self.get_contact_info(conn, contact_id)

        self.send_msg_contact(conn,contact_id, mensaje_cuenta_ident, f'Mensaje de cuenta identificada enviado #{contact_id}',verbose=True)

        nombre_de_local = contact_info['seller']['username']
        amount = contact_info['amount'] + ' ' + contact_info['currency']

        self.send_text([verificador, administrador,verificador2], f'Envia {amount} a:\n{cuenta1}\n{cuenta2}\n{nombre_de_local}',verbose=True)

        contact_messages = self.get_contact_messages(conn, contact_id)

        for msj in contact_messages:
            if msj['msg'][0:4] != mensaje_cuenta_ident[0:4]:
                self.send_text([verificador, administrador,verificador2],msj['msg'])
  
    def atender_nuevo_comercio(self, notificacion, conn):

        """
        Atiende la notificacion de 'tiene un nuevo comercio'
        revisa si estan los datos en los mensajes.
        Si están, los envia a telegram.
        Si no envia un msj al cliente solicitandolos.
        """

        time.sleep(10)

        self.marcar_notificacion_como_leida(conn,notificacion,descripcion='Nuevo comercio')

        mensaje_solicitando_datos = self.get_message_nuevo_comercio()

        contact_id = notificacion['contact_id']
        
        num_cuenta, cuenta1, cuenta2,_ = self.identificar_cuenta(notificacion,conn)

        if num_cuenta:

            self.notificar_cuenta_identificada(notificacion, conn,cuenta1,cuenta2)

        else:
            self.send_msg_contact(conn,contact_id, mensaje_solicitando_datos, f'Mensaje nuevo comercio de compra enviado #{contact_id}',verbose=True)

    def atender_nuevo_mensaje(self, notificacion, conn):

        """Atiende un mensaje nuevo"""

        """
        Atiende un nuevo mensaje,
        si el cliente envio los datos y estos no se han notificado, los envía.
        """

        self.marcar_notificacion_como_leida(conn,notificacion,descripcion='Nuevo mensaje')

        num_cuenta, cuenta1, cuenta2, enviado = self.identificar_cuenta(notificacion,conn)

        if num_cuenta and not enviado:

            self.notificar_cuenta_identificada(notificacion, conn,cuenta1,cuenta2)

    def escribir_log(self, btc, fiat, tipo):

        """Escribe los valores de fiat y btc al log de COMPRA
        si es compra de pesos colombianos, se supone qe es para mex y escribe una
        tercera columna con los cop"""

        administrador, currency, currency_venta  = self.get_atributos("administrador", "currency", "currency_venta")

        log_file = f'logs/{tipo.upper()[0]}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv'

        if not os.path.isfile(log_file):
            fiat_saldo_dia_anterior , btc_saldo_dia_anterior = self.get_saldo_dia_anterior()
            with open(log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([fiat_saldo_dia_anterior,btc_saldo_dia_anterior])
        
        if currency == 'COP':
            p_c = self.get_precio_de_cambio(currency_venta)
            fiat2 = float(fiat) / float(p_c)
            with open(log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([fiat2,btc,fiat,currency_venta])
                self.send_text([administrador], f'se escribio en log de {tipo} {currency}, {btc}, {fiat} para venta en {currency_venta}', verbose=True)

        else:

            with open(log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([fiat,btc])
                self.send_text([administrador], f'se escribio en log de de {tipo} {currency}, {btc}, {fiat} para venta en {currency_venta}',verbose=True)

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
        
        
        return  'Gracias, buen día'\
            '\n Thanks'

    def get_message_cuenta_identificada(self):

        """Devuelve el mensaje cuando identifica la cuenta a consignar"""

        return 'Ok , Procedo teniendo en cuenta los terminos de este comercio'\
            '\n Ok, I proceed in accordance with the terms of this trade.'

    def get_message_nuevo_comercio(self):
        
        """Devuelve el mensaje para nuevo comercio"""

        return 'Hola, cuales son los datos de cuenta para consignar/transferir?'\
            '\nHello, what are the account details to transfer?'

    def respond_notifications(self):

    
        """Atiende las notificaciones"""

        id_ad, currency = self.get_atributos("id_ad", "currency")
        # print(self.con_color(f'Revisando notificaciones...{currency[0:2]}'), flush=True)
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
                        self.atender_final_de_comercio(notificacion, conn, tipo='compra')

        end_time = time.time()
        duracion = end_time - start_time    
        # print(self.format_time(duracion), flush=True)

class NotificadorVentaCostaRica(Notificador):

    def atender_nuevo_comercio(self, notificacion, conn):

        """Atiende la notificacion de 'tiene un nuevo comercio'"""

        mensaje = self.get_message_nuevo_comercio()
        contact_id = notificacion['contact_id']
        contact_info = self.get_contact_info(conn, contact_id)

        if contact_info['buyer']['username'] in ['josedmarin','Djpb0102', 'camedina11', 'elissakmd', 'Ricardo8830', 'EileenArguedasM', 'Ricardo8830', 'ailak', 'grios14', 'cris_sulbaran','nazuaje','ERNESTONE','jevale310879','Andréssanchez20','Hugobttx']:
            mensaje = self.get_despues_de_aceptado()
            
        self.marcar_notificacion_como_leida(conn,notificacion,descripcion=f'Nuevo comercio #{contact_id}')

        self.send_msg_contact(conn, contact_id, mensaje, f'Mensaje nuevo comercio enviado #{contact_id}',verbose=True)

    def get_despues_de_aceptado(self):
        
        receptor, receptores = self.get_atributos("receptor","receptores")

        """Devuelve el mensaje para nuevo comercio"""

        return receptores[receptor]

    def get_message_nuevo_comercio(self):

        mensaje = 'Hola \n NO SE ADMITEN TRANSFERENCIAS DE TERCEROS\n\n'\
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
        administrador, receptor, verificador,verificador2 = self.get_atributos('administrador', 'receptor','verificador', 'verificador2')

        aceptado = False
        attachment = False
        enviado = False
        enviado_despues_de_aceptado = False
        payed = False
        
        mensaje_venta_completada = self.get_message_venta_completada()
        mensaje_despues_de_aceptado = self.get_despues_de_aceptado()

        contact_id = notificacion['contact_id']
        contact_info = self.get_contact_info(conn, contact_id)
        contact_messages = self.get_contact_messages(conn, contact_id)
        nombre_de_local = contact_info['buyer']['real_name']

        self.marcar_notificacion_como_leida(conn,notificacion,descripcion=f'Nuevo mensaje o comprobante #{contact_id}')

        for message in contact_messages:
            if 'attachment_type' in message:
                attachment = True
            if message['msg'][0:13] == mensaje_venta_completada[0:13]:
                enviado = True
            if message['msg'][-4:] == mensaje_despues_de_aceptado[-4:]:
                enviado_despues_de_aceptado = True
            if 'si' in message['msg'].lower() or 'ok' in message['msg'].lower():
                aceptado = True
                                
        if contact_info['payment_completed_at'] is not None:
            payed = True

        if aceptado and not enviado_despues_de_aceptado:

            self.send_msg_contact(conn, contact_id, mensaje_despues_de_aceptado, f'Mensaje nuevo comercio enviado #{contact_id}',verbose=True)

                        
        if attachment and payed and not enviado:
            
            self.send_msg_contact(conn, contact_id, mensaje_venta_completada, f'Mensaje nuevo comercio enviado #{contact_id}',verbose=True)

            amount = contact_info['amount'] + ' ' + contact_info['currency']

            self.send_text([verificador,administrador,verificador2], f'Revisa {amount} en la cuenta de {str(receptor).upper()}\n{nombre_de_local}',verbose=True)
        



