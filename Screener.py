import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from time import mktime


def _get_crumbs_and_cookies(stock):
    """
    get crumb and cookies for historical data csv download from yahoo finance

    parameters: stock - short-handle identifier of the company

    returns a tuple of header, crumb and cookie
    """

    url = 'https://finance.yahoo.com/quote/{}/history'.format(stock)
    with requests.session():
        header = {'Connection': 'keep-alive',
                  'Expires': '-1',
                  'Upgrade-Insecure-Requests': '1',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
                   AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
                  }

        website = requests.get(url, headers=header)
        soup = BeautifulSoup(website.text, 'lxml')
        crumb = re.findall('"CrumbStore":{"crumb":"(.+?)"}', str(soup))

        return (header, crumb[0], website.cookies)


def load_csv_data(stock, interval='1d', day_begin='2018-01-01', day_end='2018-09-01'):
    """
    queries yahoo finance api to receive historical data in csv file format

    parameters:
        stock - short-handle identifier of the company

        interval - 1d, 1wk, 1mo - daily, weekly monthly data

        day_begin - starting date for the historical data (format: yyyy-mm-dd)

        day_end - final date of the data (format: yyyy-mm-dd)

    returns a list of comma seperated value lines
    """
    day_begin_unix = int(mktime(datetime.strptime(day_begin, '%Y-%m-%d').timetuple()))
    day_end_unix = int(mktime(datetime.strptime(day_end, '%Y-%m-%d').timetuple()))

    header, crumb, cookies = _get_crumbs_and_cookies(stock)

    with requests.session():
        url = 'https://query1.finance.yahoo.com/v7/finance/download/' \
              '{stock}?period1={day_begin}&period2={day_end}&interval={interval}&events=history&crumb={crumb}' \
            .format(stock=stock, day_begin=day_begin_unix, day_end=day_end_unix, interval=interval, crumb=crumb)

        website = requests.get(url, headers=header, cookies=cookies)

        return website.text.split('\n')[:-1]


def get_data(stock):
    df = pd.read_csv('/Users/alexandersson/Downloads/' + stock, parse_dates=['Date'], index_col=['Date'])
    return df


def moving_average(df, periods):
    df['MA'+str(periods)] = df['Close'].rolling(window=periods).mean()


def plotter(df, MA50=False, MA200=False):
    plt.figure(figsize=(15,5))
    plt.subplot(211)
    plt.plot(df['Close'])
    if MA50:
        moving_average(df, 50)
        plt.plot(df['MA50'])
    if MA200:
        moving_average(df, 200)
        plt.plot(df['MA200'])
    plt.legend(['Close', 'MA50', 'MA200'])
    plt.subplot(212)
    plt.plot(df['Volume'])
    plt.legend(['Volym'], loc=2)
    plt.show()


evo=load_csv_data('evo.st', day_begin='2018-01-01', day_end='2018-09-29')
headers = evo[:1]


df = pd.DataFrame((s.split(',') for s in evo))
df.columns = df.iloc[0]
df = df.reset_index(drop=True)
df = df.drop(0)
print(df.tail())

plotter(df)