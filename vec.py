from agentes.vendedor import Vendedor

from settings.settings import MX_KEY, MX_SECRET
import time

import sys

if __name__ == "__main__":

    porcentaje_de_ganancia = 1.07
    minimo = 10
    comision_local = 0.01
    currency = 'USD'
    ad_id = '145877'
    key = MX_KEY
    secret = MX_SECRET
    parametros={
        'lat': 0,
        'lon': 0,
        'city': 'Quito',
        'location_string': 'Quito, Ecuador',
        'countrycode': 'EC',
        'account_info': '⭐BANCO GUAYAQUIL⭐TODOS LOS BANCOS⭐',
        'bank_name': '⭐BANCO GUAYAQUIL⭐TODOS LOS BANCOS⭐',
        'msg': 'NO SE ADMITEN TRANSFERENCIAS DE TERCEROS\n'\
                'El nombre del titular de la transferencia debe coincidir con el titular de la cuenta de localbitcoins para liberar los btc\n\n'\
                'Al ofertar aceptas los terminos\n\n'\
                'Transferencia⭐o deposito⭐.\n\n'\
                'En la referencia de pago debes poner pago de servicios no reembolsable\n\n'\
                'TELEGRAM: @sromeroBTC1\n\nEnglish spoken',
        'sms_verification_required': True,
        'track_max_amount': True,
        'require_trusted_by_advertiser': False,
        'require_identification': True,
        'opening_hours': '[[38, 80], [35, 88], [35, 88], [35, 90], [35, 88], [35, 88], [36, 80]]',
    }
    currency_compra = 'COP'
    vender_solo = False
    vendedor = Vendedor(porcentaje_de_ganancia, minimo, comision_local, currency, ad_id,key, secret, parametros,currency_compra, vender_solo)
    vendedor.update_price()
        
    