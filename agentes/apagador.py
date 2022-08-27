import time
from agentes.caller  import Caller
from datetime import datetime
from pytz import timezone

class Apagador(Caller):
    
    def ad(self, conn, visible):

        ad_id,params = self.get_atributos("ad_id","parametros")
        
        precio_actual, min_amount, max_amount = self.precio_actual(conn)

        params['price_equation'] = precio_actual
        params['min_amount'] = min_amount
        params['max_amount'] = max_amount
        params['visible'] = visible

        response = conn.call(method='POST', url= f'/api/ad/{ad_id}/', params={**params})
        print(response.json(), f'Ad visible {visible}', flush=True)

    def precio_actual(self, conn):

        """Devuelve el precio actual, monto minimo y monto máximo del anuncio"""

        ad_id, = self.get_atributos("ad_id")
        response = conn.call(method='GET', url= f'/api/ad-get/', params={'ads': {ad_id}})
        ad = response.json()['data']['ad_list'][0]['data']
        min_amount= float(ad['min_amount'])
        max_amount = float(ad['max_amount'])

        precio_actual = float(ad['temp_price'])
    
        return precio_actual, min_amount, max_amount

    def actuar(self):

        # all time in utc time

        conn = self.conectar()

        while True:

            print('Checking turnoff', flush=True)
            hora_actual = datetime.utcnow()

            hora_medio_dia_incial =  datetime(hora_actual.year, hora_actual.month, hora_actual.day,18,30,0)
            hora_medio_dia_incial2 =  datetime(hora_actual.year, hora_actual.month, hora_actual.day,18,33,0)

            hora_medio_dia_final = datetime(hora_actual.year, hora_actual.month, hora_actual.day,20,0,0)
            hora_medio_dia_final2 = datetime(hora_actual.year, hora_actual.month, hora_actual.day,20,3,0)

            if hora_actual > hora_medio_dia_incial and hora_actual < hora_medio_dia_incial2:
                self.apagar_ad(conn, visible=False)
                time.sleep(200)

            if hora_actual > hora_medio_dia_final and hora_actual < hora_medio_dia_final2:
                self.prender_ad(conn, visible=True)
                time.sleep(200)

            time.sleep(60)