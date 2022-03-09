from agentes.vendedor import Vendedor
from settings.settings import CR_KEY, CR_SECRET
import time


import sys

if __name__ == "__main__":

    porcentaje_de_ganancia = 1.10
    minimo = 2000
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
        'bank_name': '⭐BAC⭐SINPE⭐TODOS LOS BANCOS⭐RAPIDO⚡️️️NO TERCEROS',
        'msg':  'NO SE ADMITEN TRANSFERENCIAS DE TERCEROS\n'\
                'El nombre del titular de la transferencia debe coincidir con el titular de la cuenta de localbitcoins para liberar los btc\n\n'\
                'Al ofertar aceptas los terminos\n\n'\
                'Transferencia⭐o deposito⭐. Todos los bancos con Colón Costarricense (CRC)\n\n'\
                'Si no es banco BAC , debes tener en cuenta la comisión correspondiente.\n\n'\
                'En la referencia de pago debes poner pago de servicios no reembolsable\n\n'\
                '@sromeroBTC1\n\nEnglish spoken',
        'sms_verification_required': True,
        'track_max_amount': True,
        'require_trusted_by_advertiser': False,
        'require_identification': True,
        'opening_hours': '[[38, 80], [35, 88], [35, 88], [35, 88], [35, 88], [35, 88], [36, 80]]'
    }
    currency_compra = 'CRC'
    vender_solo = False
    vendedor = Vendedor(porcentaje_de_ganancia, minimo, comision_local, currency, ad_id,key, secret, parametros,currency_compra, vender_solo)
    vendedor.update_price()

    