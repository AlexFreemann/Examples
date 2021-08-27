
import time
import gspread
from time import sleep
from requests import post, get, put
from requests_oauthlib import OAuth1
from json import loads as jl
from json import dumps as jd
from requests.structures import CaseInsensitiveDict
import telebot  # install pyTelegramBotApi
from random import randint
from oauth2client.service_account import ServiceAccountCredentials

mes = ""

bot = telebot.TeleBot('telegram token')

shop = "shop_on_etsy"


#tokens for oauth etsy 
access_token_secret = '2d60f38937'
access_token = '9ad49fb7e7dd6d4691ac0849aa164f'

consumer_key = 'xu7brwyzudyuhwxeuydjltdc'
oauth_consumer_secret = "rtabucj7zi"

auth = OAuth1(consumer_key, oauth_consumer_secret, access_token, access_token_secret)

etsy = "https://openapi.etsy.com/v2/"
rem = "https://api.remonline.ru/"


def telega_mes(txt):
    bot.send_message("-494047761", txt)
    return sleep(5)


def give_token():
    api_key = "api_remonline"
    return jl(post(f'{rem}token/new', params={'api_key': api_key}).text)["token"]


def make_order(params):
    print('makeing order')
    creating = jl(post(f"{rem}order/", params=params).text)
    print(creating)
    order_id = creating['data']['id']
    global mes
    if creating['success']:
        mes += f"Новый зкаказ {order_id} создан успешно \n"
    else:
        mes += f"Не удалось создать заказ \n {params}\n"
    print(mes)
    return order_id


def rec(rec_id):
    for rec in etsy_request('receipts')['results']:
        if int(rec["receipt_id"]) == int(rec_id):
            break
    return rec


def order_params(trans):
    reciepte = rec(trans['receipt_id'])
    client_id = make_client(reciepte)
    img = give_image_url(trans["listing_id"])
    t = time.strftime("%d.%m.%Y %H:%M", time.gmtime(reciepte["creation_tsz"]))
    x = """{"351443":"", "351445": "model", "2147262": "rec_id", "2147263":"theme", "2147265": "coment", "2147266": "gift", "2147267": "listing_link", "2147268":"quantity" , "2147866": "listing_img","2147261":"time","2806508":"trans_id"}"""
    x = x.replace("model", model_find(trans))
    x = x.replace("rec_id", str(reciepte["receipt_id"]))
    x = x.replace("theme", str(theme_find(trans["title"])))
    x = x.replace("coment", str(reciepte["message_from_buyer"])[:127]).replace("\n", " ")
    x = x.replace("gift", gift_text(reciepte)[:127].replace("\n", " "))
    x = x.replace("listing_link", f"https://www.etsy.com/listing/{trans['listing_id']}")
    x = x.replace("quantity", str(trans['quantity']))
    x = x.replace("listing_img", img)
    x = x.replace("time", t)
    x = x.replace("trans_id", str(trans['transaction_id']))
    params = {
        'token': give_token(),
        "branch_id": "25356",
        "client_id": str(client_id),
        "order_type": "42695",
        "custom_fields": x}

    global mes
    mes += f"{img}\nНовый заказ! Магазин {shop}, тема: {str(theme_find(trans['title']))} \n"
    print(mes)
    return params


def make_client(rec):
    name = rec["formatted_address"].split("\n")[0]
    adres = give_adres(rec["formatted_address"])
    x = """{"1589734":"shop"}"""
    x = x.replace("shop", f'Etsy {shop}')
    params = {'token': give_token(), 'name': name, 'address': adres, 'email': rec["buyer_email"], "custom_fields": x}
    return jl(post(f"{rem}clients/", params=params).text)['data']['id']


