from agentes.vendedor import Vendedor
from settings.settings import CR_KEY, CR_SECRET

import sys

if __name__ == "__main__":

    precio_limite_total = float(sys.argv[1])
    minimo = 5000
    comision_local = 0.01
    currency = 'CRC'
    ad_id = '1381456'
    key = CR_KEY
    secret = CR_SECRET
    parametros={
        'lat': 0,
        'lon': 0,
        'city': 'San José',
        'location_string': 'San José Province, San José, Costa Rica',
        'countrycode': 'CR',
        'account_info': 'Transferencia⭐o deposito⭐',
        'bank_name': '⭐BAC⭐SINPE⭐TODOS LOS BANCOS⭐RAPIDO⚡️️️',
        'msg': 'Transferencia⭐o deposito⭐. Todos los bancos con Colón Costarricense (CRC)\n\n'\
                'Si no es banco BAC , debes tener en cuenta la comisión correspondiente.\n\n'\
                'En la referencia de pago debes poner compra de btc y tu usuario o marcar el recibo\n\n'\
                '@sromeroBTC1\n\nEnglish spoken',
        'sms_verification_required': True,
        'track_max_amount': True,
        'require_trusted_by_advertiser': False,
        'require_identification': True,
        'opening_hours': '[[46, 80], [36, 90], [36, 90], [36, 90], [36, 90], [36, 90], [36, 80]]'
    }
    porcentaje_btc = 1/3
    vender_solo = True
    vendedor = Vendedor(precio_limite_total, minimo, comision_local, currency, ad_id,key, secret, parametros,porcentaje_btc, vender_solo)
    vendedor.update_price()
    