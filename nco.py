from agentes.notificador import Notificador
from settings.settings import BOT_TOKEN, MX_KEY, MX_SECRET
import sys

if __name__ == "__main__":
    currency = 'COP'
    id_ad = '1352295'
    sleep_time = 30
    receptor = sys.argv[1]
    receptores = {
                    'sergio': 'Hola \n Bancolombia \n Sergio Romero Romero \n\n No cuenta ahorros \n 820-481762-98 '

                    }
    verificador = '333685986' #btc_group
    verificador2 = ''
    administrador = '333685986' #sergio
    key = MX_KEY
    secret = MX_SECRET
    bot_token = BOT_TOKEN
    enviar_mensaje = True
    notificador = Notificador(bot_token, currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador, administrador,enviar_mensaje,verificador2) 
    notificador.iniciar()