def country_to_rus(country):
    countrys = {'United States': 'США', 'Canada': 'Канада', 'Germany': 'Германия', 'United Kingdom': 'Великобритания',
                'Switzerland': 'Швейцария', 'Sweden': 'Швеция', 'Australia': 'Австралия', 'Italy': 'Италия',
                'Belgium': 'Бельгия',
                'Mexico': 'Мексика', 'New Zealand': 'Новая Зеландия', 'Latvia': 'Латвия', 'Israel': 'Израиль',
                'Ireland': 'Ирландия', 'South Korea': 'Южная Корея', 'France': 'Франция', 'Lithuania': 'Литва',
                'Cyprus': 'Кипр',
                'Slovakia': 'Словакия', 'Poland': 'Польша', 'Denmark': 'Дания'}
    country = str(country)
    print(country)
    try:
        country_rus = countrys[country]
    except:
        country_rus = ""
    print(country_rus)
    return country_rus


def give_adres(adres):
    address_list = adres.split("\n")[1:]
    country_rus = country_to_rus(address_list[-1:][0])
    print("страна рус =", country_rus)
    adres = ""
    for line in address_list:
        adres += line + " "
    return adres + country_rus


def give_image_url(listing_id):
    return jl(get(f'{etsy}/listings/{listing_id}/images', auth=auth, timeout=5).text)['results'][0][
        "url_fullxfull"].replace("\/", "/")


def gift_text(reciepte):
    if reciepte["is_gift"]:
        if reciepte["needs_gift_wrap"]:
            mes = f"ДА, НУЖНА подарочная упаковка, добавить сообщение: {reciepte['gift_message']}"
        else:
            mes = f"ДА,НЕ нужна подарочная упаковка, добавить сообщение: {reciepte['gift_message']}"
    else:
        mes = "НЕТ"
    return mes[:120]


def model_find(trans):
    x = ""
    for i in trans["variations"]:
        x += i["formatted_value"] + '; '
    return x.replace("\/", "/")


def theme_find(title):
    title = title.lower().split(' ')[0:3]
    words = ["phone", "iphone", "samsung", "case", "pad", "mouse", "11", "pro", "max", "9x7", "galaxy", "passport",
             "cover", "mug", "oz", "case"]
    for word in words:
        try:
            title.remove(word)
        except:
            continue
    theme = ""
    for i in title:
        i += " "
        theme += i
    return theme


def etsy_request(request):
    return jl(get(f'{etsy}shops/{shop}/{request}?limit=100', auth=auth).text)


def last_orders_rem():
    last_orders = []
    for i in range(1, 6):
        params = {'token': give_token(), "sort_dir": "desc", "page": f"{i}"}
        orders_list = (jl(get(f"{rem}order/", params=params, timeout=5).text)['data'])
        for order in orders_list:
            last_orders.append(order)
    return last_orders


def check_rem(trans_id, last_orders):
    cheking = True
    for order in last_orders:
        try:
            if order["custom_fields"]["f2806508"] == str(trans_id):
                cheking = False
                break
        except:
            continue
    print(trans_id, cheking)
    return cheking


def ch_status(order):
    status = order['status']['name']
    if status == "New":
        status_id = "162655"
    elif status == "Sent":
        status_id = "864531"
    elif status == "Sent WOW":
        status_id = "864549"
    else:
        print("непонятный статус")
        status_id = status
    params = {'token': give_token(), "order_id": order['id'], "status_id": status_id}
    x = str(post(f'{rem}order/status/', params=params))
    if '200' in x:
        x = 'Успешно'
    else:
        x = 'Неудачно'
    global mes
    mes += f"Изменение статуса заказа в Rem: {x} \n\n"
    print(mes)
    return


def mark_shipping(order):
    url = f"{etsy}/shops/{shop}/receipts/{order['custom_fields']['f2147262']}/tracking?tracking_code={order['custom_fields']['f351443']}&carrier_name=belpost"
    x = r'{}'.format(post(url, auth=auth))
    # x=jl(x)['results'][0]['shipping_details']['was_shipped']
    print(x)
    print(type(x))
    if '200' in x:
        x = 'Успешно'
    else:
        x = 'Неудачно'
    global mes
    mes += f"Отметка трека на Etsy {shop} по заказу в Reme №{order['id']}: {x} \n"
    print(mes)
    return


