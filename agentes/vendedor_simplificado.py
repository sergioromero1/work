from agentes.vendedor import Vendedor
from decoradores.loop import loop
from utils.color import Color
import csv
import datetime
import os
import time

class VendedorSimplificado(Vendedor):

    @loop
    def update_price(self):

        """Actualiza el precio teniendo en cuenta un precio limite 
            total y posicion deseada. Cuando hay un cambio abrubto
            de mas de 300 MXN descansa por unos minutos.
        """

        currency, = self.get_atributos("currency")
        conn = self.conectar()

        while True:

            self.escribir_saldo_dia_anterior()

            precio_limite_total = 117_500_000
            
            if precio_limite_total is None:
                print(f'No hay btc', flush=True)
                time.sleep(30)
                continue

            print(precio_limite_total, flush=True)

            print(f'\nrunning...{currency[0:2]}\n', flush=True)

            info = self.informacion_comerciantes(conn)
            
            if len(info) > 0:
                precio_del_otro = self.recorrer_puestos(info, conn)
            else:
                self.precio_limite_alcanzado(conn, precio_limite_total)
                continue

            if precio_del_otro < float(precio_limite_total):

                self.precio_limite_alcanzado(conn, precio_limite_total)
                continue

            if self.vender_solo:
                precio_de_inicio,_,_ = self.adelantar(precio_del_otro, conn)
            else:
                precio_de_inicio,_,_ = self.adelantar_beta(precio_del_otro, conn)
            
            delta_de_precio = 0

            while delta_de_precio < precio_de_inicio*0.01:
                start_time = time.time()
                print('\nrunning...combat\n', flush=True)
                mi_precio, _, _ = self.precio_actual(conn)
                info = self.informacion_comerciantes(conn)
                
                if mi_precio > precio_limite_total:

                    precio_del_otro = self.recorrer_puestos(info, conn)
                    if self.vender_solo:
                        self.adelantar(precio_del_otro, conn)
                    else:
                        self.adelantar_beta(precio_del_otro, conn)

                else:
                    self.precio_limite_alcanzado(conn, precio_limite_total)

                mi_nuevo_precio,_,_ = self.precio_actual(conn)

                delta_de_precio = precio_de_inicio - mi_nuevo_precio
                end_time = time.time()
                duracion = end_time - start_time    
                print(self.format_time(duracion), f'El delta de precio es: {delta_de_precio}', flush=True)
                time.sleep(30)

            else:
                self.descansar(conn)