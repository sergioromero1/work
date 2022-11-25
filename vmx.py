from agentes.vendedor import Vendedor

from settings.settings import MX_KEY, MX_SECRET
import time

import sys

if __name__ == "__main__":

    porcentaje_de_ganancia = 1.045
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
                'Si no vas a hacer el pago en los 90 minutos correspondientes, no envíes dinero.\n\n'\
                'Si haces triangulación (no eres tu quien esta consignando o transfiriendo directamente) y no envías el recibo dentro de los tiempos estipulados'\
                ' en el comercio corres el riesgo de ser bloqueado.\n\nSi haces triangulación ( no eres tu quien esta consignando o transfiriendo directamente) y no'\
                ' envías el comprobante en 90 minutos corres el riesgo de que tus BTC sean liberados mucho después o de que se agoten los BTC y te sea devuelto el dinero, '\
                'en ese caso te atendemos por\nt3legr4m: @sromeroBTC1', 
        'sms_verification_required': True,
        'track_max_amount': True,
        'require_trusted_by_advertiser': False,
        'require_identification': True,
        'opening_hours': '[[38, 80], [35, 88], [35, 88], [35, 90], [35, 88], [35, 88], [36, 80]]',
    }
    currency_compra = 'COP'
    vendedor = Vendedor(porcentaje_de_ganancia, minimo, comision_local, currency, ad_id,key, secret, parametros,currency_compra)
    vendedor.update_price()
        
    