def check_track(order):
    check = True
    try:
        if order['custom_fields']['f351443'] == "":
            check = False
    except:
        check = False
    return check


def wh_write_off(model_id, q, order_id):
    if model_id != "":
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        data = {"token": give_token(),
                "warehouse": 95527,
                "description": f"Списание по заказу {order_id}",
                "entities": [{"sn_accounting": False,
                              "residues": [{"cell_id": 104248, "quantity": q}],
                              "entity": int(model_id)}]}
        r = post(f"{rem}warehouse/outcome-transactions/", data=jd(data), headers=headers)
        print(r.text)
        print('model id', model_id)
        print(f"Списание со склада {jl(r.text)['success']} по заказу {order_id}")
        global mes
        mes += f"Списание со склада {jl(r.text)['success']} по заказу {order_id} \n"
    else:
        mes += f"Ничего не списал по заказу {order_id} \n"
        print(mes)
    return


def format_model_name(name):
    name = name.replace("  ", " ")
    name = name.replace("N.", "No.")
    model_name = ""
    for n in range(1, 6):
        x = len(name)
        new_name = name.replace(f"No.{n}", "")
        if len(new_name) != x:
            model_name = new_name.replace(";", "").strip().lower()
            break
    model_name = model_name.replace("  ", " ")
    if "Lenis" in shop:
        if "plastic" in model_name:
            model_name = model_name.replace(" plastic", "")
            model_name = f"plastic {model_name}"
        elif "silicone" in model_name:
            model_name = model_name.replace(" silicone", "")
            model_name = f"silicone {model_name}"
        else:
            model_name = model_name
        new_model_name = model_name
    else:
        new_model_name = model_name
    return new_model_name


