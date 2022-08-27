from .conectar import Connection
from decoradores.loop import loop
import time
import requests

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

class Notificador(Caller):

    def __init__(self, ad_id,key, secret, parametros, bot_token,enviar_mensaje,verificador,administrador, sleep_time,tipo):
        super().__init__(ad_id,key, secret, parametros)
        self.bot_token = bot_token
        self.enviar_mensaje = enviar_mensaje
        self.verificador = verificador
        self.administrador = administrador
        self.sleep_time = sleep_time
        self.tipo =tipo
    
    def is_active(self,conn):

        ad_id, = self.get_atributos("ad_id")
        response = conn.call(method='GET', url= f'/api/ad-get/', params={'ads': {ad_id}})
        ad = response.json()['data']['ad_list'][0]['data']
        visible = ad['visible']

        return visible

    def sendtext(self, receptores, bot_message):

        bot_token, enviar_mensaje = self.get_atributos("bot_token", "enviar_mensaje")
        if enviar_mensaje:
            for receptor in receptores:
                send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + receptor + '&parse_mode=Markdown&text=' + bot_message
                response = requests.post(send_text)
                
                return response.json()['ok']

    @loop
    def iniciar(self):

        while True:
            self.activar()
            time.sleep(int(self.sleep_time))

    def activar(self):
        administrador, tipo, verificador, enviar_mensaje = self.get_atributos("administrador", "tipo", "verificador", "enviar_mensaje")
        conn = self.conectar()
        se_activo = False
        while True:
            print('Revisando estado....', flush=True)
            active = self.is_active(conn)
            
            if active and not se_activo:
                se_activo = True
                if enviar_mensaje:
                    self.sendtext([administrador,verificador],f'El comercio de {tipo} de CR está PRENDIDO -- PRENDIDO')

            if not active and se_activo:
                se_activo = False
                if enviar_mensaje:
                    self.sendtext([administrador,verificador],f'El comercio de {tipo} de CR está APAGADO')

    