from .conectar import Connection
import csv
import datetime
import os
import time

class Vendedor:

    def __init__(self, precio_limite_total, minimo, comision_local, currency, ad_id,key, secret, parametros,porcentaje_btc, vender_solo):

        self.precio_limite_total = precio_limite_total
        self.minimo = minimo
        self.comision_local = comision_local
        self.currency = currency
        self.ad_id = ad_id
        self.key = key
        self.secret = secret
        self.parametros = parametros
        self.porcentaje_btc = porcentaje_btc
        self.vender_solo = vender_solo

    def get_atributos(self, *nombres: str):
        """Retorna los atributos solicitados como una tupla"""

        return (self.__dict__[nombre] for nombre in nombres)

    def get_btc_en_scrow(self, conn, currency):
        
        response = conn.call(method='GET',url= f'/api/dashboard/')
        num_contactos = int(response.json()['data']['contact_count'])

        info = {'MX': 0, 'CR': 0}  #SUJETO A REVISION Y CAMBIO POR MAS PAISES

        if num_contactos != 0:
            for contacto in range(num_contactos):

                currency_interna = response.json()['data']['contact_list'][contacto]['data']['currency']
                amount_btc = response.json()['data']['contact_list'][contacto]['data']['amount_btc']
                fee_btc = response.json()['data']['contact_list'][contacto]['data']['fee_btc']

                info[f'{currency_interna[0:2]}'] += float(amount_btc) + float(fee_btc)

            return round(info[f'{currency[0:2]}'],8) if info[f'{currency[0:2]}'] !=0 else 0

        return info[f'{currency[0:2]}']

    def get_total_btc(self, conn):

        """obtiene el total de btc para el currency"""
        currency, porcentaje_btc = self.get_atributos("currency", "porcentaje_btc")
        
        if currency == 'MXN':             #SUJETO A REVISION Y CAMBIO POR MAS PAISES
            currency_otro = 'CRC'         #SUJETO A REVISION Y CAMBIO POR MAS PAISES
        else:                             #SUJETO A REVISION Y CAMBIO POR MAS PAISES
            currency_otro = 'MXN'          #SUJETO A REVISION Y CAMBIO POR MAS PAISES

        response = conn.call(method='GET',url= f'/api/wallet-balance/')
        balance = response.json()['data']['total']['balance']
        btc_en_scrow = self.get_btc_en_scrow(conn, currency)
        btc_en_scrow_otros = self.get_btc_en_scrow(conn, currency_otro)
        btc_vendidos = self.leer_log(currency)
        btc_vendidos_otro = self.leer_log(currency_otro)

        total_btc = round((float(balance) + float(btc_vendidos) + float(btc_vendidos_otro) + float(btc_en_scrow) + float(btc_en_scrow_otros)) * porcentaje_btc,8) - float(btc_vendidos) - float(btc_en_scrow) 

        return total_btc

    def adelantar(self, precio_del_otro, conn):

        """Adelanta un precio(se pone por debajo)"""

        ad_id, currency = self.get_atributos("ad_id", "currency")
        
        nuevo_precio = round(precio_del_otro - precio_del_otro*0.00001)
        print(f'El precio a mejorar es {precio_del_otro} {currency}')
        response = conn.call(method='POST', url= f'/api/ad-equation/{ad_id}/', params={'price_equation': f'{nuevo_precio}'})
        mi_nuevo_precio = self.precio_actual(conn)
        print(response.json(), f'Precio adelantado, Mi nuevo precio es {mi_nuevo_precio} {currency}')

        return mi_nuevo_precio

    def adelantar_beta(self, precio_del_otro, conn):

        """Adelanta un precio(se pone por debajo)"""

        ad_id, comision_local, currency,  minimo = self.get_atributos("ad_id", "comision_local","currency",  "minimo")

        nuevo_precio = round(precio_del_otro - precio_del_otro*0.00001)
        print(f'El precio a mejorar es {precio_del_otro} {currency}')
        total_btc = self.get_total_btc(conn)
        nuevo_maximo = total_btc * (1.0 - comision_local) * nuevo_precio
        prendida = self.is_active(conn)
        params  = self.informacion_del_anuncio(minimo, nuevo_maximo, nuevo_precio, prendida)
        response = conn.call(method='POST', url= f'/api/ad/{ad_id}/', params={**params})
        mi_nuevo_precio = self.precio_actual(conn)
        print(response.json(), f'Precio adelantado, Mi nuevo precio es {mi_nuevo_precio} {currency}')

        return mi_nuevo_precio

    def conectar(self,server='https://localbitcoins.com'):

        """Se conecta a local bitcoins"""

        key, secret = self.get_atributos("key", "secret")
        conn = Connection()
        conn._set_hmac(server, key, secret)
        
        return conn

    def descansar(self, conn):

        """Descansa cuando ha combatido mucho por el precio"""


        info = self.informacion_comerciantes(conn)
        precio_cuarto = info['cuarto']['price']

        if self.vender_solo:
            self.adelantar(precio_cuarto, conn)
        else:
            self.adelantar_beta(precio_cuarto, conn)

        print('\nresting...\n')
        time.sleep(420)

    def fijar(self,precio_limite, conn):

        """Fija el anuncio en un precio determinado"""

        ad_id, currency = self.get_atributos("ad_id", "currency")

        nuevo_precio = precio_limite
        response = conn.call(method='POST', url= f'/api/ad-equation/{ad_id}/', params={'price_equation': f'{nuevo_precio}'})
        mi_nuevo_precio = self.precio_actual(conn)
        print(response.json(), f'Precio fijado, Mi precio estabilizado por 15 min es {mi_nuevo_precio} {currency}')

    def fijar_beta(self, precio_limite, conn):

        """Fija el anuncio en un precio determinado"""

        ad_id, comision_local, currency, minimo = self.get_atributos("ad_id","comision_local", "currency", "minimo")

        nuevo_precio = precio_limite
        total_btc = self.get_total_btc(conn)
        nuevo_maximo = total_btc * (1.0 - comision_local) * nuevo_precio
        prendida = self.is_active(conn)
        params  = self.informacion_del_anuncio(minimo, nuevo_maximo, nuevo_precio, prendida)
        response = conn.call(method='POST', url= f'/api/ad/{ad_id}/', params={**params})
        
        mi_nuevo_precio = self.precio_actual(conn)
        print(response.json(), f'Precio fijado, Mi precio estabilizado por 15 min es {mi_nuevo_precio} {currency}')

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

    def informacion_del_anuncio(self, minimo, nuevo_maximo, nuevo_precio, prendida):

        """Devuelve un diccionario con los parametros del anuncio"""

        currency, parametros = self.get_atributos("currency","parametros")

        is_visible = True
        if not prendida:
            is_visible = False
            nuevo_maximo = minimo + 1

        params={
        'price_equation': f'{nuevo_precio}',
        'lat': parametros['lat'],
        'lon': parametros['lon'],
        'city': parametros['city'],
        'location_string': parametros['location_string'],
        'countrycode': parametros['countrycode'],
        'currency': currency,
        'account_info': parametros['account_info'],
        'bank_name': parametros['bank_name'],
        'msg': parametros['msg'],
        'sms_verification_required': parametros['sms_verification_required'],
        'track_max_amount': parametros['track_max_amount'],
        'require_trusted_by_advertiser': parametros['require_trusted_by_advertiser'],
        'require_identification': parametros['require_identification'],
        'min_amount': int(minimo),
        'max_amount': int(nuevo_maximo),
        'opening_hours': parametros['opening_hours'],
        'visible': is_visible

        }
        return params

    def is_active(self,conn):

        ad_id, = self.get_atributos("ad_id")
        response = conn.call(method='GET', url= f'/api/ad-get/', params={'ads': {ad_id}})
        ad = response.json()['data']['ad_list'][0]['data']
        visible = ad['visible']

        return visible

    def leer_log(self, currency):
        """Lee y retorna los valores totales de fiat y btc del log"""

        total_fiat = 0
        total_btc = 0
        if os.path.isfile(f'logs/{currency[0:2]}-{str(datetime.datetime.now().date())}.csv'):
            with open(f'logs/{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    total_fiat += float(row[0])
                    total_btc += float(row[1])
        
        return round(total_btc,8) if total_btc !=0 else 0

    def precio_actual(self, conn):

        """Devuelve el precio actual, monto minimo y monto máximo del anuncio"""

        ad_id, = self.get_atributos("ad_id")
        response = conn.call(method='GET', url= f'/api/ad-get/', params={'ads': {ad_id}})
        ad = response.json()['data']['ad_list'][0]['data']
        min_amount= float(ad['min_amount'])
        max_amount = float(ad['max_amount'])

        precio_actual = float(ad['temp_price'])
        
        return precio_actual, min_amount, max_amount

    def precio_limite_alcanzado(self, conn, precio_limite_total):
        
        """fija precio cuando el limite es alcanzado"""

        currency,  = self.get_atributos("currency")

        print(f'Precio limite total de {precio_limite_total} {currency} alcanzado')
        if self.vender_solo:
            self.fijar(precio_limite_total + 1, conn)
        else:
            self.fijar_beta(precio_limite_total + 1, conn)

        time.sleep(900)

    def recorrer_puestos(self,info, conn):
        
        """Recorre las posiciones para saber donde ubicarse y se ubica en la 
            mejor oferta de precio
        """

        _, mi_min , mi_max = self.precio_actual(conn)
        puesto_a_superar = 'cuarto'
        for puesto,datos in info.items():
            if mi_max >= datos['min_amount'] and mi_min <= datos['max_amount'] and datos['name'] != 'sromero':
                puesto_a_superar = str(puesto)
                break
        
        precio_del_otro = info[f'{puesto_a_superar}']['price']

        if self.vender_solo:
            mi_nuevo_precio = self.adelantar(precio_del_otro, conn)
        else:
            mi_nuevo_precio = self.adelantar_beta(precio_del_otro, conn)

        return mi_nuevo_precio

    def update_price(self):

        """Actualiza el precio teniendo en cuenta un precio limite 
            total y posicion deseada. Cuando hay un cambio abrubto
            de mas de 300 MXN descansa por unos minutos.
        """

        precio_limite_total, currency = self.get_atributos("precio_limite_total", "currency")
        conn = self.conectar()

        while True:

            print(f'\nrunning...{currency[0:2]}\n')
            info = self.informacion_comerciantes(conn)
            precio_de_inicio,_,_ = self.recorrer_puestos(info, conn)
            
            if precio_de_inicio < float(precio_limite_total):

                self.precio_limite_alcanzado(conn, precio_limite_total)
                continue
            
            delta_de_precio = 0

            while delta_de_precio < precio_de_inicio*0.01:
                start_time = time.time()
                print('\nrunning...combat\n')
                mi_precio, _, _ = self.precio_actual(conn)
                info = self.informacion_comerciantes(conn)
                
                if mi_precio > precio_limite_total:

                    self.recorrer_puestos(info, conn)

                else:
                    self.precio_limite_alcanzado(conn, precio_limite_total)

                mi_nuevo_precio,_,_ = self.precio_actual(conn)

                delta_de_precio = precio_de_inicio - mi_nuevo_precio
                end_time = time.time()
                duracion = end_time - start_time    
                print(self.format_time(duracion), f'El delta de precio es: {delta_de_precio}')
                time.sleep(15)

            else:
                self.descansar(conn)