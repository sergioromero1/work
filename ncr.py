from agentes.notificador import Notificador
from settings.settings import BOT_TOKEN, CR_KEY, CR_SECRET
import sys

if __name__ == "__main__":
    currency = 'CRC'
    id_ad = '1381456'
    sleep_time = 20
    receptor = sys.argv[1]
    receptores = {'kozel': 'BAC \n Fernando Josue Kozel Borbon \n\n Numero de cuenta Bac \n 941235723  \n\n Número de cuenta IBAN \n '\
                        'CR36010200009412357238\n\n SINPE MOVIL: 63847393 \n\n En el concepto/referencia escribe: Servicios tecnicos',

                    'leo': 'BAC \n Leonel Moises Arley Esteller \n\n Numero de cuenta Bac \n 947162996  \n\n Número de cuenta IBAN \n '\
                        'CR25010200009471629965\n\n SINPE MOVIL: 62803209 \n\n En el concepto/referencia escribe: Servicios tecnicos',

                    'mama': 'BAC \n Briceidy Borbon Picado \n\n Numero de cuenta Bac \n 947245270  \n\n Número de cuenta IBAN \n '\
                        'CR26010200009472452701\n\n SINPE MOVIL: 88275537 \n\n En el concepto/referencia escribe: Servicios tecnicos',

                    'jose': 'BAC \n JOSE JUAN CAMPOS ALVAREZ \n\n Numero de cuenta Bac \n 947449476  \n\n Número de cuenta IBAN \n '\
                        'CR14010200009474494767\n\n SINPE MOVIL: 62765267 \n\n En el concepto/referencia escribe: Servicios tecnicos',

                    'leo2': 'BN \n ARLEY ESTELLER LEONEL MOI \n\n Numero de cuenta cliente \n 200-01-016-045179-3  \n\n Número de cuenta IBAN \n '\
                        'CR88015101620010451793\n\n No SINPE MOVIL por el momento \n\n En el concepto/referencia escribe: Servicios tecnicos'
                
                    }
    verificador = '1526093626' #kozel
    key = CR_KEY
    secret = CR_SECRET
    bot_token = BOT_TOKEN
    notificador = Notificador(bot_token, currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador) 
    notificador.iniciar()


