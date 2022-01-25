import unittest
from agentes.notificador import Notificador
from settings.settings import BOT_TOKEN, MX_KEY, MX_SECRET


class TestWork(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        currency = 'COP'
        id_ad = '1352295'
        sleep_time = 30
        receptor = 'sergio'
        receptores = {
                    'sergio': 'Bancolombia \n Sergio Romero Romero \n\n No cuenta ahorros \n 820-481762-98 '

                    }
        verificador = '333685986' #btc_group
        administrador = '333685986' #sergio
        enviar_mensaje = False
        self.work = Notificador(BOT_TOKEN, currency, id_ad,MX_KEY, MX_SECRET, sleep_time, receptor, receptores, verificador,administrador,enviar_mensaje)

    def test_llamada_notificaciones(self):
        notificador = self.work
        rate = float(notificador.get_precio_de_cambio('MXN'))
        self.assertGreaterEqual(rate, 185.0)

if __name__ == '__main__':
    unittest.main()