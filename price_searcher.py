#!/usr/bin/env python3

from flask import Flask, redirect
import json
import requests


app = Flask(__name__)
product_dict = {}
product_urls = []
max_range = 200


@app.route("/")
def list_product_ids():
    """Returns the first max_range product ids to the '/' endpoint."""
    if len(product_urls) > max_range:
        end = max_range
        url_list = '<h3>Results from {0} to {1} of {2}<br></h3>'.format(
            1,
            end,
            len(product_urls),
        )
        url_list += '<a href="/range/{}">next</a><br><br>'.format(end)
    else:
        end = len(product_urls)
        url_list = '<h3>Results from {0} to {1} of {2}<br></h3>'.format(
            1,
            end,
            len(product_urls),
        )
    for i in range(end):
        url_list += product_urls[i]
    return url_list


@app.route('/range/<start_str>')
def list_product_ids_in_range(start_str):
    """Returns start + max_range product ids to the '/range/' endpoint."""
    start = int(start_str)
    if start > len(product_urls):
        new_start = len(product_urls) - (len(product_urls) % max_range)
        if new_start == 0:
            return redirect('/')
        else:
            return redirect('/range/{}'.format(new_start))

    if len(product_urls) > start + max_range:
        end = start + max_range
        url_list = '<h3>Results from {0} to {1} of {2}<br></h3>'.format(
            start + 1,
            end,
            len(product_urls),
        )
        url_list += '<a href="/range/{}">next</a><br>'.format(end)
    else:
        end = len(product_urls)
        url_list = '<h3>Results from {0} to {1} of {2}<br></h3>'.format(
            start + 1,
            end,
            len(product_urls),
        )
    if start > max_range:
        url_list += '<a href="/range/{}">previous</a><br><br>'.format(
            start - max_range)
    else:
        url_list += '<a href="/">previous</a><br><br>'.format(0)
    for i in range(start, end):
        url_list += product_urls[i]
    return url_list


@app.route('/id/<product_id>')
def data_for_id(product_id):
    """Returns product information in JSON to the /id/ endpoint."""
    item = product_dict[product_id]
    price = item.get('price', None)
    if price == '':
        price = None
    elif price:
        price = float(price)
    try:
        in_stock = item['in_stock']
    except KeyError:
        try:
            in_stock = item['instock']
        except KeyError:
            in_stock = None
    if in_stock == 'yes' or in_stock == 'y':
        in_stock = True
    elif in_stock == 'no' or in_stock == 'n':
        in_stock = False
    else:
        in_stock = None
    return json.dumps({
        'id': product_id,
        'name': item.get('name', None),
        'brand': item.get('brand', None),
        'retailer': item.get('retailer', None),
        'price': price,
        'in stock': in_stock,
    }, separators=(',', ':'))


@app.before_first_request
def ingest_data():
    """Ingests data from the url and csv sources at startup."""
    ingest_from_url('https://s3-eu-west-1.amazonaws.com/'
                    'pricesearcher-code-tests/'
                    'python-software-developer/products.json')
    ingest_from_csv('products.csv')


def ingest_from_url(url):
    """Ingests data from the given url."""
    r = requests.get(url)
    data = r.json()
    for item in data:
        item_id = item['id']
        product_dict[item_id] = item
        product_urls.append('<a href="/id/{0}">{1}</a><br>'.format(
            item_id,
            item_id,
        ))


def ingest_from_csv(path):
    """Ingests data from the .csv file at path."""
    with open(path, 'rt') as f:
        fields = f.readline().replace(' ', '').replace('\n', '').\
            lower().split(',')
        id_index = fields.index('id')
        for line in f:
            data = line.replace('"', '').replace('\n', '').\
                replace(' ', '').split(',')
            item_id = data[id_index]
            item = dict(zip(fields, data))
            product_dict[item_id] = item
            product_urls.append('<a href="/id/{0}">{1}</a><br>'.format(
                item_id,
                item_id,
            ))
