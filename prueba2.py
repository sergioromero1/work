from settings.settings import BOT_TOKEN
import requests


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

if __name__ == "__main__":
    sendt()