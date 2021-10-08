from agentes.vendedor import Vendedor

from settings.settings import MX_KEY, MX_SECRET
import time

import sys

if __name__ == "__main__":

    porcentaje_de_ganancia = 1.02
    minimo = 50
    comision_local = 0.01
    currency = 'USDT'
    ad_id = '1380529'
    key = MX_KEY
    secret = MX_SECRET
    parametros={
        'lat': 0,
        'lon': 0,
        'city': 'Mexico City',
        'location_string': 'Mexico City, CDMX, Mexico',
        'countrycode': 'MX',
        'account_info': 'Transferencia⭐USTD⭐ Tether ⭐Trasnfer',
        'bank_name': 'Transferencia⭐USTD⭐ Tether ⭐Trasnfer',
        'msg': 'Transferencia⭐USTD⭐ Tether ⭐Trasnfer\n\n'\
            'recibimos en Binance smart Chain\n\n'\
            'we recieve through Binance smart Chain\n\n'\
            'Cualquier duda estoy a sus ordenes, Gracias!!\n\n'\
            'telegram: @sromeroBTC1', 
        'sms_verification_required': True,
        'track_max_amount': True,
        'require_trusted_by_advertiser': False,
        'require_identification': True,
        'opening_hours': '[[38, 80], [35, 88], [35, 88], [35, 88], [35, 88], [35, 88], [36, 80]]',
    }
    currency_compra = 'USTD'
    vender_solo = False
    vendedor = Vendedor(porcentaje_de_ganancia, minimo, comision_local, currency, ad_id,key, secret, parametros,currency_compra, vender_solo)
    vendedor.update_price()
        
    