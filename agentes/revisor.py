from .conectar import Connection
from bs4 import BeautifulSoup
from datetime import timedelta
from utils.color import Color

import csv
import datetime
import os
import requests
import time

class Revisor:

    def __init__(self, bot_token,key, secret, sleep_time, verificador):

        self.bot_token = bot_token
        self.key = key
        self.secret = secret
        self.sleep_time = sleep_time
        self.verificador = verificador

    def conectar(self,server='https://localbitcoins.com'):

        """Se conecta a local bitcoins"""

        key, secret = self.get_atributos("key", "secret")
        conn = Connection()
        conn._set_hmac(server, key, secret)
        
        return conn

    def con_color(self, string):
        return Color.BLUE + string + Color.END

    def check_day(self, time_released):
        
        created_at_str = time_released[0:10] + ' ' + time_released[11:19]

        cleaning = datetime.datetime.strptime(created_at_str,'%Y-%m-%d %H:%M:%S') - timedelta(hours=5)
        released_at = cleaning.date()

        now = datetime.datetime.now().date()

        return released_at == now

    def escribir_log(self, tipo, currency, btc, fiat):

        """Escribe los valores de fiat y btc al log"""
        t='V'
        if tipo == 'buy':
            t = 'C'

        if currency == 'COP' and tipo == 'buy':
            p_c = self.get_precio_de_cambio('MXN')
            fiat2 = float(fiat) / float(p_c)
            with open(f'logs/{t}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([fiat2,btc,fiat])

        else:
            with open(f'logs/{t}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([fiat,btc])

    def get_precio_de_cambio(self, currency):

        page = requests.get(f'https://www.x-rates.com/calculator/?from={currency}&to=COP&amount=1')
        soup = BeautifulSoup(page.text, 'html.parser')

        part1 = soup.find(class_="ccOutputTrail").previous_sibling
        part2 = soup.find(class_="ccOutputTrail").get_text(strip=True)
        rate = f"{part1}{part2}"

        return rate

    def leer_log(self, tipo, currency, btc, fiat):

        """Lee los valores del log"""
        t='V'
        if tipo == 'buy':
            t = 'C'
        encontrado = False
        if os.path.isfile(f'logs/{t}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv'):
            with open(f'logs/{t}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if float(btc) == float(row[1]):
                        encontrado = True

        if not encontrado:
            self.escribir_log(tipo, currency, btc, fiat)
            self.sendtext(f'Se escribio en log despues de revision {tipo}, {currency}, {btc}, {fiat}')
                    
    def get_atributos(self, *nombres: str):
        """Retorna los atributos solicitados como una tupla"""

        return (self.__dict__[nombre] for nombre in nombres)

    def encontrar_comercios(self):
        conn = self.conectar()
        comercios = []
        try:
            lista_liberados = conn.call(method='GET', url=f'/api/dashboard/released/').json()['data']['contact_list']
        except ValueError:
            lista_liberados = {}
        for posicion in lista_liberados:
            time_released = posicion['data']['released_at']
            if self.check_day(time_released):
                btc = round(float(posicion['data']['amount_btc']) - float(posicion['data']['fee_btc']),8)
                fiat = posicion['data']['amount']
                currency = posicion['data']['currency']
                tipo = 'buy'
                if posicion['data']['is_selling']:
                    tipo = 'sell'
                    btc = round(float(posicion['data']['amount_btc']) + float(posicion['data']['fee_btc']),8)
                comercios.append({'tipo':tipo, 'currency':currency, 'btc':btc, 'fiat':fiat})
        
        return comercios

    def revisar(self):

        sleep_time = int(self.sleep_time)
        while True:
            start_time = time.time()
            print(self.con_color(f'realizando revisión 1'), flush=True)
            comercios = self.encontrar_comercios()

            for comercio in comercios:
                tipo = comercio['tipo']
                currency = comercio['currency']
                btc = comercio['btc']
                fiat = comercio['fiat']
                self.leer_log(tipo, currency, btc, fiat)

            end_time = time.time()
            duracion = end_time - start_time    
            print(duracion, flush=True)
            time.sleep(sleep_time)

    def sendtext(self, bot_message):

        bot_token , verificador = self.get_atributos("bot_token", "verificador")

        persona_id = verificador

        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + persona_id + '&parse_mode=Markdown&text=' + bot_message

        response = requests.post(send_text)

        return response.json()['ok']


