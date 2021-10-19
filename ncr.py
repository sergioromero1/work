from agentes.notificador import Notificador
from settings.settings import BOT_TOKEN, CR_KEY, CR_SECRET
import sys

if __name__ == "__main__":
    currency = 'CRC'
    id_ad = '1381456'
    sleep_time = 20
    receptor = sys.argv[1]
    receptores = {'kozel': 'BAC \n Fernando Josue Kozel Borbon \n\n Numero de cuenta Bac \n 941235723  \n\n Número de cuenta IBAN \n '\
                        'CR36010200009412357238\n\n SINPE MOVIL: 63847393 \n\n En el concepto/referencia escribe: Servicios tecnicos'\
                        # '\n Si el nombre del titular de la transferencia no coincide con el titular de la cuenta de localbitcoins debes poner: Servicios tecnicos no reembolsable',
                        '\n Si el monto es mayor a 12000 CRC El nombre del titular de la transferencia debe coincidir con el titular de la cuenta de localbitcoins para liberar los btc',


                    'leo': 'BAC \n Leonel Moises Arley Esteller \n\n Numero de cuenta Bac \n 947162996  \n\n Número de cuenta IBAN \n '\
                        'CR25010200009471629965\n\n SINPE MOVIL: 62803209 \n\n En el concepto/referencia escribe: Servicios tecnicos'\
                        # '\n Si el nombre del titular de la transferencia no coincide con el titular de la cuenta de localbitcoins debes poner: Servicios tecnicos no reembolsable',
                        '\n Si el monto es mayor a 12000 CRC El nombre del titular de la transferencia debe coincidir con el titular de la cuenta de localbitcoins para liberar los btc',


                    'mama': 'BAC \n Briceidy Borbon Picado \n\n Numero de cuenta Bac \n 947245270  \n\n Número de cuenta IBAN \n '\
                        'CR26010200009472452701\n\n SINPE MOVIL: 88275537 \n\n En el concepto/referencia escribe: Servicios tecnicos'\
                        # '\n Si el nombre del titular de la transferencia no coincide con el titular de la cuenta de localbitcoins debes poner: Servicios tecnicos no reembolsable',
                        '\n Si el monto es mayor a 12000 CRC El nombre del titular de la transferencia debe coincidir con el titular de la cuenta de localbitcoins para liberar los btc',


                    'jose': 'BAC \n JOSE JUAN CAMPOS ALVAREZ \n\n Numero de cuenta Bac \n 947449476  \n\n Número de cuenta IBAN \n '\
                        'CR14010200009474494767\n\n SINPE MOVIL: 62765267 \n\n En el concepto/referencia escribe: Servicios tecnicos'\
                        # '\n Si el nombre del titular de la transferencia no coincide con el titular de la cuenta de localbitcoins debes poner: Servicios tecnicos no reembolsable',
                        '\n Si el monto es mayor a 12000 CRC El nombre del titular de la transferencia debe coincidir con el titular de la cuenta de localbitcoins para liberar los btc',


                    'leo2': 'BN \n Leonel Moises Arley Esteller \n\n Numero de cuenta cliente \n 200-01-016-045179-3  \n\n Número de cuenta IBAN \n '\
                        'CR88015101620010451793\n\n SINPE MOVIL 61691986 \n\n En el concepto/referencia escribe: Servicios tecnicos'\
                        # '\n Si el nombre del titular de la transferencia no coincide con el titular de la cuenta de localbitcoins debes poner: Servicios tecnicos no reembolsable',
                        '\n Si el monto es mayor a 12000 CRC El nombre del titular de la transferencia debe coincidir con el titular de la cuenta de localbitcoins para liberar los btc',


                    'papa': 'BCR \n Fernando Delgado Solis \n\n Número de cuenta IBAN \n '\
                        'CR63015202001238749106\n\n Si es por SINPE MOVIL 61342921\n A nombre de Briceidy Borbon Picado \n\n En el concepto/referencia escribe: Servicios tecnicos'\
                        # '\n Si el nombre del titular de la transferencia no coincide con el titular de la cuenta de localbitcoins debes poner: Servicios tecnicos no reembolsable',
                        '\n Si el monto es mayor a 12000 CRC El nombre del titular de la transferencia debe coincidir con el titular de la cuenta de localbitcoins para liberar los btc',


                    'mama2': 'BCR \n Briceidy Borbon Picado \n\n Número de cuenta IBAN \n '\
                        'CR48015202220002751406\n\n SINPE MOVIL: 61509538 \n\n En el concepto/referencia escribe: Servicios tecnicos'\
                        # '\n Si el nombre del titular de la transferencia no coincide con el titular de la cuenta de localbitcoins debes poner: Servicios tecnicos no reembolsable'
                        '\n Si el monto es mayor a 12000 CRC El nombre del titular de la transferencia debe coincidir con el titular de la cuenta de localbitcoins para liberar los btc',
                    }
                    
    verificador = '1526093626' #kozel
    key = CR_KEY
    secret = CR_SECRET
    bot_token = BOT_TOKEN
    notificador = Notificador(bot_token, currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador) 
    notificador.iniciar()



