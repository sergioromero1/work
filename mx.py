from agentes.vendedor import Vendedor

from settings.settings import MX_KEY, MX_SECRET
import time

import sys

if __name__ == "__main__":

    precio_limite_total = float(sys.argv[1])
    minimo = 50
    comision_local = 0.01
    currency = 'MXN'
    ad_id = '1261529'
    key = MX_KEY
    secret = MX_SECRET
    parametros={
        'lat': 0,
        'lon': 0,
        'city': 'Mexico City',
        'location_string': 'Mexico City, CDMX, Mexico',
        'countrycode': 'MX',
        'account_info': '⭐SPEI⭐OXXO⭐',
        'bank_name': '⭐SPEI⭐OXXO⭐TODOS LOS BANCOS⭐',
        'msg': 'Transferencia⭐SPEI⭐o deposito en ⭐OXXO⭐. Todos los bancos con Mexican Peso (MXN)\n\nCualquier duda estoy a sus ordenes, Gracias!!\n\n'\
                'Si haces triangulación (no eres tu quien esta consignando o transfiriendo directamente) y no envías el recibo dentro de los tiempos estipulados'\
                ' en el comercio corres el riesgo de ser bloqueado.\n\nSi haces triangulación ( no eres tu quien esta consignando o transfiriendo directamente) y no'\
                ' envías el comprobante en 90 minutos corres el riesgo de que tus BTC sean liberados mucho después o de que se agoten los BTC y te sea devuelto el dinero, '\
                'en ese caso te atendemos por\nt3legr4m: @sromeroBTC1', 
        'sms_verification_required': True,
        'track_max_amount': True,
        'require_trusted_by_advertiser': False,
        'require_identification': True,
        'opening_hours': '[[46, 80], [36, 90], [36, 90], [34, 90], [36, 90], [36, 90], [36, 80]]',
    }
    porcentaje_btc = 0.63936
    vender_solo = True
    vendedor = Vendedor(precio_limite_total, minimo, comision_local, currency, ad_id,key, secret, parametros,porcentaje_btc, vender_solo)
    vendedor.update_price()
        
    