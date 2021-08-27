#this code chencks new job ofers by categories every 10 sec. it's simple but my gf finded new job ;)

import re
import requests
import time as t
from bs4 import BeautifulSoup
from random import choice
from time import sleep
import telebot # install pyTelegramBotApi


bot = telebot.TeleBot('YOUR_TOKEN') #creating a connetion with telegram bot


categories=["https://www.olx.pl/praca/e-commerce-handel-internetowy/warszawa/","https://www.olx.pl/praca/administracja-biurowa/warszawa/","https://www.olx.pl/praca/finanse-ksiegowosc/warszawa/","https://www.olx.pl/praca/gastronomia/warszawa/",'https://www.olx.pl/praca/informatyka/warszawa/','https://www.olx.pl/praca/kasjer-ekspedient/warszawa/','https://www.olx.pl/praca/kierowca-kurier/warszawa/','https://www.olx.pl/praca/inne-oferty-pracy/warszawa/']

link='https://www.olx.pl/praca/e-commerce-handel-internetowy/warszawa/'
chat_id='YOUR_CHAT_ID'

def parser(link): #parser via random proxy
    proxies = ['54.38.218.215:6582', '125.17.80.226:8080', '54.38.155.89:6582', '151.232.72.12:80', '151.232.72.18:80',
               '151.232.72.20:80', '151.232.72.16:80', '103.147.134.218:8080', '182.71.200.50:80', '151.232.72.15:80',
               '188.166.237.61:3128', '147.135.7.120:3128', '59.120.117.244:80', '163.172.29.94:3838',
               '104.244.99.186:80', '142.44.221.126:8080', '128.199.214.87:3128', '88.99.10.251:1080',
               '185.61.92.207:43947', '195.189.60.97:3128', '201.75.0.51:53281', '151.232.72.22:80',
               '45.137.216.118:80', '95.174.67.50:18080', '151.232.72.23:80', '151.232.72.14:80', '83.97.23.90:18080',
               '103.146.177.39:80', '165.22.64.68:36918', '165.22.81.30:39686', '88.99.10.254:1080', '167.71.5.83:3128',
               '169.57.1.84:8123', '161.202.226.194:80', '105.27.238.161:80', '78.47.16.54:80', '151.232.72.19:80',
               '64.71.145.122:3128', '54.38.219.100:6582', '191.96.42.80:8080', '157.230.103.91:38609',
               '173.192.128.238:25', '88.198.24.108:8080', '81.201.60.130:80', '80.48.119.28:8080', '159.8.114.37:8123',
               '37.120.192.154:8080', '163.172.213.218:3838', '162.144.106.245:3838', '85.238.104.235:47408',
               '43.248.24.158:51166', '173.212.202.65:80', '20.185.176.102:80', '13.209.155.88:8080',
               '213.230.107.125:3128', '202.40.188.94:40486', '113.254.85.88:8193', '52.157.97.234:80',
               '131.108.61.46:3128', '152.0.201.164:999', '103.57.70.248:52000', '162.144.36.187:3838',
               '119.82.253.123:36169', '85.10.219.97:1080', '183.87.153.98:49602', '144.76.214.154:1080',
               '203.202.245.58:80', '104.45.188.43:3128', '148.251.153.6:1080', '185.134.23.198:80',
               '85.10.219.103:1080', '191.232.170.36:80', '94.141.233.66:53171', '54.38.218.209:6582',
               '54.38.218.214:6582', '176.56.107.140:50177', '61.228.35.49:8080', '110.138.205.217:8080',
               '54.38.155.95:6582', '88.99.10.255:1080']
    s = requests.Session()
    s.proxies = choice(proxies)
    r = s.get(link)
    sleep(1)

    return r.text


def send_mes_telegram(txt):# telegram bot sene some text(txt) to some chat (chat_id)
    return bot.send_message(chat_id,txt)


def find_n_listing(txt): #finding how many new listings of job
    x=int(re.findall('<h2>Znaleziono (.+) ogłosz.+</h2>',txt)[0].replace(" ",""))
    return x


def find_last_listings(n,txt):#finding last listings and formating them
    soup = BeautifulSoup(txt,'html.parser')
    listings=soup.find_all(class_='offer-wrapper') #find all listings
    listings=listings[3:3+n] #only new listings
    listings_c=[]
    for i in listings: #formating listing for dict

        title=re.findall('<strong>(.+)</strong>',str(i.find(class_="lheight22 margintop5")))[0]
        link_listing=re.findall('href="(.+)">',str(i.find(class_="lheight22 margintop5")))[0]

        try:
            price=re.findall("""(od)</span>(.+)</span><span class="price-label"><span>( do)</span>(.+ zł)</span>""",str(i.find(class_='list-item__price')))[0]
            clear_price='зп '
            for el in price:
                clear_price+=el

        except:
            clear_price="зп не указана"

        listings_c.append({'title':title,'price':clear_price,'link':link_listing})

    return listings_c


try:

    categories_info={}
    for c in categories: #info about each category to dict ex:{categori:how many lisitings}
        # print(c, find_n_listing(parser(c)))
        categories_info.update({c:find_n_listing(parser(c))})


    while True:
        for i in categories_info:

            print(categories_info[i])
            print(i)


        for cat in categories:
            n_new_listings=int(str(find_n_listing(parser(cat))))-int(str(categories_info[cat])) #how many new listings (new-old)
            print(n_new_listings)


            if n_new_listings>0 : #send to telegram new offers
                for listing in find_last_listings(n_new_listings,parser(cat)):
                    send_mes_telegram(f'Новое объявление \n{listing["title"]}\n{listing["price"]}\n{listing["link"]}' )
                    sleep(3)

            categories_info.update({cat:int(n_new_listings)+int(categories_info[cat])}) #renew info about offers

        sleep(10)
except Exception as e:  # some thing if some
    try:
        send_mes_telegram(e)
    except:
        print('Lost internet connection')
