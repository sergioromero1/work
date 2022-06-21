from agentes.apagador import Apagador
from settings.settings import CR_KEY, CR_SECRET

if __name__ == "__main__":

    ad_id = '1397853'
    key = CR_KEY
    secret = CR_SECRET
    parametros={
        'lat': 0,
        'lon': 0,
        'city': 'San José',
        'location_string': 'San José, Costa Rica',
        'countrycode': 'CR',
        'account_info': 'Transferencia⭐BAC⭐SINPE⭐RAPIDO⚡️️️',
        'bank_name': '⭐BAC⭐SINPE⭐RAPIDO⚡️️️',
        'msg':  'Hacemos transferencia sin costo por bac\n'\
                'si es por sinpe se cobra una comision de 2000\n\n'\
                'Al ofertar aceptas los terminos\n\n'\
                'envíanos los siguientes datos\n'\
                'para realizar el pago\n\n'\
                '1. Nombre :\n'\
                '______________\n\n'\
                '2. Numero de Cuenta o sinpe :\n'\
                'xxx-xxxxxx-xx\n\n'\
                'Telegram @sromeroBTC1\n\n'\
                'Cualquier duda estamos a sus ordenes, Gracias!!\n\nEnglish spoken',
        'sms_verification_required': True,
        'track_max_amount': True,
        'require_trusted_by_advertiser': False,
        'require_identification': True,
        'opening_hours': '[[52, 80], [35, 88], [35, 88], [35, 88], [35, 88], [35, 88], [40, 80]]'
    }

    apagador = Apagador(ad_id,key, secret, parametros)
    apagador.actuar()

    