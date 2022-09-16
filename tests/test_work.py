from locale import currency
import unittest
from agentes.notificador import Notificador, NotificadorCompra
from agentes.vendedor import Vendedor

from settings.settings import BOT_TOKEN, MX_KEY, MX_SECRET


class TestWork(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        currency1 = 'COP'
        currency = 'CRC'
        currency_venta = 'CRC'
        id_ad2 = '1352295'
        id_ad = '1381456'
        sleep_time = 30
        receptor = 'sergio'
        receptores = {
                    'sergio': 'Bancolombia \n Sergio Romero Romero \n\n No cuenta ahorros \n 820-481762-98 '

                    }
        verificador = '' #btc_group
        verificador2 = '' #btc_group
        administrador = '333685986' #sergio
        enviar_mensaje = False
        expresiones_regex = [r'\D\D\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d\s\D', r'CR([-\s]?\d{4}){5}']

        self.notificador = Notificador(BOT_TOKEN, currency, id_ad,MX_KEY, MX_SECRET, sleep_time, receptor, receptores, verificador, administrador,enviar_mensaje,verificador2) 

        self.notificador_compra = NotificadorCompra(BOT_TOKEN, currency, id_ad,MX_KEY, MX_SECRET, sleep_time, receptor, receptores, verificador, administrador, enviar_mensaje,verificador2, currency_venta, expresiones_regex)


    def test_llamada_notificaciones(self):
        notificador = self.notificador
        rate = float(notificador.get_precio_de_cambio('MXN'))
        self.assertGreaterEqual(rate, 185.0)

    def test_identificar_cuenta(self):
        nc = self.notificador_compra
        conn = nc.conectar()
        notificacion = {
            'read': True, 
            'created_at': '2022-09-01T23:26:07+00:00', 
            'msg': '¡Tiene una nueva oferta de #78952833!', 
            'url': '/contact/3RH1i1M8XLG8mkpSBQBap/online_buy_buyer', 
            'id': '078efcfed55f', 
            'contact_id': 78952833}
        num_cuenta,cuenta1,cuenta2,enviado = nc.identificar_cuenta(notificacion,  conn)
        self.assertTrue(num_cuenta)

    def test_info(self):
        info = {'primero': {
            'name': 'Chepegabino', 
            'price': 412943.05, 
            'min_amount': 200.0, 
            'max_amount': 1612.67, 
            'trade_count': 70.0, 
            'feedback_score': 100.0, 
            'currency': 'MXN'
            }, 'segundo': {'name': 'tutsidelopez', 'price': 413750.37, 'min_amount': 100.0, 'max_amount': 370.0, 'trade_count': 700.0, 'feedback_score': 100.0, 'currency': 'MXN'}, 'tercero': {'name': 'rperez91', 'price': 418254.19, 'min_amount': 1000.0, 'max_amount': 44854.6, 'trade_count': 300.0, 'feedback_score': 100.0, 'currency': 'MXN'}, 'cuarto': {'name': 'r2d2cuevas', 'price': 418594.27, 'min_amount': 100.0, 'max_amount': 3242.63, 'trade_count': 4000.0, 'feedback_score': 99.0, 'currency': 'MXN'}, 'quinto': {'name': 'r2d2cuevas', 'price': 418594.27, 'min_amount': 100.0, 'max_amount': 3242.63, 'trade_count': 4000.0, 'feedback_score': 99.0, 'currency': 'MXN'}, 'sexto': {'name': 'albalfre17', 'price': 419805.25, 'min_amount': 500.0, 'max_amount': 2948.79, 'trade_count': 2000.0, 'feedback_score': 100.0, 'currency': 'MXN'}, 'septimo': {'name': 'huachix', 'price': 419805.25, 'min_amount': 9000.0, 'max_amount': 63365.45, 'trade_count': 400.0, 'feedback_score': 100.0, 'currency': 'MXN'}, 'octavo': {'name': 'myacdoomk', 'price': 423841.84, 'min_amount': 1000.0, 'max_amount': 13526.36, 'trade_count': 300.0, 'feedback_score': 99.0, 'currency': 'MXN'}, 'noveno': {'name': 'huachix', 'price': 423841.84, 'min_amount': 10000.0, 'max_amount': 63974.73, 'trade_count': 400.0, 'feedback_score': 100.0, 'currency': 'MXN'}}

        porcentaje_de_ganancia = 1.09
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
        v = Vendedor(porcentaje_de_ganancia, minimo, comision_local, currency, ad_id,key, secret, parametros,currency_compra)
        conn = v.conectar()
        precio, mmin, mmax = v.precio_actual(conn)
        price = v.recorrer_puestos(info,conn)
        print(precio, mmin,mmax )
        self.assertEqual(price, 413750.37)


if __name__ == '__main__':
    unittest.main()