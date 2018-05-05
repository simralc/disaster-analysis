
# coding: utf-8

# In[1]:


import io, time, json
import requests
from bs4 import BeautifulSoup
import urllib
from urllib import parse


# In[2]:


def retrieve_html(url, params = None):  
    if params is None:
        params = ''
    response = requests.get(url + urllib.parse.urlencode(params))
    return response.status_code, response.text


# In[3]:


def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    prd = soup.find("table", id="results")
    if prd is None:
        print('No results found')
        return
    prd = soup.find_all("tr")
    fund_val = prd[8].find_all("td")[-2].text
    return fund_val


# In[4]:


def get_all_states(html):
    soup = BeautifulSoup(html, 'html.parser')
    states = soup.find("select", id="statefips").find_all("option")
    states_text = [t.text for t in states]
    states_values = [t['value'] for t in states]
    return states_values


# In[11]:


def getFundingForQuery(url, params, search_html):
    state_list = get_all_states(search_html)
    state_damage_vals = []
    for state in state_list:
        params['statefips'] = state
        state_damage_page = retrieve_html(url, params)[1]
        state_damage_vals.append(parse_page(state_damage_page))
    return state_damage_vals


# In[19]:


def getFundingDataFromNOAA(eventType='(Z) Storm Surge/Tide', beginDate_mm='01', beginDate_dd='01', 
                           beginDate_yyyy='2017', endDate_mm='01', endDate_dd='31', endDate_yyyy='2018', 
                           county='ALL', statefips='48,TEXAS'):
    url = "https://www.ncdc.noaa.gov/stormevents/listevents.jsp?"
    params = {'eventType': eventType,
                  'beginDate_mm': beginDate_mm,
                  'beginDate_dd': beginDate_dd,
                  'beginDate_yyyy': beginDate_yyyy,
                  'endDate_mm': endDate_mm,
                  'endDate_dd': endDate_dd,
                  'endDate_yyyy': endDate_yyyy,
                  'county': county,
                  'sort': 'DT',
                  'submitbutton': 'Search',
                  'statefips': statefips}

    searchUrl = "https://www.ncdc.noaa.gov/stormevents/choosedates.jsp?statefips=-999%2CALL"
    search_html = retrieve_html(searchUrl)[1]
    damage_values = getFundingForQuery(url, params, search_html)
    return damage_values


# In[15]:


# vals = getFundingDataFromNOAA()


# In[16]:


# vals[:10]

