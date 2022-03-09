from agentes.notificador import Notificador
from settings.settings import BOT_TOKEN, MX_KEY, MX_SECRET
import sys

if __name__ == "__main__":
    currency = 'MXN'
    id_ad = '1261529'
    sleep_time = 30
    receptor = sys.argv[1]
    receptores = {'cristina': 'BANAMEX \n Cristina Nolasco \n\n Para pago en oxxo \n 5206 9496 3512 8290  \n\n Para Transferencia SPEI \n '\
                        '002180701431343757',

                    'bbva': 'BBVA Bancomer \n Cristina Nolasco \n\n Para pago en oxxo \n 4152 3135 9796 3326  \n\n Para Transferencia SPEI \n '\
                        '012180015420804899',

                    'sergio': 'HSBC \n Sergio Romero Romero \n\n Para pago en oxxo \n 4830 3031 5122 5386  \n\n Para Transferencia SPEI \n '\
                        '021180040645026366',

                    'edgarHSBC': 'HSBC \n Edgar Rivas Nolasco \n\n Para pago en oxxo \n 4830 3033 5028 3038  \n\n Para Transferencia SPEI \n '\
                        '021180040645025781',

                    'edgarBANAMEX': 'BANAMEX \n Edgar Rivas Nolasco \n\n Para pago en oxxo \n 5206 9496 4573 4293  \n\n Para Transferencia SPEI \n '\
                        '002818701476622446',

                    'perfiles': 'BANAMEX \n Cristina Nolasco \n\n Para pago en oxxo \n 5204 1651 7729 2392  \n\n Para Transferencia SPEI \n '\
                        '002180700913724772'
                    }
    verificador = '333685986' #'-1001215642574' #btc_group
    administrador = '333685986' #sergio
    key = MX_KEY
    secret = MX_SECRET
    bot_token = BOT_TOKEN
    enviar_mensaje = True
    notificador = Notificador(bot_token, currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador, administrador,enviar_mensaje) 
    notificador.iniciar()



