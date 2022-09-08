from agentes.notificador import Notificador
from settings.settings import BOT_TOKEN, MX_KEY, MX_SECRET
import sys

if __name__ == "__main__":
    currency = 'MXN'
    id_ad = '1261529'
    sleep_time = 30
    receptor = sys.argv[1]
    receptores = {'cristina': 'Hola \n BANAMEX \n Cristina Nolasco \n\n Para pago en oxxo \n 5206 9496 3512 8290  \n\n Para Transferencia SPEI \n '\
                        '002180701431343757',

                    'bbva': 'Hola \n BBVA Bancomer \n Cristina Nolasco \n\n Para pago en oxxo \n 4152 3135 9796 3326  \n\n Para Transferencia SPEI \n '\
                        '012180015420804899',

                    'ivan': 'Hola \n BBVA Bancomer \n Edgar Ivan Hernandez \n\n Para pago en oxxo \n 4152 3137 6809 4521  \n\n Para Transferencia SPEI \n '\
                        '012818015379048405',

                    'sergio': 'Hola \n HSBC \n Sergio Romero Romero \n\n Para pago en oxxo \n 4830 3031 5122 5386  \n\n Para Transferencia SPEI \n '\
                        '021180040645026366',

                    'edgarHSBC': 'Hola \n HSBC \n Edgar Rivas Nolasco \n\n Para pago en oxxo \n 4830 3033 5028 3038  \n\n Para Transferencia SPEI \n '\
                        '021180040645025781',

                    'edgarBANAMEX': 'Hola \n BANAMEX \n Edgar Rivas Nolasco \n\n Para pago en oxxo \n 5206 9496 4573 4293  \n\n Para Transferencia SPEI \n '\
                        '002818701476622446',

                    'perfiles': 'Hola \n BANAMEX \n Cristina Nolasco \n\n Para pago en oxxo \n 5204 1651 7729 2392  \n\n Para Transferencia SPEI \n '\
                        '002180700913724772'
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



