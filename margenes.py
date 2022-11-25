import requests
from bs4 import BeautifulSoup
import sys
from agentes.conectar import Connection
from settings.settings import BOT_TOKEN, MX_KEY, MX_SECRET


COMISION_LOCAL = 0.02

def conectar(server='https://localbitcoins.com'):

    """Se conecta a local bitcoins"""
    
    hmac_key = MX_KEY
    hmac_secret = MX_SECRET
    conn = Connection()
    conn._set_hmac(server, hmac_key, hmac_secret)
    
    return conn

def get_precio_de_cambio(currency):

    page = requests.get(f'https://www.x-rates.com/calculator/?from={currency}&to=COP&amount=1')
    soup = BeautifulSoup(page.text, 'html.parser')

    part1 = soup.find(class_="ccOutputTrail").previous_sibling
    part1 = part1.replace(",","")
    part2 = soup.find(class_="ccOutputTrail").get_text(strip=True)
    rate = f"{part1}{part2}"

    return rate

def informacion_comerciantes(conn, currency, tipo):
    
    """
    Retorna la informacion de los 6 primeros anuncios
    currency : str = abreviatura de la divisa
    tipo: str = buy o sell dependiendo si es compra o venta
    """

    response = conn.call(method='GET',url= f'/{tipo}-bitcoins-online/{currency}/.json')
    ad = response.json()['data']['ad_list']
    info = {}
    for posicion in range(len(ad)):
        info[f'{posicion}'] = {}
    
    position = 0
    for inside_dict in info.values():
        
        inside_dict['name'] = str(ad[position]['data']['profile']['username'])
        inside_dict['price'] = float(ad[position]['data']['temp_price'])
        inside_dict['min_amount'] = float(ad[position]['data']['min_amount']) if ad[position]['data']['min_amount'] is not None else 0
        inside_dict['max_amount'] = float(ad[position]['data']['max_amount_available']) if ad[position]['data']['max_amount_available'] is not None else 0

        position += 1

    return info

def margen(conn, currency, mmin, mmax):
    
    precio_compra = precio(conn, currency, mmin, mmax, 'sell')
    precio_venta = precio(conn, currency, mmin, mmax, 'buy')

    if currency == 'MXN':
        precio_cambio = float(get_precio_de_cambio('MXN'))
        precio_compra = precio(conn,'COP', 200000, 1800000, 'sell') / precio_cambio

    if currency == 'USD':
        precio_cambio = float(get_precio_de_cambio('USD'))
        precio_compra = precio(conn,'COP', 200000, 1800000, 'sell') / precio_cambio
    
    margen = precio_venta / precio_compra - COMISION_LOCAL

    return margen, precio_venta, precio_compra

def precio(conn, currency, mmin, mmax, tipo):

    info = informacion_comerciantes(conn, currency, tipo)
    for puesto,datos in info.items():
        if mmax >= datos['min_amount'] and mmin <= datos['max_amount'] and datos['name'] != 'sromero':
            puesto_a_superar = str(puesto)
            break

    primer_precio = info[f'{puesto_a_superar}']['price']
    
    return primer_precio

def main():
    conn = conectar()
    cap = float(sys.argv[1])
    m_cr, pv_cr, pc_cr = margen(conn, 'CRC', 10000, 300000)
    m_mx, pv_mx, pc_mx = margen(conn, 'MXN', 100, 10000)
    m_us, pv_us, pc_us = margen(conn, 'USD', 100, 400)
    new_cap = cap*round(m_mx,3)
    print(f'Margen CR:  {round(m_cr,3)}')
    print(f'Margen MX:  {round(m_mx,3)}  pv {round(pv_mx)}  pc {round(pc_mx)}  cap {cap} newcap {new_cap}')
    print(f'Margen EC:  {round(m_us,3)}')



if __name__ == "__main__":
    main()

