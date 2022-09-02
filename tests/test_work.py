from locale import currency
import unittest
from agentes.notificador import Notificador, NotificadorCompra
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


if __name__ == '__main__':
    unittest.main()