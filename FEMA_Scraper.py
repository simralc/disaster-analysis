
# coding: utf-8

# In[5]:


import io, time, json
import requests
from bs4 import BeautifulSoup
import urllib.parse as parse
import re


# In[13]:


### Get Amount of Funding Raised/Approved for a Hurricane
def retrieve_html(url):
    """
    Return the raw HTML at the specified URL.

    Args:
        url (string): 

    Returns:
        status_code (integer):
        raw_html (string): the raw HTML content of the response, properly encoded according to the HTTP headers.
    """
    r = requests.get(url)
    return (r.status_code, r.content)

def getAllLocations(url):
    code, content = retrieve_html(url)
    if code != 200:
        print('Could not Find Locations')
        return None
    
    soup = BeautifulSoup(content, 'html.parser')
    locationvals = soup.find('select', id="edit-field-dv2-state-territory-tribal-value-selective").find_all('option')
    return [loc.text for loc in locationvals]
    
    
def getNewUrl(source, keys, params):
    code, content = retrieve_html(source)
    if code != 200:
        print('Failed to Retrive Info for Hurricane ' + params['disasterName'])
        return None
    soup = BeautifulSoup(content, 'html.parser')
    locationvals = soup.find('select', id="edit-field-dv2-state-territory-tribal-value-selective").find("option", text=params['location'])
    incidentvals = soup.find('select', id="edit-field-dv2-incident-type-tid").find("option", text=params['incidentType'])
    
    keys['field_dv2_state_territory_tribal_value_selective'] = locationvals['value']
    keys['field_dv2_incident_type_tid'] = incidentvals['value']
    keys['field_dv2_incident_begin_value%5Bvalue%5D%5Bmonth%5D'] = months[params['startMonth']]
    keys['field_dv2_incident_begin_value%5Bvalue%5D%5Byear%5D'] = params['startYear']
    keys['field_dv2_incident_end_value%5Bvalue%5D%5Bmonth%5D'] = params['endMonth']
    keys['field_dv2_incident_end_value%5Bvalue%5D%5Byear%5D'] = params['endYear']
    return params['source'] + '?' + parse.urlencode(keys)

def searchPageforSpending(soup, disaster):
    b = soup.find('div', class_="view-content")
    if b == None:
        return 0 
    b = b.find_all('a')
    relevantrefs = [ref for ref in b if disaster in ref.text]
    result = 0
    amount = re.compile("\$(\S*)")
    for ref in relevantrefs:
        nexturl = 'https://www.fema.gov/' + ref['href']
        code, content = retrieve_html(nexturl)
        if code != 200:
            continue
        dissumsoup = BeautifulSoup(content, 'html.parser')
        snaps = dissumsoup.find('div', class_="disaster-snapshot col-lg-4 col-md-12").find_all('p')
        texts = [p.text for p in snaps if '$' in p.text]
        amounts = [amount.findall(text)[0] for text in texts]
        values = [float(value.replace(',', '')) for value in amounts]
        result += sum(values)
        time.sleep(0.01)
    return result

def getRaisedFunds(params, atts):
    nextPage = getNewUrl(params['source'], atts, params)
    totalSpending = 0
    while(nextPage != None):
        time.sleep(0.2)
        code, content = retrieve_html(nextPage)
        if code != 200:
            break
        soup = BeautifulSoup(content, 'html.parser')
        totalSpending += searchPageforSpending(soup, params['disasterName'])
        nexttag = soup.find('a', title="Go to next page")
        if nexttag == None:
            break                           
        nextPage = params['source'] + '?' + nexttag['href']
    return totalSpending

def getAllFunding(disastersinfo, searchParams):
    locations = getAllLocations(searchParams['source'])
    fundingRaised = {}
    for (name, year) in disastersinfo:
        searchParams['startYear'] = year
        searchParams['endYear'] = year
        searchParams['disasterName'] = name
        fundingRaised[name] = {}
        for loc in locations:
            searchParams['location'] = loc
            fundingRaised[name][loc] = getRaisedFunds(searchParams, keys)
    return fundingRaised


# In[11]:


keys = {'field_dv2_state_territory_tribal_value_selective' : 'All',
        'field_dv2_incident_type_tid' : 49124, # Hurricane Code
        'field_dv2_declaration_type_value' : 'DR',
        'field_dv2_incident_begin_value%5Bvalue%5D%5Bmonth%5D' : 0,
        'field_dv2_incident_begin_value%5Bvalue%5D%5Byear%5D' : 2000,
        'field_dv2_incident_end_value%5Bvalue%5D%5Bmonth%5D' : 0,
        'field_dv2_incident_end_value%5Bvalue%5D%5Byear%5D' : 2000}
months = {'January' : 1,
          'February' : 2,
          'March' : 3,
          'April' : 4,
          'May' : 5,
          'June' : 6,
          'July' : 7,
          'August' : 8,
          'September' : 9,
          'October' : 10,
          'November' : 11,
          'December' : 12}
searchParams = {'source' : 'https://www.fema.gov/disasters',
                'location' : 'Florida',
                'incidentType' : 'Hurricane',
                'declarationType' : 'DR',
                'startMonth' : 'January',
                'startYear' : 2013,
                'endMonth' : 'December',
                'endYear' : 2018,
                'disasterName' : 'Hurricane Irma'}


# In[14]:


# disastersInfo = [('Irma', 2017)]
# getAllFunding(disastersInfo, searchParams)

