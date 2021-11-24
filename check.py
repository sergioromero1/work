from agentes.revisor import Revisor
from settings.settings import BOT_TOKEN, CR_KEY, CR_SECRET

if __name__ == "__main__":

    sleep_time = 900            
    verificador = '333685986' #sergio
    key = CR_KEY
    secret = CR_SECRET
    bot_token = BOT_TOKEN
    revisor = Revisor(bot_token, key, secret, sleep_time, verificador) 
    revisor.revisar()