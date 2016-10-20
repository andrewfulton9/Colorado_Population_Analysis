from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd

def get_tags(soup):
    '''
    input: beautiful soup html object
    output: dictionary of table values

    get table values and put them in a dictionary
    '''
    d = {}
    for item in soup.find_all('tr'):
        x = item.find_all('td')
        if x:
            d[x[0].text] = x[1].text
    return d

def tranform_nums(dictionary):
    '''
    input: dictionary
    output: dictionary with tranformed values

    Transform values of dictionary from strings to floats
    '''
    d = dictionary
    for k, v in d.items():
        dig = re.findall(r'[\d.]+', v)
        d[k] = float(''.join(dig))
    return d

def save_tags(dictionary):
    '''
    input: dictionary
    output: None

    turns dictionary to pandas series and saves it as a pickle
    '''
    ser = pd.Series(dictionary)
    ser.to_pickle('data/county_area.pkl')

if __name__ == '__main__':
    url = 'http://www.indexmundi.com/facts/united-states/quick-facts/colorado/land-area#table'
    html = requests.get(url).content

    soup = bs(html, 'html.parser')
    d = get_tags(soup)
    d = tranform_nums(d)
    save_tags(d)
