from agentes.notificador import Notificador, NotificadorCompra , NotificadorVentaCostaRica
from agentes.vendedor import Vendedor
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
    print(notificaciones)

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
    # print(contact_mesages)
    # lista_liberados = conn.call(method='GET', url=f'/api/dashboard/released/').json()['data']['contact_list']
    # print(lista_liberados)

def info_pais():
    porcentaje_de_ganancia = 1.09
    minimo = 50
    comision_local = 0.01
    currency = 'MXN'
    ad_id = '1261529'
    key = MX_KEY
    secret = MX_SECRET
    parametros={
        'lat': 0,
        'lon': 0,
        'city': 'Mexico City',
        'location_string': 'Mexico City, CDMX, Mexico',
        'countrycode': 'MX',
        'account_info': '⭐SPEI⭐OXXO⭐',
        'bank_name': '⭐SPEI⭐OXXO⭐TODOS LOS BANCOS⭐',
        'msg': 'Transferencia⭐SPEI⭐o deposito en ⭐OXXO⭐. Todos los bancos con Mexican Peso (MXN)\n\nCualquier duda estoy a sus ordenes, Gracias!!\n\n'\
                'Si no vas a hacer el pago en los 90 minutos correspondientes, no envíes dinero.\n\n'\
                'Si haces triangulación (no eres tu quien esta consignando o transfiriendo directamente) y no envías el recibo dentro de los tiempos estipulados'\
                ' en el comercio corres el riesgo de ser bloqueado.\n\nSi haces triangulación ( no eres tu quien esta consignando o transfiriendo directamente) y no'\
                ' envías el comprobante en 90 minutos corres el riesgo de que tus BTC sean liberados mucho después o de que se agoten los BTC y te sea devuelto el dinero, '\
                'en ese caso te atendemos por\nt3legr4m: @sromeroBTC1', 
        'sms_verification_required': True,
        'track_max_amount': True,
        'require_trusted_by_advertiser': False,
        'require_identification': True,
        'opening_hours': '[[38, 80], [35, 88], [35, 88], [35, 90], [35, 88], [35, 88], [36, 80]]',
    }
    currency_compra = 'COP'
    v = Vendedor(porcentaje_de_ganancia, minimo, comision_local, currency, ad_id,key, secret, parametros,currency_compra)
    conn = v.conectar()
    # com = v.informacion_comerciantes(conn)
    # response = conn.call(method='GET',url= f'/buy-bitcoins-online/{currency}/.json')
    # values = response.json()
    username = 'sromero'
    # my_self = conn.call(method='GET',url= f'/api/account_info/{username}/')
    # m = float(my_self.json()['data']['confirmed_trade_count_text'].replace('+',''))
    # print(m)

    # data = conn.call(method='GET',url= f'/buy-bitcoins-online/CRC/.json')
    # ad = data.json()['data']['ad_list']
    # uno = float(ad[2]['data']['max_amount_available'])
    # dos = float(ad[2]['data']['profile']['trade_count'].replace('+','').replace(' ',''))
    # tres = float(ad[2]['data']['profile']['feedback_score'])
    # cuatro = str(ad[2]['data']['currency'])

    # print(uno,dos,tres,cuatro)
    enviar_mensaje = conn.call(method='POST', url= f'/api/contact_message_post/79036484/', params={'msg': f'hola'})
    # info = v.informacion_comerciantes(conn)
    print(enviar_mensaje)

def info_pais2():
    currency = 'MXN'
    id_ad = '1261529'
    sleep_time = 30
    receptor = 'ivan'
    receptores = {'irene': 'Hola \n BBVA Bancomer \n Maria Irene Martinez \n\n Para pago en oxxo y transferencia \n tarjeta debito \n\n 4152 3137 5463 8984 \n '\
                        '002180701431343757',

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
    # mensaje = notificador.get_message_nuevo_comercio()
    conn = notificador.conectar()
    contact_id = 79125664
    mensaje_nuevo_comercio = '#'
    noti = {
        'read': True, 
        'created_at': '2022-09-01T23:26:07+00:00', 
        'msg': '¡Tiene una nueva oferta de #78952833!', 
        'url': '/contact/3RH1i1M8XLG8mkpSBQBap/online_buy_buyer', 
        'id': '078efcfed55f', 
        'contact_id': 78952833}
    # notificador.send_msg_contact(conn,contact_id, mensaje_nuevo_comercio, f'Mensaje nuevo comercio enviado #{contact_id}',verbose=True)
    # notificador.marcar_notificacion_como_leida(conn,noti,f'Nuevo comercio #{contact_id}')
    print(conn.call(method='GET', url=f'/api/contact_messages/{79124706}/').json()['data']['message_list'])

if __name__ == "__main__":
    get_notification()