def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("keys.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(f"Models").sheet1  # Open the spreadhseet
    models = sheet.get_all_values()
    return models


def find_model_id(model_name, models):
    model_name = format_model_name(model_name)
    wh_name = 'ручками'
    model_id = ''
    for model in models:
        for cell in range(2, len(model)):
            if model[cell] == model_name:
                model_id = model[0]
                wh_name = model[1]
                break
    global mes
    mes += f"Модель на {model_name} ,спишу со склада {wh_name} \n"
    print(mes)
    print('found model id', model_id)
    return model_id


input("sdmfksd")

while True:
    try:
        models = get_sheet()

        last_orders = last_orders_rem()

        # добавление заказа если не отмечен что отправлен и если нет в заказах рема на первой странице то добавляет заказы
        for transaction in etsy_request('transactions')['results']:
            if rec(transaction['receipt_id'])['was_shipped'] is False and \
                    rec(transaction['receipt_id'])['was_paid'] is True and check_rem(transaction['transaction_id'],
                                                                                     last_orders):
                order_id = make_order(order_params(transaction))
                wh_write_off(find_model_id(model_find(transaction), models), str(transaction['quantity']), order_id)
                if mes != "":
                    telega_mes(mes)
                mes = ''
                sleep(1)

        # Отметка трека и смена статуса если есть трек и статус не маркед
        for order in last_orders:
            if "[Marked]" not in order['status']['name'] and check_track(order) and order['client']['custom_fields'][
                'f1589734'] == f'Etsy {shop}':
                mark_shipping(order)
                ch_status(order)

        if mes != "":
            telega_mes(mes)
        mes = ''
    except Exception as e:
        sleep(1)
        try:
            telega_mes(f"Беда на {shop}: {e}")
            print(f"Беда на {shop}: {e}")
        except:
            print('Отвалился интернет')
        sleep(600)
    print('прошел цикл')
    sleep(randint(3 * 3600, 7 * 3600))
import time
import gspread
from time import sleep
from requests import post, get, put
from requests_oauthlib import OAuth1
from json import loads as jl
from json import dumps as jd
from requests.structures import CaseInsensitiveDict
import telebot  # install pyTelegramBotApi
from random import randint
from oauth2client.service_account import ServiceAccountCredentials

mes = ""

bot = telebot.TeleBot('599526168:AAHbo5p6BQbQRJlt0wfi10UpaDZvGwPfo9U')

shop = "KavunCrafts"

access_token_secret = '2d60f38937'
access_token = '9ad49fb7e7dd6d4691ac0849aa164f'

consumer_key = 'xu7brwyzudyuhwxeuydjltdc'
oauth_consumer_secret = "rtabucj7zi"

auth = OAuth1(consumer_key, oauth_consumer_secret, access_token, access_token_secret)

etsy = "https://openapi.etsy.com/v2/"
rem = "https://api.remonline.ru/"


def telega_mes(txt):
    bot.send_message("-494047761", txt)
    return sleep(5)


def give_token():
    api_key = "8efd4717b04145afa19c9b72715e444b"
    return jl(post(f'{rem}token/new', params={'api_key': api_key}).text)["token"]


def make_order(params):
    print('makeing order')
    creating = jl(post(f"{rem}order/", params=params).text)
    print(creating)
    order_id = creating['data']['id']
    global mes
    if creating['success']:
        mes += f"Новый зкаказ {order_id} создан успешно \n"
    else:
        mes += f"Не удалось создать заказ \n {params}\n"
    print(mes)
    return order_id


def rec(rec_id):
    for rec in etsy_request('receipts')['results']:
        if int(rec["receipt_id"]) == int(rec_id):
            break
    return rec


def order_params(trans):
    reciepte = rec(trans['receipt_id'])
    client_id = make_client(reciepte)
    img = give_image_url(trans["listing_id"])
    t = time.strftime("%d.%m.%Y %H:%M", time.gmtime(reciepte["creation_tsz"]))
    x = """{"351443":"", "351445": "model", "2147262": "rec_id", "2147263":"theme", "2147265": "coment", "2147266": "gift", "2147267": "listing_link", "2147268":"quantity" , "2147866": "listing_img","2147261":"time","2806508":"trans_id"}"""
    x = x.replace("model", model_find(trans))
    x = x.replace("rec_id", str(reciepte["receipt_id"]))
    x = x.replace("theme", str(theme_find(trans["title"])))
    x = x.replace("coment", str(reciepte["message_from_buyer"])[:127]).replace("\n", " ")
    x = x.replace("gift", gift_text(reciepte)[:127].replace("\n", " "))
    x = x.replace("listing_link", f"https://www.etsy.com/listing/{trans['listing_id']}")
    x = x.replace("quantity", str(trans['quantity']))
    x = x.replace("listing_img", img)
    x = x.replace("time", t)
    x = x.replace("trans_id", str(trans['transaction_id']))
    params = {
        'token': give_token(),
        "branch_id": "25356",
        "client_id": str(client_id),
        "order_type": "42695",
        "custom_fields": x}

    global mes
    mes += f"{img}\nНовый заказ! Магазин {shop}, тема: {str(theme_find(trans['title']))} \n"
    print(mes)
    return params


def make_client(rec):
    name = rec["formatted_address"].split("\n")[0]
    adres = give_adres(rec["formatted_address"])
    x = """{"1589734":"shop"}"""
    x = x.replace("shop", f'Etsy {shop}')
    params = {'token': give_token(), 'name': name, 'address': adres, 'email': rec["buyer_email"], "custom_fields": x}
    return jl(post(f"{rem}clients/", params=params).text)['data']['id']


def country_to_rus(country):
    countrys = {'United States': 'США', 'Canada': 'Канада', 'Germany': 'Германия', 'United Kingdom': 'Великобритания',
                'Switzerland': 'Швейцария', 'Sweden': 'Швеция', 'Australia': 'Австралия', 'Italy': 'Италия',
                'Belgium': 'Бельгия',
                'Mexico': 'Мексика', 'New Zealand': 'Новая Зеландия', 'Latvia': 'Латвия', 'Israel': 'Израиль',
                'Ireland': 'Ирландия', 'South Korea': 'Южная Корея', 'France': 'Франция', 'Lithuania': 'Литва',
                'Cyprus': 'Кипр',
                'Slovakia': 'Словакия', 'Poland': 'Польша', 'Denmark': 'Дания'}
    country = str(country)
    print(country)
    try:
        country_rus = countrys[country]
    except:
        country_rus = ""
    print(country_rus)
    return country_rus


def give_adres(adres):
    address_list = adres.split("\n")[1:]
    country_rus = country_to_rus(address_list[-1:][0])
    print("страна рус =", country_rus)
    adres = ""
    for line in address_list:
        adres += line + " "
    return adres + country_rus


def give_image_url(listing_id):
    return jl(get(f'{etsy}/listings/{listing_id}/images', auth=auth, timeout=5).text)['results'][0][
        "url_fullxfull"].replace("\/", "/")


def gift_text(reciepte):
    if reciepte["is_gift"]:
        if reciepte["needs_gift_wrap"]:
            mes = f"ДА, НУЖНА подарочная упаковка, добавить сообщение: {reciepte['gift_message']}"
        else:
            mes = f"ДА,НЕ нужна подарочная упаковка, добавить сообщение: {reciepte['gift_message']}"
    else:
        mes = "НЕТ"
    return mes[:120]


def model_find(trans):
    x = ""
    for i in trans["variations"]:
        x += i["formatted_value"] + '; '
    return x.replace("\/", "/")


def theme_find(title):
    title = title.lower().split(' ')[0:3]
    words = ["phone", "iphone", "samsung", "case", "pad", "mouse", "11", "pro", "max", "9x7", "galaxy", "passport",
             "cover", "mug", "oz", "case"]
    for word in words:
        try:
            title.remove(word)
        except:
            continue
    theme = ""
    for i in title:
        i += " "
        theme += i
    return theme


def etsy_request(request):
    return jl(get(f'{etsy}shops/{shop}/{request}?limit=100', auth=auth).text)


def last_orders_rem():
    last_orders = []
    for i in range(1, 6):
        params = {'token': give_token(), "sort_dir": "desc", "page": f"{i}"}
        orders_list = (jl(get(f"{rem}order/", params=params, timeout=5).text)['data'])
        for order in orders_list:
            last_orders.append(order)
    return last_orders


def check_rem(trans_id, last_orders):
    cheking = True
    for order in last_orders:
        try:
            if order["custom_fields"]["f2806508"] == str(trans_id):
                cheking = False
                break
        except:
            continue
    print(trans_id, cheking)
    return cheking


def ch_status(order):
    status = order['status']['name']
    if status == "New":
        status_id = "162655"
    elif status == "Sent":
        status_id = "864531"
    elif status == "Sent WOW":
        status_id = "864549"
    else:
        print("непонятный статус")
        status_id = status
    params = {'token': give_token(), "order_id": order['id'], "status_id": status_id}
    x = str(post(f'{rem}order/status/', params=params))
    if '200' in x:
        x = 'Успешно'
    else:
        x = 'Неудачно'
    global mes
    mes += f"Изменение статуса заказа в Rem: {x} \n\n"
    print(mes)
    return


def mark_shipping(order):
    url = f"{etsy}/shops/{shop}/receipts/{order['custom_fields']['f2147262']}/tracking?tracking_code={order['custom_fields']['f351443']}&carrier_name=belpost"
    x = r'{}'.format(post(url, auth=auth))
    # x=jl(x)['results'][0]['shipping_details']['was_shipped']
    print(x)
    print(type(x))
    if '200' in x:
        x = 'Успешно'
    else:
        x = 'Неудачно'
    global mes
    mes += f"Отметка трека на Etsy {shop} по заказу в Reme №{order['id']}: {x} \n"
    print(mes)
    return


def check_track(order):
    check = True
    try:
        if order['custom_fields']['f351443'] == "":
            check = False
    except:
        check = False
    return check


def wh_write_off(model_id, q, order_id):
    if model_id != "":
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        data = {"token": give_token(),
                "warehouse": 95527,
                "description": f"Списание по заказу {order_id}",
                "entities": [{"sn_accounting": False,
                              "residues": [{"cell_id": 104248, "quantity": q}],
                              "entity": int(model_id)}]}
        r = post(f"{rem}warehouse/outcome-transactions/", data=jd(data), headers=headers)
        print(r.text)
        print('model id', model_id)
        print(f"Списание со склада {jl(r.text)['success']} по заказу {order_id}")
        global mes
        mes += f"Списание со склада {jl(r.text)['success']} по заказу {order_id} \n"
    else:
        mes += f"Ничего не списал по заказу {order_id} \n"
        print(mes)
    return


def format_model_name(name):
    name = name.replace("  ", " ")
    name = name.replace("N.", "No.")
    model_name = ""
    for n in range(1, 6):
        x = len(name)
        new_name = name.replace(f"No.{n}", "")
        if len(new_name) != x:
            model_name = new_name.replace(";", "").strip().lower()
            break
    model_name = model_name.replace("  ", " ")
    if "Lenis" in shop:
        if "plastic" in model_name:
            model_name = model_name.replace(" plastic", "")
            model_name = f"plastic {model_name}"
        elif "silicone" in model_name:
            model_name = model_name.replace(" silicone", "")
            model_name = f"silicone {model_name}"
        else:
            model_name = model_name
        new_model_name = model_name
    else:
        new_model_name = model_name
    return new_model_name


def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("keys.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(f"Models").sheet1  # Open the spreadhseet
    models = sheet.get_all_values()
    return models


def find_model_id(model_name, models):
    model_name = format_model_name(model_name)
    wh_name = 'ручками'
    model_id = ''
    for model in models:
        for cell in range(2, len(model)):
            if model[cell] == model_name:
                model_id = model[0]
                wh_name = model[1]
                break
    global mes
    mes += f"Модель на {model_name} ,спишу со склада {wh_name} \n"
    print(mes)
    print('found model id', model_id)
    return model_id


input("sdmfksd")

while True:
    try:
        models = get_sheet()

        last_orders = last_orders_rem()

        # добавление заказа если не отмечен что отправлен и если нет в заказах рема на первой странице то добавляет заказы
        for transaction in etsy_request('transactions')['results']:
            if rec(transaction['receipt_id'])['was_shipped'] is False and \
                    rec(transaction['receipt_id'])['was_paid'] is True and check_rem(transaction['transaction_id'],
                                                                                     last_orders):
                order_id = make_order(order_params(transaction))
                wh_write_off(find_model_id(model_find(transaction), models), str(transaction['quantity']), order_id)
                if mes != "":
                    telega_mes(mes)
                mes = ''
                sleep(1)

        # Отметка трека и смена статуса если есть трек и статус не маркед
        for order in last_orders:
            if "[Marked]" not in order['status']['name'] and check_track(order) and order['client']['custom_fields'][
                'f1589734'] == f'Etsy {shop}':
                mark_shipping(order)
                ch_status(order)

        if mes != "":
            telega_mes(mes)
        mes = ''
    except Exception as e:
        sleep(1)
        try:
            telega_mes(f"Беда на {shop}: {e}")
            print(f"Беда на {shop}: {e}")
        except:
            print('Отвалился интернет')
        sleep(600)
    print('прошел цикл')
    sleep(randint(3 * 3600, 7 * 3600))

