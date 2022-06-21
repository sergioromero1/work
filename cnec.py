from agentes.notificador import NotificadorCompra
from settings.settings import BOT_TOKEN, COMPRA_KEY, COMPRA_SECRET

if __name__ == "__main__":
    currency = 'COP'
    currency_venta = 'USD'
    id_ad = '1366009'
    sleep_time = 30
    receptor = ''
    receptores = {}
    verificador = '5364458308' #alejandro
    verificador2 = '' 
    administrador = '333685986' #sergio
    key = COMPRA_KEY
    secret = COMPRA_SECRET
    bot_token = BOT_TOKEN
    enviar_mensaje = True
    notificador = NotificadorCompra(bot_token, currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador, administrador, enviar_mensaje,verificador2, currency_venta) 
    notificador.iniciar()