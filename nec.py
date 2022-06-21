from agentes.notificador import Notificador
from settings.settings import BOT_TOKEN, MX_KEY, MX_SECRET
import sys

if __name__ == "__main__":
    currency = 'USD'
    id_ad = '1458177'
    sleep_time = 30
    receptor = sys.argv[1]
    receptores = {'alejandro': 'ALEJANDRO RODRIGUEZ \n\n BANCO PICHINCHA\n No de cuenta   2205166757'\
                            'BANCO GUAYAQUIL \n No de cuenta   0030968268'
                    }
    verificador = '5364458308' #'alejandro
    verificador2 = ''
    administrador = '333685986' #sergio
    key = MX_KEY
    secret = MX_SECRET
    bot_token = BOT_TOKEN
    enviar_mensaje = True
    notificador = Notificador(bot_token, currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador, administrador,enviar_mensaje,verificador2) 
    notificador.iniciar()



