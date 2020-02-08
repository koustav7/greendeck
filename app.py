# required libraries
import pandas as pd
from urllib import request
from flask import Flask
from flask_cors import CORS
from pandas.io.json import json_normalize

# url containing data
url = 'https://greendeck-datasets-2.s3.amazonaws.com/netaporter_gb_similar.json'

# preprocessing part chosen is the columns I want to keep
def mypreprocess(url, chosen):
    res = request.urlopen(url)
    content = res.read()
    fin_con = content.decode('utf-8')
    data = pd.read_json(fin_con, lines = True, orient = 'columns')
    list = [data[i] for i in chosen]
    df = pd.concat(list, axis = 1)
    return(df)


def discount(buy, sell):
    y = (sell-buy)/buy
    return(y*100)

# dataset having columns in json format
fin = mypreprocess(url, ['_id', 'name', 'website_id', 'price'])

# decoding the json data
ide = json_normalize(df._id)
price = json_normalize(df.price)
website_id = json_normalize(df.website_id)
df = pd.concat([ide, fin['name'], website_id, price], axis = 1)

# creating the app
app = Flask(__name__)
CORS(app)


@app.route('/', methods=['POST'])
def output():
    dict = {'query_type': flask.request.json['query_type'], 'filters': flask.request.json['filters']} # reading POST requests
    if dict['query_type'] == 'discounted_products_list': # begining of solving 1st portion
        ls = dict['filters']
        dict1 = ls[0]
        if dict1['operand1'] == 'discount':
            lst = []
            if dict1['operator'] == '>':
                for i in range(len(df)):
                    if discount(df['regular_price.value'][i], df['offer_price.value'][i]) > dict1['operand2']: # selecting index of out interest
                            lst.append(i)
            if dict1['operator'] == '==':
                 for i in range(len(df)):
                     if discount(df['regular_price.value'][i], df['offer_price.value'][i]) == dict1['operand2']:
                         lst.append(i)
            if dict1['operator'] == '<':
                  for i in range(len(df)):
                      if discount(df['regular_price.value'][i], df['offer_price.value'][i]) < dict1['operand2']:
                          lst.append(i)
            l = [df['$oid'][i] for i in lst] # using the index to get the list of id's
            output = {"discounted_products_list": l} # output discounted product list
        if dict1['operand1'] == 'brand.name':
            a = 0                   # calculating index of given brand name
            for i in df['name']:
                if i == dict1['operand2']:
                    a = a+1
                    break
                else:
                    a = a+1
            lst = []
            if dict1['operator'] =='>':
                for i in range(len(df)):
                     if discount(df['regular_price.value'][i], df['offer_price.value'][i]) > discount(df['regular_price.value'][a], df['offer_price.value'][a]): # higher discount than given brand
                         lst.append(i)
            if dict1['operator'] == '==':
                for i in range(len(df)):
                    if discount(df['regular_price.value'][i], df['offer_price.value'][i]) == discount(df['regular_price.value'][a], df['offer_price.value'][a]): # same discount as given brand
                        lst.append(i)
            if dict1['operator'] == '<':
                for i in range(len(df)):
                    if discount(df['regular_price.value'][i], df['offer_price.value'][i]) < discount(df['regular_price.value'][a], df['offer_price.value'][a]): #less discount
                        lst.append(i)
            l = [df['$oid'][i] for i in lst]
            output = {"discounted_products_list": l} # output

        if dict1['operand1'] == 'competition': #getting index of given brand from the dataset
            a = 0
            for i in df['name']:
                if i == dict1['operand2']:
                    a = a+1
                    break

                else:
                    a = a+1

            lst = []
            for i in range(len(df)):
                if discount(df['regular_price.value'][i], df['offer_price.value'][i]) == discount(df['regular_price.value'][a], df['offer_price.value'][a]) or discount(df['regular_price.value'][i], df['offer_price.value'][i]) > discount(df['regular_price.value'][a], df['offer_price.value'][a]): # selecting the index
                    lst.append(i)


            l = [df['$oid'][i] for i in lst]
            output = {"discounted_products_list": l}


    if dict['query_type'] == "discounted_products_count|avg_discount":
        ls = dict['filters']
        dict1 = ls[0]
        if dict1['operand1'] == 'discount':
            disc = []
            l = []
            if dict1['operator'] == '>':
                for i in range(len(df)):
                    if discount(df['regular_price.value'][i], df['offer_price.value'][i]) > dict1['operand2']: # calculating the no of elements having greater discount than the given
                        l.append(i)
                        disc.append(discount(df['regular_price.value'][i], df['offer_price.value'][i]))
            if dict1['operator'] == '==':
                for i in range(len(df)):
                    if discount(df['regular_price.value'][i], df['offer_price.value'][i]) == dict1['operand2']: # calculating the no of elements having same discount as the given
                        l.append(i)
                        disc.append(discount(df['regular_price.value'][i], df['offer_price.value'][i]))
            if dict1['operator'] == '<':
                for i in range(len(df)):
                    if discount(df['regular_price.value'][i], df['offer_price.value'][i]) < dict1['operand2']: # calculating the no of elements having lesser discount than the given
                        l.append(i)
                        disc.append(discount(df['regular_price.value'][i], df['offer_price.value'][i]))

            avg_disc = sum(disc)/len(disc) # avarage discount
            output = { "discounted_products_count": len(l), "avg_discount": avg_disc} # output

        if dict1['operand1'] == 'brand.name':
            disc = []
            l = []
            a = 0
            for i in df['name']: # selecting the index of given brand
                if i == dict1['operand2']:
                    a = a+1
                    break
                else:
                    a = a+1
            if dict1['operator'] == '>':
                for i in range(len(df)):
                    if discount(df['regular_price.value'][i], df['offer_price.value'][i]) > discount(df['regular_price.value'][a], df['offer_price.value'][a]): # the index of the brands having greater discount than the given brand
                        l.append(i)
                        disc.append(discount(df['regular_price.value'][i], df['offer_price.value'][i]))

            if dict1['operator'] == '==':
                for i in range(len(df)):
                    if discount(df['regular_price.value'][i], df['offer_price.value'][i]) == discount(df['regular_price.value'][a], df['offer_price.value'][a]): # the index of the brands having same discount than the given brand
                        l.append(i)
                        disc.append(discount(df['regular_price.value'][i], df['offer_price.value'][i]))

            if dict1['operator'] == '<':
                for i in range(len(df)):
                    if discount(df['regular_price.value'][i], df['offer_price.value'][i]) < discount(df['regular_price.value'][a], df['offer_price.value'][a]): # the index of the brands having lesser discount than the given brand
                        l.append(i)
                        disc.append(discount(df['regular_price.value'][i], df['offer_price.value'][i]))
            avg_disc = sum(disc)/len(disc)
            output = { "discounted_products_count": len(l), "avg_discount": avg_disc} # output

    if dict['query_type'] == 'expensive_list':
        if len(dict) == 1:
            l = []
            for i in range(len(df)):
                if df['offer_price.value'][i] > df['basket_price.value'][i]: # selecting the products which are expensive
                    l.append(i)
            lst = [df['$oid'] for i in l]
            output = {"expensive_list": lst}
        else:
            ls = dict['filters']
            dict1 = ls[0]
            a = 0
            for i in df['name']: # selecting index of given brand
                if i == dict1['operand2']:
                    a = a+1
                    break
                else:
                    a = a+1
            l = []
            for i in range(len(df)):
                if (df['offer_price.value'][i]-df['basket_price.value'][i]) > (df['offer_price.value'][a]-df['basket_price.value'][a]): # selecting the index of the products having greater expense than the given one
                    l.append(i)
            lst = [df['$oid'] for i in l]
            output = {"expensive_list": lst}

    return(output) # output depending on  accepted POST request

if __name__ == '__main__' :
     app.run(debug=True, host = '0.0.0.0', port=5000) # running port of app
