from agentes.notificador import NotificadorCompra
import requests
from settings.settings import BOT_TOKEN, MX_KEY, MX_SECRET



def atender_nuevo_mensaje():

        aceptado = True
        attachment = False
        enviado = False
        enviado_despues_de_aceptado = False
        payed = False
        
        if aceptado and not enviado_despues_de_aceptado:
            print('hola')

def sendt():
    bot_message = 'hola alejo '
    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + '5364458308' + '&parse_mode=Markdown&text=' + bot_message
    response = requests.post(send_text)
    print(response.json()['ok'])

def get_notification():
    currency = 'CRC'
    currency_venta = 'CRC'
    id_ad = '1381456'
    sleep_time = 30
    receptor = 'sergio'
    receptores = {
                'sergio': 'Bancolombia \n Sergio Romero Romero \n\n No cuenta ahorros \n 820-481762-98 '

                }
    verificador = '' #btc_group
    verificador2 = '' #btc_group
    administrador = '333685986' #sergio
    enviar_mensaje = True
    expresiones_regex = [r'\D\D\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d[-\s]?\d\s\D', r'CR([-\s]?\d{4}){5}']

    nc = NotificadorCompra(BOT_TOKEN, currency, id_ad,MX_KEY, MX_SECRET, sleep_time, receptor, receptores, verificador, administrador, enviar_mensaje,verificador2, currency_venta, expresiones_regex)
    conn = nc.conectar()
    response = conn.call(method='GET', url='/api/notifications/')
    notificaciones = response.json()['data']
    print(notificaciones[2])

    notificacion = {
        'read': True, 
        'created_at': '2022-09-01T23:26:07+00:00', 
        'msg': '¡Tiene una nueva oferta de #78952833!', 
        'url': '/contact/3RH1i1M8XLG8mkpSBQBap/online_buy_buyer', 
        'id': '078efcfed55f', 
        'contact_id': 78952833}
    # num_cuenta,cuenta1,cuenta2,enviado = nc.identificar_cuenta(notificacion,  conn)
    # print(enviado)
    # nc.marcar_notificacion_como_leida(conn,notificacion,descripcion='Nuevo comercio')
    # nc.notificar_cuenta_identificada(notificacion,conn,'00000','11111')
    # var=nc.identificar_ad_id(notificacion,conn)
    # contact_info  = nc.get_contact_info(conn,notificacion['contact_id'])
    # print(contact_info)
    contact_info2 = {
        'created_at': '2022-09-01T23:26:07+00:00',
        'buyer': {'username': 'sromero', 'trade_count': '2000+',
        'feedback_score': 100, 'name': 'sromero (2000+; 100%)',
        'last_online': '2022-09-02T15:53:29+00:00'},
        'seller': {
            'username': 'Melon89CR',
            'trade_count': '50+',
            'feedback_score': 100,
            'name': 'Melon89CR (50+; 100%)',
            'last_online': '2022-09-02T00:01:28+00:00'
            },
        'is_buying': True,
        'is_selling': False,
        'currency': 'CRC',
        'amount': '40089.12',
        'amount_btc': '0.00326500',
        'fee_btc': '0.00003265',
        'exchange_rate_updated_at': '2022-09-01T23:26:07+00:00',
        'payment_completed_at': '2022-09-01T23:44:41+00:00',
        'escrowed_at': '2022-09-01T23:26:07+00:00',
        'funded_at': '2022-09-01T23:26:07+00:00',
        'canceled_at': None, 'released_at': '2022-09-01T23:58:16+00:00',
        'disputed_at': None, 'closed_at': '2022-09-01T23:58:16+00:00',
        'contact_id': 78952833,
        'advertisement': {
            'id': 1397853,
            'trade_type': 'ONLINE_BUY',
            'advertiser': {
                'username': 'sromero',
                'trade_count': '2000+',
                'feedback_score': 100,
                'name': 'sromero (2000+; 100%)',
                'last_online': '2022-09-02T15:53:29+00:00'
                },
            'payment_method': 'SPECIFIC_BANK'
            },
        'reference_code': 'L78952833B1B08E9',
        'account_info': 'Transferencia⭐BAC⭐SINPE⭐RAPIDO⚡️️️'
    }
    # contact_mesages  = nc.get_contact_messages(conn,  notificacion['contact_id'])
    print(contact_mesages)



if __name__ == "__main__":
    get_notification()