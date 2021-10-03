from agentes.vendedor import Vendedor
from settings.settings import MX_KEY, MX_SECRET

import sys

if __name__ == "__main__":

    porcentaje_de_ganancia = 1.07
    minimo = 100000
    comision_local = 0.01
    currency = 'COP'
    ad_id = '1352295'
    key = MX_KEY
    secret = MX_SECRET
    parametros={
        'lat': 0,
        'lon': 0,
        'city': 'Bogota',
        'location_string': 'Bogota, Colombia',
        'countrycode': 'CO',
        'account_info': 'Transferencia APP⭐ Corresponsal ⭐BANCOLOMBIA⭐',
        'bank_name': 'Transferencia APP⭐ Corresponsal ⭐BANCOLOMBIA⭐',
        'msg': 'Transferencia APP⭐ Corresponsal ⭐BANCOLOMBIA⭐. \n\n No terceros\n\n'\
                'Dependiendo de la transferencia podemos solicitar tu identificación\n\n'\
                'Si es por corresponsal marcar el recibo como no reembosable y nombre de usuario.\n\n'\
                'Si es por transferencia en asunto poner servicios técnicos no reembolsable.\n\n'\
                'Telegram: @sromeroBTC1\n\n'\
                'Cualquier duda estoy a sus ordenes, Gracias!!', 
        'sms_verification_required': True,
        'track_max_amount': True,
        'require_trusted_by_advertiser': False,
        'require_identification': True,
        'opening_hours': '[[38, 80], [35, 88], [35, 88], [35, 88], [35, 88], [35, 88], [36, 80]]'
    }
    porcentaje_btc = 2/3
    vender_solo = True
    vendedor = Vendedor(porcentaje_de_ganancia, minimo, comision_local, currency, ad_id,key, secret, parametros,porcentaje_btc, vender_solo)
    vendedor.update_price()
    