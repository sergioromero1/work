from .conectar import Connection
from decoradores.loop import loop
from utils.color import Color
import csv
import datetime
import os
import time

class Vendedor:

    def __init__(self, porcentaje_de_ganancia, minimo, comision_local, currency, ad_id,key, secret, parametros,currency_compra):

        self.porcentaje_de_ganancia = porcentaje_de_ganancia
        self.minimo = minimo
        self.comision_local = comision_local
        self.currency = currency
        self.ad_id = ad_id
        self.key = key
        self.secret = secret
        self.parametros = parametros
        self.currency_compra = currency_compra

    def get_atributos(self, *nombres: str):
        """Retorna los atributos solicitados como una tupla"""

        return (self.__dict__[nombre] for nombre in nombres)
    #OK
    def get_btc_en_scrow(self, conn, currency):
        
        response = conn.call(method='GET',url= f'/api/dashboard/')
        num_contactos = int(response.json()['data']['contact_count'])

        info = {f'{currency[0:2]}':0}  

        if num_contactos != 0:
            for contacto in range(num_contactos):
                currency_contacto = response.json()['data']['contact_list'][contacto]['data']['currency']
                if currency_contacto == currency:
                    if response.json()['data']['contact_list'][contacto]['data']['is_selling']:
                        amount_btc = response.json()['data']['contact_list'][contacto]['data']['amount_btc']
                        fee_btc = response.json()['data']['contact_list'][contacto]['data']['fee_btc']

                        info[f'{currency[0:2]}'] += float(amount_btc) + float(fee_btc)

            return round(info[f'{currency[0:2]}'],8) if info[f'{currency[0:2]}'] !=0 else 0

        return info[f'{currency[0:2]}']
    #OK
    def get_saldo_dia_anterior(self):
        """Lee y retorna los valores totales de btc sin vender del dia anterior"""
        currency, currency_compra = self.get_atributos("currency", "currency_compra")

        for td in range(1,31):
            total_btc_compra = 0
            if os.path.isfile(f'logs/C-{currency_compra[0:2]}-{str(datetime.datetime.now().date()-datetime.timedelta(days=td))}.csv'):
                with open(f'logs/C-{currency_compra[0:2]}-{str(datetime.datetime.now().date()-datetime.timedelta(days=td))}.csv', newline='') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        total_btc_compra += float(row[1])
        
            total_btc_venta = 0
            if os.path.isfile(f'logs/V-{currency[0:2]}-{str(datetime.datetime.now().date()-datetime.timedelta(days=td))}.csv'):
                with open(f'logs/V-{currency[0:2]}-{str(datetime.datetime.now().date()-datetime.timedelta(days=td))}.csv', newline='') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        total_btc_venta += float(row[1])

            precio_de_compra_dia_anterior = 0
            if os.path.isfile(f'logs/C-{currency_compra[0:2]}-{str(datetime.datetime.now().date()-datetime.timedelta(days=td))}.csv'):
                with open(f'logs/C-{currency_compra[0:2]}-{str(datetime.datetime.now().date()-datetime.timedelta(days=td))}.csv', newline='') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if float(row[1]) != 0:
                            precio = float(row[0])/float(row[1])
                            peso = float(row[1]) / total_btc_compra
                            precio_de_compra_dia_anterior += precio * peso
                
                break

        total_btc = total_btc_compra - total_btc_venta
        total_fiat = total_btc * precio_de_compra_dia_anterior
        
        return (round(total_fiat,2), round(total_btc,8)) if total_btc > 0.00007 else (0 , 0)
    #OK
    def escribir_saldo_dia_anterior(self):

        currency_compra, = self.get_atributos("currency_compra")

        if not os.path.isfile(f'logs/C-{currency_compra[0:2]}-{str(datetime.datetime.now().date())}.csv'):
            fiat_saldo_dia_anterior , btc_saldo_dia_anterior = self.get_saldo_dia_anterior()
            with open(f'logs/C-{currency_compra[0:2]}-{str(datetime.datetime.now().date())}.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([fiat_saldo_dia_anterior,btc_saldo_dia_anterior])

    def get_precio_limite_total(self):

        currency, currency_compra, porcentaje_de_ganancia = self.get_atributos("currency", "currency_compra", "porcentaje_de_ganancia")

        fiat_correspondiente_comprado, btc_comprados = self.leer_log(currency_compra, tipo='compra')

        venta_total_bool, fiat_ultima_fila, btc_ultima_fila, hay_btc = self.verificar_venta_total(currency,currency_compra)
        
        precio_limite_total = None

        if fiat_correspondiente_comprado !=0 and btc_comprados !=0:
            precio_limite_total = round((float(fiat_correspondiente_comprado) / float(btc_comprados))*porcentaje_de_ganancia,2)

            if venta_total_bool:
                precio_limite_total = round((float(fiat_ultima_fila) / float(btc_ultima_fila))*porcentaje_de_ganancia,2)


        return precio_limite_total if (fiat_correspondiente_comprado !=0 and btc_comprados !=0) or hay_btc else None

    def get_total_btc(self, conn):

        """obtiene el total de btc para el currency"""
        currency, currency_compra = self.get_atributos("currency", "currency_compra")
                        
        _, btc_comprados = self.leer_log(currency_compra,tipo='compra')
        _, btc_vendidos = self.leer_log(currency,tipo='venta')
        btc_en_scrow = self.get_btc_en_scrow(conn, currency)

        total_btc = round(float(btc_comprados)-float(btc_vendidos)-float(btc_en_scrow),8)

        return total_btc

    def get_my_trade_count(self,conn):
        username = 'sromero'
        my_self = conn.call(method='GET',url= f'/api/account_info/{username}/')
        my_trade_count = float(my_self.json()['data']['confirmed_trade_count_text'].replace('+',''))

        return my_trade_count

    def adelantar(self, precio_del_otro, conn):

        """Adelanta un precio(se pone por debajo)"""

        ad_id, comision_local, currency,  minimo = self.get_atributos("ad_id", "comision_local","currency",  "minimo")

        nuevo_precio = round(precio_del_otro - precio_del_otro*0.00001)
        print(f'El precio a mejorar es {precio_del_otro} {currency}', flush=True)
        total_btc = self.get_total_btc(conn)
        nuevo_maximo = total_btc * (1.0 - comision_local) * nuevo_precio
        prendida = self.is_active(conn)
        params  = self.informacion_del_anuncio(minimo, nuevo_maximo, nuevo_precio, prendida)
        response = conn.call(method='POST', url= f'/api/ad/{ad_id}/', params={**params})
        mi_nuevo_precio,_,_ = self.precio_actual(conn)
        print(response.json(), self.con_color(f'Precio adelantado, \n Mi nuevo precio es {mi_nuevo_precio} {currency}'), flush=True)

        return mi_nuevo_precio

    def actualizar_ad(self,conn, ad_id, params):

        currency, = self.get_atributos("currency")

        response = conn.call(method='POST', url= f'/api/ad/{ad_id}/', params={**params})
        mi_nuevo_precio,_,_ = self.precio_actual(conn)
        print(response.json(), self.con_color(f'Precio adelantado, \n Mi nuevo precio es {mi_nuevo_precio} {currency}'), flush=True)

    def conectar(self,server='https://localbitcoins.com'):

        """Se conecta a local bitcoins"""

        key, secret = self.get_atributos("key", "secret")
        conn = Connection()
        conn._set_hmac(server, key, secret)
        
        return conn

    def con_color(self, string):
        return Color.BLUE + string + Color.END

    def descansar(self, conn):

        """Descansa cuando ha combatido mucho por el precio"""


        info = self.informacion_comerciantes(conn)
        try:
            precio_cuarto = info['cuarto']['price']
        except KeyError:
            precio_cuarto = info['segundo']['price']

        self.adelantar(precio_cuarto, conn)

        print(self.con_color('\nresting...\n'), flush=True)
        time.sleep(420)

    def fijar(self, precio_limite, conn):
        start_time = time.time()
        """Fija el anuncio en un precio determinado"""

        ad_id, comision_local, currency, minimo = self.get_atributos("ad_id","comision_local", "currency", "minimo")

        nuevo_precio = precio_limite
        total_btc = self.get_total_btc(conn)
        nuevo_maximo = total_btc * (1.0 - comision_local) * nuevo_precio
        prendida = self.is_active(conn)
        params  = self.informacion_del_anuncio(minimo, nuevo_maximo, nuevo_precio, prendida)
        response = conn.call(method='POST', url= f'/api/ad/{ad_id}/', params={**params})
        
        mi_nuevo_precio,_,_ = self.precio_actual(conn)
        print(response.json(), f'Precio fijado, Mi precio estabilizado por 15 min es {mi_nuevo_precio} {currency}', flush=True)
        end_time = time.time()
        duracion = end_time - start_time 
        print('la duracion de enviar los datos para fijar el precio fue: ', self.format_time(duracion), flush=True)

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
        
        try:
            response = conn.call(method='GET',url= f'/buy-bitcoins-online/{currency}/.json')
            ad = response.json()['data']['ad_list']
        except ValueError:
            ad = []
        info = {}
        if len(ad) > 0:
            posiciones = ['primero','segundo','tercero','cuarto','quinto','sexto','septimo','octavo','noveno']
            
            for item in range(len(ad)):
                info[posiciones[item]] = {}
                if item == 8:
                    break

            position = 0
            for inside_dict in info.values():
                
                inside_dict['name'] = str(ad[position]['data']['profile']['username'])
                inside_dict['price'] = float(ad[position]['data']['temp_price'])
                inside_dict['min_amount'] = float(ad[position]['data']['min_amount_available']) if ad[position]['data']['min_amount_available'] is not None else 0
                inside_dict['max_amount'] = float(ad[position]['data']['max_amount_available']) if ad[position]['data']['max_amount_available'] is not None else (inside_dict['min_amount'] + 1) * 10
                inside_dict['trade_count'] = float(ad[position]['data']['profile']['trade_count'].replace('+','').replace(' ',''))
                inside_dict['feedback_score'] = float(ad[position]['data']['profile']['feedback_score'])
                inside_dict['currency'] = str(ad[position]['data']['currency'])

                position += 1

        return info

    def informacion_del_anuncio(self, minimo, nuevo_maximo, nuevo_precio, prendida):

        """Devuelve un diccionario con los parametros del anuncio"""

        currency, parametros = self.get_atributos("currency","parametros")

        is_visible = True
        if not prendida:
            is_visible = False
            nuevo_maximo = minimo + 1

        if int(nuevo_maximo) < 0:
            is_visible = False

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

    def leer_log(self, currency, tipo):
        """Lee y retorna los valores totales de fiat y btc del log"""

        total_btc = 0
        total_fiat = 0
        if os.path.isfile(f'logs/{tipo.upper()[0]}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv'):
            with open(f'logs/{tipo.upper()[0]}-{currency[0:2]}-{str(datetime.datetime.now().date())}.csv', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    total_btc += float(row[1])
                    total_fiat += float(row[0])
                   
        return (round(total_fiat,2) , round(total_btc,8)) if total_btc !=0 else (0 , 0)

    def verificar_venta_total(self, currency,currency_compra):
        """Verifica si ya se vendio todo lo del mismo dia para seguir vendiendo,
        y usar el precio de la nueva compra siguiente en otra función"""

        if os.path.isfile(f'logs/C-{currency_compra[0:2]}-{str(datetime.datetime.now().date())}.csv'):
            with open(f'logs/C-{currency_compra[0:2]}-{str(datetime.datetime.now().date())}.csv', newline='') as f:
                reader = list(csv.reader(f))
                btc_ultima_fila = reader[-1][1]
                fiat_ultima_fila = reader[-1][0]

        _, btc_comprados = self.leer_log(currency_compra,tipo='compra')
        _, btc_vendidos = self.leer_log(currency,tipo='venta')
        diferencia_btc = (abs(btc_comprados - btc_vendidos) - float(btc_ultima_fila))
        comp_vend = abs(btc_comprados - btc_vendidos)
        if comp_vend < 0.00001:
            hay_btc = False
        else:
            hay_btc = True


        if  diferencia_btc < 0.000015:
            return (True, round(float(fiat_ultima_fila),2), round(float(btc_ultima_fila),8), hay_btc) 
        else:
            return (False, _, _, hay_btc)

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

        print(self.con_color(f'Precio limite total de {precio_limite_total} {currency} alcanzado'), flush=True)

        self.fijar(precio_limite_total + 1, conn)

        time.sleep(350)

    def recorrer_puestos(self,info, conn):
        
        """Recorre las posiciones para saber donde ubicarse y se ubica en la 
            mejor oferta de precio. 

        """

        currency,  = self.get_atributos("currency")

        precio_actual, mi_min , mi_max = self.precio_actual(conn)
        my_trade_count = self.get_my_trade_count(conn)
        puesto_a_superar = 'segundo'
        for puesto,datos in info.items():
            if (
                mi_max >= datos['min_amount'] and
                mi_min <= datos['max_amount'] and 
                datos['name'] != 'sromero' and 
                datos['currency'] == currency
                ):
                if mi_max / datos['max_amount'] >=2.5: ## entre mas alto este numero con menos max amount de los otros , combate
                    continue 
                if my_trade_count / datos['trade_count']  >= 10: ## entre mas alto este numero con menos trade count de los otros , combate
                    continue
                puesto_a_superar = str(puesto)
                break

        precio_del_otro = info[f'{puesto_a_superar}']['price'] if info else precio_actual

        return precio_del_otro

    @loop
    def update_price(self):

        """Actualiza el precio teniendo en cuenta un precio limite 
            total y posicion deseada. Cuando hay un cambio abrubto
            de mas de 300 MXN descansa por unos minutos.
        """

        currency, = self.get_atributos("currency")
        conn = self.conectar()

        while True:

            self.escribir_saldo_dia_anterior()

            precio_limite_total = self.get_precio_limite_total()
            
            if precio_limite_total is None:
                print(f'No hay btc', flush=True)
                time.sleep(30)
                continue

            print(precio_limite_total, flush=True)

            print(f'\nrunning...{currency[0:2]}\n', flush=True)

            info = self.informacion_comerciantes(conn)
            
            if len(info) > 0:
                precio_del_otro = self.recorrer_puestos(info, conn)
            else:
                self.precio_limite_alcanzado(conn, precio_limite_total)
                continue

            if precio_del_otro < float(precio_limite_total):

                self.precio_limite_alcanzado(conn, precio_limite_total)
                continue

            precio_de_inicio = self.adelantar(precio_del_otro, conn)

            delta_de_precio = 0

            while delta_de_precio < precio_de_inicio*0.01:
                start_time = time.time()
                print('\nrunning...combat\n', flush=True)
                mi_precio, _, _ = self.precio_actual(conn)
                info = self.informacion_comerciantes(conn)
                
                if mi_precio > precio_limite_total:

                    precio_del_otro = self.recorrer_puestos(info, conn)
                    self.adelantar(precio_del_otro, conn)

                else:
                    self.precio_limite_alcanzado(conn, precio_limite_total)

                mi_nuevo_precio,_,_ = self.precio_actual(conn)

                delta_de_precio = precio_de_inicio - mi_nuevo_precio
                end_time = time.time()
                duracion = end_time - start_time    
                print(self.format_time(duracion), f'El delta de precio es: {delta_de_precio}', flush=True)
                time.sleep(30)

            else:
                self.descansar(conn)