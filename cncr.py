from agentes.notificador import NotificadorCompra
from settings.settings import BOT_TOKEN, COMPRA_KEY, COMPRA_SECRET

if __name__ == "__main__":
    currency = 'CRC'
    currency_venta = 'CRC'
    id_ad = '1397853'
    sleep_time = 40
    receptor = ''
    receptores = {}
    verificador = ''#'1526093626' #kozel
    verificador2 = ''#'5281917452' #leo
    administrador = '333685986' #sergio
    key = COMPRA_KEY
    secret = COMPRA_SECRET
    bot_token = BOT_TOKEN
    enviar_mensaje = True
    expresiones_regex = [r'\D\D\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d\s\D', r'CR([-\s]?\d{4}){5}']
    notificador = NotificadorCompra(bot_token, currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador, administrador, enviar_mensaje,verificador2, currency_venta, expresiones_regex) 
    notificador.iniciar()