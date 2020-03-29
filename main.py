from bs4 import BeautifulSoup
from datetime import datetime
import demjson
import pandas as pd
import urllib
import re

class CoronaStats:
    def __init__(self):
        self.url = 'https://www.worldometers.info/coronavirus/'

        req = urllib.request.urlopen(urllib.request.Request(
            self.url,
            data = None,
            headers = {
                'User-Agent': 'Mozilla/5.0' # Worldometer doesn't like us
            }
        ))

        self.df = pd.read_html(req.read().decode('utf-8'))[0]
    
    def get_total_cases(self, country = 'Total: '):
        return self.df.loc[self.df['Country,Other'] == country.capitalize(), 'TotalCases'].array[0]
    
    def get_new_cases(self, country = 'Total: '):
        return self.df.loc[self.df['Country,Other'] == country.capitalize(), 'NewCases'].array[0]
    
    def get_total_deaths(self, country = 'Total: '):
        return self.df.loc[self.df['Country,Other'] == country.capitalize(), 'TotalDeaths'].array[0]
    
    def get_new_deaths(self, country = 'Total: '):
        return self.df.loc[self.df['Country,Other'] == country.capitalize(), 'NewDeaths'].array[0]
    
    def get_total_recovered(self, country = 'Total: '):
        return self.df.loc[self.df['Country,Other'] == country.capitalize(), 'TotalRecovered'].array[0]
    
    def get_active_cases(self, country = 'Total: '):
        return self.df.loc[self.df['Country,Other'] == country.capitalize(), 'ActiveCases'].array[0]
    
    def get_critical_cases(self, country = 'Total: '):
        return self.df.loc[self.df['Country,Other'] == country.capitalize(), 'Serious,Critical'].array[0]
    
    def get_total_cases_per_1m(self, country = 'Total: '):
        return self.df.loc[self.df['Country,Other'] == country.capitalize(), 'Tot Cases/1M pop'].array[0]
    
    def get_total_deaths_per_1m(self, country = 'Total: '):
        return self.df.loc[self.df['Country,Other'] == country.capitalize(), 'Tot Deaths/1M pop'].array[0]

    def get_history(self, country = 'Total: '):
        url = 'https://www.worldometers.info/coronavirus/'

        if country != 'Total: ':
            url += 'country/' + country

        req = urllib.request.urlopen(urllib.request.Request(
            url,
            data = None,
            headers = {
                'User-Agent': 'Mozilla/5.0' # Worldometer doesn't like us
            }
        ))
        page = BeautifulSoup(req.read().decode('utf8'), 'html.parser')

        if country == 'Total: ':
            div1 = page.find_all('div', class_ = 'col-md-6')[2].script.text
            div2 = page.find_all('div', class_ = 'col-md-6')[3].script.text
        else:
            div1 = page.find_all('div', class_ = 'graph_row')[0].script.text
            div2 = page.find_all('div', class_ = 'graph_row')[3].script.text

        js_obj1 = re.match(r"[\s\S]*?Highcharts\.chart\('coronavirus-cases-linear', ([\s\S]*?)\);", div1).group(1)
        graph1 = demjson.decode(js_obj1)

        js_obj2 = re.match(r"[\s\S]*?Highcharts\.chart\('coronavirus-deaths-linear', ([\s\S]*?)\);", div2).group(1)
        graph2 = demjson.decode(js_obj2)

        dates = [datetime.strptime(i + ' {}'.format(datetime.today().year), '%b %d %Y') for i in graph1['xAxis']['categories']]
        cases = graph1['series'][0]['data']
        deaths = graph2['series'][0]['data']

        return pd.DataFrame(zip(dates, cases, deaths), columns = ['Date', 'TotalCases', 'TotalDeaths'])
