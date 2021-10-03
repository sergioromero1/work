from agentes.comprador import Comprador
from settings.settings import COMPRA_KEY, COMPRA_SECRET

import sys

if __name__ == "__main__":

    posicion= sys.argv[1]
    currency = 'USDT'
    ad_id = '1407331'
    key = COMPRA_KEY
    secret = COMPRA_SECRET
    comprador = Comprador(currency, ad_id, posicion, key, secret)
    comprador.update_price()
    
        
    
