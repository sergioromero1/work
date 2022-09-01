from agentes.notificador import NotificadorVentaCostaRica
from settings.settings import BOT_TOKEN, CR_KEY, CR_SECRET
import sys

if __name__ == "__main__":
    currency = 'CRC'
    id_ad = '1381456'
    sleep_time = 25
    receptor = sys.argv[1]
    receptores = {'kozel': 'Hola \n BAC \n Fernando Josue Kozel Borbon \n\n Numero de cuenta Bac \n 941235723  \n\n Número de cuenta IBAN \n '\
                        'CR36010200009412357238\n\n SINPE MOVIL: 63847393 \n\n En el concepto/referencia escribe: Servicios tecnicos',

                    'leo': 'Hola \n BAC \n Leonel Moises Arley Esteller \n\n Numero de cuenta Bac \n 947162996  \n\n Número de cuenta IBAN \n '\
                        'CR25010200009471629965\n\n SINPE MOVIL: 62803209 \n\n En el concepto/referencia escribe: Servicios tecnicos',

                    'mama': 'Hola \n BAC \n Briceidy Borbon Picado \n\n Numero de cuenta Bac \n 947245270  \n\n Número de cuenta IBAN \n '\
                        'CR26010200009472452701\n\n SINPE MOVIL: 88275537 \n\n En el concepto/referencia escribe: Servicios tecnicos',

                    'jose': 'Hola \n BAC \n JOSE JUAN CAMPOS ALVAREZ \n\n Numero de cuenta Bac \n 947449476  \n\n Número de cuenta IBAN \n '\
                        'CR14010200009474494767\n\n SINPE MOVIL: 62765267 \n\n En el concepto/referencia escribe: Servicios tecnicos',

                    'pamela':'Hola \n BAC \n Reichell Pamela Delgado nuñez \n\n Numero de cuenta Bac \n 948390729 \n\n Número de cuenta IBAN \n '\
                        'CR93010200009483907292\n\n SINPE MOVIL: 61766052 \n\n En el concepto/referencia escribe: Servicios tecnicos',

                    'leo2': 'Hola \n BN \n Leonel Moises Arley Esteller \n\n Numero de cuenta cliente \n 200-01-016-045179-3  \n\n Número de cuenta IBAN \n '\
                        'CR88015101620010451793\n\n SINPE MOVIL 61691986 \n\n En el concepto/referencia escribe: Servicios tecnicos',

                    'papa': 'Hola \n BCR \n Fernando Delgado Solis \n\n Número de cuenta IBAN \n '\
                        'CR63015202001238749106\n\n Si es por SINPE MOVIL 61342921\n A nombre de Briceidy Borbon Picado \n\n En el concepto/referencia escribe: Servicios tecnicos',

                    'mama2':'Hola \n BCR \n Briceidy Borbon Picado \n\n Número de cuenta IBAN \n '\
                        'CR48015202220002751406\n\n SINPE MOVIL: 61509538 \n\n En el concepto/referencia escribe: Servicios tecnicos',

                    }
                    
    verificador = '1526093626' #kozel
    verificador2 = ''
    administrador = '333685986' #sergio
    key = CR_KEY
    secret = CR_SECRET
    bot_token = BOT_TOKEN
    enviar_mensaje = True
    clientes_dc = ['josedmarin','Djpb0102', 'camedina11', 'elissakmd', 'DanielRuiz11', 'Ricardo8830', 'EileenArguedasM', 'Ricardo8830', 'ailak', 'grios14', 'cris_sulbaran','nazuaje','ERNESTONE','jevale310879','Andréssanchez20']
    notificador = NotificadorVentaCostaRica(bot_token, currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador, administrador,enviar_mensaje, verificador2) 
    notificador.iniciar()



