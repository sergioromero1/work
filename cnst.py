from agentes.notificador import NotificadorCompraCostaRica
from settings.settings import BOT_TOKEN, COMPRA_KEY, COMPRA_SECRET

if __name__ == "__main__":
    currency = 'USDT'
    currency_venta = 'USDT'
    id_ad = '1407331'
    sleep_time = 20
    receptor = ''
    receptores = {}
    verificador = '333685986' #sergio
    administrador = '333685986' #sergio
    key = COMPRA_KEY
    secret = COMPRA_SECRET
    bot_token = BOT_TOKEN
    notificador = NotificadorCompraCostaRica(bot_token, currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador, administrador, currency_venta) 
    notificador.iniciar()