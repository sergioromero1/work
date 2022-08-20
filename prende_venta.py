from agentes.caller import Notificador
from settings.settings import BOT_TOKEN, CR_KEY, CR_SECRET

if __name__ == "__main__":

    currency = 'CRC'
    ad_id = '1381456'
    key = CR_KEY
    secret = CR_SECRET
    verificador = '1526093626' #kozel
    verificador2 = ''
    administrador = '333685986' #sergio
    parametros = {}
    enviar_mensaje = True
    bot_token = BOT_TOKEN
    sleep_time = 10
    tipo = 'venta'
    notif = Notificador(ad_id,key, secret, parametros, bot_token,enviar_mensaje,verificador,administrador, sleep_time,tipo)
    notif.iniciar()