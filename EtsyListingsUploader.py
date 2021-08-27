import xlrd
from json import loads as l
from json import dumps as d
from requests import post as post
from requests import put as put
from PIL import Image
from time import sleep
from os import listdir as ld
from os.path import isdir as isd
from requests_oauthlib import OAuth1Session, OAuth1
from random import choice,shuffle
import sys



def get_key_data(path_to_listing_data):
    sh = xlrd.open_workbook(path_to_listing_data).sheet_by_index(0)
    key_data = {}
    for rx in range(sh.nrows):
        key_data.update({sh.cell_value(rx, 0): sh.cell_value(rx, 1)})
    return key_data


def post_listing(params):
    try:
        listing_id=l(post(url, auth=auth, params=params).text)['results'][0]['listing_id']
        print(f'Listing created! Listing id is {listing_id}')
    except Exception as e:
        print(f'Listing is not created! Error: {e}')
    sleep(0.1)
    return listing_id

def add_variation(models,listing_id):
    r = read(put('{}/{}/inventory'.format(base_url,listing_id), auth=auth, data={'products': models,'price_on_property': ['514']}))
    print(f"Uploading models for listing {listing_id} {read_r(r)}")
    return

def add_photos(imgs, l_id):
    n=0
    for img in imgs:
        n += 1
        Image.open(img).save('up.jpg')
        params = {'listing_id': l_id, 'listing_image_id': n}
        files = {'image': ['up.jpg', open('up.jpg', 'rb'), 'image/jpeg']}
        r=post("{}/{}/images".format(url, l_id), params=params, files=files, auth=auth)
        print(f'Adding a photo number {n} to listing {l_id} is {read_r(r)}')
        sleep(0.3)
    return

def read_r(r):
    if '200' in str(r):
        r='completed'
    else:
        r='UNcompleted!!!'
        return r

def get_imgs(way):
    imgs = [way]
    for img in dinamic_imgs(way):
        imgs.append(img)
    for img in str(key_data['photos_static']).split(','):
        imgs.append(img)
    imgs.reverse()
    return imgs


def dinamic_imgs(way):
    imgs=[]
    m = int(way.split('\\')[-1].lower().replace(key_data['file_mask'], '').replace('.jpg', ''))
    n = int(key_data['photos_dynamic'])
    for i in range(0, n):
        imgs.append(way.replace(key_data['file_mask'], "").replace(str(m), str((m-1)*n+i+1)))
    return imgs


def get_random_keywords(theme,n):
    keywords = l(open(key_data['file_keywords']).read().replace("'", '"'))
    try:
        key_line=keywords[theme.lower().rstrip()]
        print(f'All your keywords {key_line}')
    except:
        key_line=['Gift for her','Gift for him']
        print('Unfortunately I can not find keywords, but do not worry I can help you')
    keys_str=""
    while True:
        if len(key_line)==0:
            break
        r_word=choice(key_line)
        key_line.remove(r_word)
        if len(keys_str+r_word+' ')>n:
            break
        else:
            keys_str += r_word + ' '
    print(f'Random matching words:{keys_str}')
    return keys_str


def title_generator(theme):
    title=f'{theme} {key_data["title"]} {get_random_keywords(theme,139-len(title))}'
    print(f'So, that is title {title}\n Do you like it? I hope yes')
    return title


def description_generator(title):
    return f'{title}\n\n{key_data[description]}'

def tags_generator(theme):
    tags_str=f"{key_data['tags']},{theme[:20]},{get_random_keywords(theme,20)}"
    print(f"Your tags looks like: {tags_str}")
    return tags_str


def models_gen(vars1, vars2):
    models = []
    for var1 in vars1:
        for var2 in vars2:
            models.append({'property_values': [{'property_id': 514, 'property_name': key_data['name_vars1'], 'values': [var1]},
                                               {'property_id': 513, 'property_name': key_data['name_vars2'], 'values': [var2]}],
                           'offerings': [{'price': round(float(vars1[var1])+vars2[var2],2), 'quantity': 50}]})
    return models

def key_data_test(key_data):

    return

def get_ways(general_way):
    ways = []
    for d in ld(general_way):
        for i in ld(f'{general_way}\\{d}'):
            if isd(f'{general_way}\\{d}\\{i}'):
                for file in ld(f'{general_way}\\{d}\\{i}'):
                    if key_data['file_mask'] in file:
                        ways.append(f'{general_way}\\{d}\\{i}\\{file}')
            else:
                for file in ld(f'{general_way}\\{d}'):
                    if key_data['file_mask'] in file:
                        ways.append(f'{general_way}\\{d}\\{file}')

    ways=sorted(set(ways))
    print(f'I found {len(ways)} ways\n{ways}')
    return ways


pathes=[input('введите путь к ключевому файлу')]

auth = OAuth1(consumer_key, oauth_consumer_secret, oauth_token, access_token_secret)

for path_to_listing_data in pathes:

    url = 'https://openapi.etsy.com/v2/listings'

    key_data=get_key_data(path_to_listing_data)
    key_data_test(key_data)
    models=models_gen(key_data['vars1'],key_data['vars2'])


    for way in get_ways(key_data['path']):
        print(way)
        theme = way.split("\\")[-2]
        title=title_generator(theme)
        params = {'quantity': key_data['quantity'], 'title': title,
                  'description': description_generator(title), 'price': key_data['base_price'],
                  'taxonomy_id': key_data['taxonomy_id'], 'shipping_template_id': key_data['shipping_id'], 'who_made': 'i_did', 'is_supply': '0',
                  'when_made': 'made_to_order', 'state': 'draft', 'processing_min': key_data['processing_min'], 'processing_max': key_data['processing_max'],
                  "tags": tags_generator(theme), 'materials': key_data['material']}
        l_id = post_listing(params)
        print(l_id)
        add_variation(models,l_id)
        add_photos(way, l_id)
        print(f'Listing {l_id} is fully uploaded!')
        break
    print(f'All listings of {path_to_listing_data.split} are uploaded! GGWP!')
