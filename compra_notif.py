from agentes.notificador import NotificadorCompra
from settings.settings import BOT_TOKEN, COMPRA_KEY, COMPRA_SECRET

if __name__ == "__main__":
    currency = 'COP'
    id_ad = '1240275'
    sleep_time = 20
    receptor = ''
    receptores = {}
    verificador = '1526093626' #kozel
    key = COMPRA_KEY
    secret = COMPRA_SECRET
    bot_token = BOT_TOKEN
    notificador = NotificadorCompra(bot_token, currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador) 
    notificador.iniciar()
        
    



