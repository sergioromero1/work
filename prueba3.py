


def get_message_nuevo_comercio():

        receptores = {'irene': 'Hola \n BBVA Bancomer \n Maria Irene Martinez \n\n Para pago en oxxo y transferencia \n tarjeta debito \n\n 4152 3137 5463 8984 \n '\
                        '002180701431343757',

                    'cristina': 'Hola \n BBVA Bancomer \n Cristina Nolasco \n\n Para pago en oxxo \n 4152 3135 9796 3326  \n\n Para Transferencia SPEI \n '\
                        '012180015420804899',

                    'ivan': 'Hola \n BBVA Bancomer \n Edgar Ivan Hernandez \n\n Para pago en oxxo \n 4152 3137 6809 4521  \n\n Para Transferencia SPEI \n '\
                        '012818015379048405',

                    'sergio': 'Hola \n HSBC \n Sergio Romero Romero \n\n Para pago en oxxo \n 4830 3031 5122 5386  \n\n Para Transferencia SPEI \n '\
                        '021180040645026366'

                    # 'edgarHSBC': 'Hola \n HSBC \n Edgar Rivas Nolasco \n\n Para pago en oxxo \n 4830 3033 5028 3038  \n\n Para Transferencia SPEI \n '\
                    #     '021180040645025781',

                    # 'edgarBANAMEX': 'Hola \n BANAMEX \n Edgar Rivas Nolasco \n\n Para pago en oxxo \n 5206 9496 4573 4293  \n\n Para Transferencia SPEI \n '\
                    #     '002818701476622446',

                    # 'perfiles': 'Hola \n BANAMEX \n Cristina Nolasco \n\n Para pago en oxxo \n 5204 1651 7729 2392  \n\n Para Transferencia SPEI \n '\
                    #     '002180700913724772'
                    }
        
        receptor = 'ivan'

        """Devuelve el mensaje para nuevo comercio"""

        return receptores[receptor]

print(get_message_nuevo_comercio())
