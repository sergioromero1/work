from .conectar import Connection
from utils.color import Color
from decoradores.loop import loop
import time
import sys

class Comprador:

    def __init__(self, currency, ad_id, posicion, key, secret):

        self.currency = currency
        self.ad_id = ad_id
        self.posicion = posicion
        self.key = key
        self.secret = secret

    def get_atributos(self, *nombres: str):
        """Retorna los atributos solicitados como una tupla"""

        return (self.__dict__[nombre] for nombre in nombres)

    def adelantar(self, precio_del_otro, conn):

        """Adelanta un precio(se pone por debajo)"""

        ad_id, currency = self.get_atributos("ad_id", "currency")

        nuevo_precio = round(precio_del_otro + precio_del_otro*0.00001)
        print(f'El precio a mejorar es {precio_del_otro} {currency}', flush=True)
        response = conn.call(method='POST', url= f'/api/ad-equation/{ad_id}/', params={'price_equation': f'{nuevo_precio}'})
        mi_nuevo_precio = self.precio_actual(conn)
        print(response.json(), self.con_color(f'Precio adelantado, Mi nuevo precio es {mi_nuevo_precio} {currency}'), flush=True)

        return mi_nuevo_precio

    def con_color(self, string):
        return Color.BLUE + string + Color.END

    def conectar(self,server='https://localbitcoins.com'):

        """Se conecta a local bitcoins"""

        key, secret = self.get_atributos("key", "secret")
        conn = Connection()
        conn._set_hmac(server, key, secret)

        return conn

    def format_time(self,sec):

        """ Cambia el formato de tiempo"""

        mins = sec // 60
        sec = sec % 60
        hours = mins // 60
        mins = mins % 60
        return "Duración = {0}:{1}:{2}".format(int(hours),int(mins),round(sec,2))

    def informacion_comerciantes(self, conn):

        """Retorna la informacion de los 6 primeros anuncios"""

        currency,  = self.get_atributos("currency")


        response = conn.call(method='GET',url= f'/sell-bitcoins-online/{currency}/.json')
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

    def precio_actual(self, conn):

        """Devuelve el precio actual, monto minimo y monto máximo del anuncio"""

        ad_id, = self.get_atributos("ad_id")
        response = conn.call(method='GET', url= f'/api/ad-get/', params={'ads': {ad_id}})
        ad = response.json()['data']['ad_list'][0]['data']
        min_amount= float(ad['min_amount'])
        max_amount = float(ad['max_amount'])

        precio_actual = float(ad['temp_price'])

        return precio_actual, min_amount, max_amount

    def recorrer_puestos(self,info):

        """Recorre las posiciones para saber donde ubicarse y se ubica en la
            mejor oferta de precio
        """

        for puesto,datos in info.items():
            if datos['name'] != 'sromero':
                puesto_a_superar = str(puesto)
                break

        return puesto_a_superar

    @loop
    def update_price(self):

        """Actualiza el precio teniendo en cuenta la
            posicion en la que se quiere vender
        """

        posicion, currency = self.get_atributos("posicion", "currency")
        conn = self.conectar()

        while True:

            print(f'\nrunning...{currency[0:2]}\n', flush=True)
            info = self.informacion_comerciantes(conn)
            puesto_a_superar = self.recorrer_puestos(info)
            if posicion == 'primero':
                self.adelantar(info[f'{puesto_a_superar}']['price'],conn)
            else:
                self.adelantar(info[f'{posicion}']['price'],conn)
            time.sleep(120)
