from agentes.notificador import Notificador
from settings.settings import BOT_TOKEN, MX_KEY, MX_SECRET
import sys

if __name__ == "__main__":
    currency = 'USDT'
    id_ad = '1380529'
    sleep_time = 20
    receptor = sys.argv[1]
    receptores = {'sergio': 'Accounts on Binance Exchange / cuentas de binance p2p : \n\n '\
                                # '0xe377a51c3aacf802fc4e65551a807988380a0cbd\n\n'\
                                'TCR20 :\n THrvgVbWyD14ef2LDkkRZSm9TmWNkBwVdz\n\n'\

                                'BSC  : \n0xe377a51c3aacf802fc4e65551a807988380a0cbd'\
                            # '\n\nAccounts on independent Blockchains / En Blockchains: '\
                                # '\n\n Binance Smart Chain:'\
                            # '\n 0xF01aA7d8983d27231949b98FB6fcB1f578A5faF9'\
                            # '\n\n Trc 20 \n TQcRXoJh77ei1QD6Qitmgy5hU5SiwS3kJy'\
                                }
    verificador = '333685986' #sergio
    key = MX_KEY
    secret = MX_SECRET
    bot_token = BOT_TOKEN
    notificador = Notificador(bot_token, currency, id_ad,key, secret, sleep_time, receptor, receptores, verificador) 
    notificador.iniciar()



