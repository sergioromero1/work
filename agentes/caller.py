from .conectar import Connection

class Caller:

    def __init__(self, ad_id,key, secret, parametros):

        self.ad_id = ad_id
        self.key = key
        self.secret = secret
        self.parametros = parametros

    def conectar(self,server='https://localbitcoins.com'):

        """Se conecta a local bitcoins"""

        key, secret = self.get_atributos("key", "secret")
        conn = Connection()
        conn._set_hmac(server, key, secret)
        
        return conn

    def get_atributos(self, *nombres: str):
        """Retorna los atributos solicitados como una tupla"""

        return (self.__dict__[nombre] for nombre in nombres)

    