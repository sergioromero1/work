from agentes.notificador2 import Notificador
from settings.settings import BOT_TOKEN, MX_KEY, MX_SECRET
import sys

if __name__ == "__main__":
    currency = 'MXN'
    id_ad = '1261529'
    sleep_time = 30
    receptor = sys.argv[1]
    receptores = {'irene': 'Hola \n BBVA Bancomer \n Maria Irene Martinez \n\n Para pago en oxxo \n 4152 3137 5463 8984  \n\n Para Transferencia SPEI \n '\
                        '012818015381863212',

                'cristina': 'Hola \n BBVA Bancomer \n Cristina Nolasco \n\n Para pago en oxxo \n 4152 3135 9796 3326  \n\n Para Transferencia SPEI \n '\
                        '012180015420804899',

                'ivan': 'Hola \n BBVA Bancomer \n Edgar Ivan Hernandez \n\n Para pago en oxxo \n 4152 3137 6809 4521  \n\n Para Transferencia SPEI \n '\
                        '012818015379048405',

                }
    verificador = '' #'-1001215642574' #btc_group
    verificador2 = ''
    administrador = '333685986' #sergio
    key = MX_KEY
    secret = MX_SECRET
    bot_token = BOT_TOKEN
    enviar_mensaje = True
    notificador = Notificador(bot_token, currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador, administrador,enviar_mensaje,verificador2) 
    notificador.iniciar()



