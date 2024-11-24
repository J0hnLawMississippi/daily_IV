#!/usr/bin/env python3

import pandas as pd
import csv
import requests
from datetime import datetime
#from array import array


#extract values from json with requests
def reqjson0(url, header):
        return requests.get(url, headers = header).json()['result']

def reqjson1(url, header, key):
        return requests.get(url, headers = header).json()['result']['{0}'.format(key)]

def reqjson2(url, header, index, key):
        return requests.get(url, headers = header).json()['result'][index]['{0}'.format(key)]

def reqjson2_0(url, header, key0, key1):
        return requests.get(url, headers = header).json()['result']['{0}'.format(key0)]['{0}'.format(key1)]

def reqjson3(url, header, key0, index, key1):
        return requests.get(url, headers = header).json()['result']['{0}'.format(key0)][index]['{0}'.format(key1)]


#headers for requests
jsonhead = { "Content-Type": "application/json" }


#######################################################################################################

def stringin(string, v0, v1, v2):
        return string.format(v0,v1,v2)

def stringin0(string, v0, v1):
        return string.format(v0,v1)



#######################################################################################################

'''

months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
for each in months: #rewrite python trick last chapter bader
        if (len(maturity) == 7):
                day = maturity[0:2]
                year = '20' + maturity[5:]
                if maturity[2:-2] == each:
                        month = months.index(each) + 1

        elif (len(maturity) == 6):
                day = maturity[0:1]
                year = '20' + maturity[4:]
                if maturity[1:-2]  == each:
                        month = months.index(each) + 1


expiration = [ datetime(int(year),int(month),int(day),8,0,0,0)]

now = datetime.utcnow()
T = list(map(lambda x: duration(x, now), expiration))


'''



#OPTION URLS

string = 'https://www.deribit.com/api/v2/public/get_order_book?depth=5&instrument_name=BTC-{0}-{1}-{2}'

string0 = 'https://www.deribit.com/api/v2/public/get_index_price?index_name=btc_usd'

string1 = 'https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC'

#print(reqjson1(string0,jsonhead, 'index_price'))

maturity = '27DEC24'

def myround(x, base=5000):
    return base * round(x/base)


#we use the index price for simplicity, use underlying futures price for greater accuracy of ATM strike
ATM_strike = myround( reqjson1(string0,jsonhead, 'index_price') ) 
#print(ATM_strike)

step = 5000

strike0 = ATM_strike - 7 * step
strikelast =  ATM_strike + 7*step


X0 = range(int(strike0),int(strikelast),int(step))


#bid,ask mid IV?
#values = ['ask_iv', 'underlying_price', 'best_bid_price', 'best_ask_price', 'underlying_index'] #mark_iv, ask_iv, bid_iv ...


expiry0 = [maturity]
inst0 = ['C','P']



expiry1 = expiry0 * len(X0) * len(inst0)
expiry1.sort()
expiry1.reverse() #adapt depending on future expiry dates


inst1 = len(expiry0) * (inst0[0] * len(X0) + inst0[1] *len (X0))


X1 = list(X0) * len(expiry0) * len(inst0)

UrlList =  list(map(lambda x,y,z: stringin(string, x,y,z), expiry1, X1, inst1))

pt = len(list(X0))
#print(pt)


#split up UrlList

db_callUrls = UrlList[0:pt] 
db_putUrls = UrlList[pt:2*pt] 

#get market volatilities 
cIV = list(map(lambda x: reqjson1(x, jsonhead, 'ask_iv'), db_callUrls))
pIV = list(map(lambda x: reqjson1(x, jsonhead, 'ask_iv'), db_putUrls))


#print(cIV,pIV)




okx_string0 = 'https://okx.com/api/v5/public/opt-summary?uly=BTC-USD'
okx_string1 = 'https://okx.com/api/v5/public/instruments?instType=OPTION'

okx_options = requests.get(okx_string0).json()['data']

okx_opt_string = 'BTC-USD-241227-{0}-{1}'


okx_strikes = list(range(80000,125000,5000))
cs = len(okx_strikes) * 'C'
ps = len(okx_strikes) * 'P'


okx_calls =  list(map(lambda x,y: stringin0(okx_opt_string, x,y), okx_strikes, cs))
okx_puts = list(map(lambda x,y: stringin0(okx_opt_string, x,y), okx_strikes, ps))

okx_cIV = []
okx_pIV = []

#okx_call_data =  [x for x in okx_options if x['instId'] == okx_calls[0]]



for each in okx_calls:
        for every in okx_options:
                if every['instId'] == each:
                        okx_cIV.append(every['askVol'])


for each in okx_puts:
        for every in okx_options:
                if every['instId'] == each:
                        okx_pIV.append(every['askVol'])

#print(okx_cIV)
#print(okx_pIV)


db_calls = [x[-20:] for x in db_callUrls]
db_puts = [x[-20:] for x in db_putUrls]
 
 
data = pd.DataFrame(list(zip(db_calls,cIV, db_puts, pIV)),
                    columns = ['DB_Calls', 'DB_Call_IVs', 'DB_Puts', 'DB_Put_IVs'])

data['OKX_Calls'] = pd.Series(okx_calls)
data['OKX_Call_IVs'] = pd.Series(okx_cIV) 
data['OKX_Puts'] = pd.Series(okx_puts)
data['OKX_Put_IVs'] = pd.Series(okx_pIV) 

data['OKX_Call_IVs'] = data['OKX_Call_IVs'].astype(float)
data['OKX_Put_IVs'] = data['OKX_Put_IVs'].astype(float)

data['OKX_Call_IVs'] *= 100
data['OKX_Put_IVs'] *= 100


now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

data.round(2).to_csv(f'daily_IV_db_okx_{now}.csv')



'''

# First, create dictionaries for quick access
okx_options_dict = {option['instId']: option for option in okx_options}

# Then, use these dictionaries to find matches more efficiently
okx_cIV = [okx_options_dict[each]['askVol'] for each in okx_calls if each in okx_options_dict]
okx_pIV = [okx_options_dict[each]['askVol'] for each in okx_puts if each in okx_options_dict]


print(okx_cIV)
print(okx_pIV)

'''
