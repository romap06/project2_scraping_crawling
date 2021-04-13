#################################
##### Name: Roma Patel
##### Uniqname: romap
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

CACHE_FILENAME = "sites_mapping_cache.json"
CACHE_DICT = {}

map_key = secrets.MAP_QUEST_CONSUMER_KEY

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()


def construct_unique_key(baseurl):
    ''' constructs a key that is guaranteed to uniquely and
    repeatably identify an API request by its baseurl and params

    AUTOGRADER NOTES: To correctly test this using the autograder, use an underscore ("_")
    to join your baseurl with the params and all the key-value pairs from params
    E.g., baseurl_key1_value1

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint

    Returns
    -------
    string
        the unique key as a string
    '''
    # params_list = []

    # for key, value in params.items():
    #     params_list.append('{}_{}'.format(key, value))

    # params_list.sort()
    # params_string = baseurl+'_'+'_'.join(params_list)

    return baseurl

def make_request_with_cache(baseurl):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new
    request, save it, then return it.

    AUTOGRADER NOTES: To test your use of caching in the autograder, please do the following:
    If the result is in your cache, print "fetching cached data"
    If you request a new result using make_request(), print "making new request"

    Do no include the print statements in your return statement. Just print them as appropriate.
    This, of course, does not ensure that you correctly retrieved that data from your cache,
    but it will help us to see if you are appropriately attempting to use the cache.

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint

    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''

    unique_key = construct_unique_key(baseurl)
    CACHE_DICT = open_cache()
    if unique_key in CACHE_DICT.keys():
        print("Using Cache")
        return CACHE_DICT[unique_key]
    else:
        print("Fetching")
        html = requests.get(baseurl).text
        CACHE_DICT[unique_key] = html
        save_cache(CACHE_DICT)
        return CACHE_DICT[unique_key]

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.

    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')

    '''

    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone


    def info(self):
        return f"{self.name} ({self.category}): {self.address} {self.zipcode}"


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''


    html = requests.get('https://www.nps.gov/index.htm').text
    soup = BeautifulSoup(html, 'html.parser')
    state_links = {}
    get_drop_down_pt1 = soup.find(class_= 'dropdown-menu SearchBar-keywordSearch')

    baseurl = 'https://www.nps.gov'
    for state in get_drop_down_pt1.find_all('a'):
        state_links[state.text.lower()] = baseurl+state.get('href')

    return state_links


def get_site_instance(site_url):
    '''Make an instances from a national site URL.

    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov

    Returns
    -------
    instance
        a national site instance
    '''

    unique_key = construct_unique_key(site_url)
    CACHE_DICT = open_cache()
    if unique_key in CACHE_DICT.keys():
        print("Using Cache")
        response = make_request_with_cache(site_url)
        soup = BeautifulSoup(response, 'html.parser')

    else:
        print("Fetching")

        response = make_request_with_cache(site_url)
        CACHE_DICT[unique_key] = response
        save_cache(CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')

    category = soup.find('span', class_="Hero-designation").text
    name = soup.find('a', class_="Hero-title").text
    address = soup.find('span', itemprop="addressLocality").text +', '+ soup.find('span', itemprop="addressRegion").text
    zipcode = soup.find('span', class_="postal-code").text.strip()
    phone = soup.find('span', class_="tel").text.strip()

    site_instance = NationalSite(category= category, name=name, address=address, zipcode=zipcode, phone=phone)

    return site_instance


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.

    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov

    Returns
    -------
    list
        a list of national site instances
    '''
    baseurl_pt1 = 'https://www.nps.gov'
    baseurl_pt2 = 'index.htm'

    unique_key = construct_unique_key(state_url)
    CACHE_DICT = open_cache()
    if unique_key in CACHE_DICT.keys():
        print("Using Cache")
        response = make_request_with_cache(state_url)
        soup = BeautifulSoup(response, 'html.parser')
    else:
        print("Fetching")
        response = make_request_with_cache(state_url)
        CACHE_DICT[unique_key] = response
        save_cache(CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')

    find_main = soup.find('div', id='parkListResultsArea')
    links_list = find_main.find_all('h3')

    site_instances = []
    for links in links_list:
        href_container = links.find_all('a')
        for href_link in href_container:
            site_link = baseurl_pt1+href_link.get('href')+baseurl_pt2
            part_1 = get_site_instance(site_link)
            site_instances.append(part_1)

    return site_instances


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.

    Parameters
    ----------
    site_object: object
        an instance of a national site

    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''

    params = {
    "key": map_key,
    "origin": site_object.zipcode,
    "radius": 10,
    "units": "m", #miles
    "maxMatches": 10,
    "ambiguities": "ignore",
    "outFormat": "json",
    }

    baseurl = "http://www.mapquestapi.com/search/v2/radius"

    unique_key = construct_unique_key(site_object.zipcode)
    CACHE_DICT = open_cache()
    if unique_key in CACHE_DICT.keys():
        print("Using Cache")
        return CACHE_DICT[unique_key]
    else:
        print("Fetching")
        response = requests.get(baseurl, params=params)
        map_result = response.json()
        CACHE_DICT[unique_key] = map_result
        save_cache(CACHE_DICT)

    map_results_list = {}
    for location_info in map_result["searchResults"]:
        nearby_name = location_info["name"]
        nearby_field = location_info["fields"]
        if nearby_field["group_sic_code_name"] != '':
            nearby_category = nearby_field["group_sic_code_name"]
        else:
            nearby_category = "no category"
        if nearby_field["address"] != '':
            nearby_address = nearby_address = nearby_field["address"]
        else:
            nearby_address = "no address"
        if nearby_field["city"] != '':
            nearby_city = nearby_field["city"]
        else:
            nearby_city = "no city"
        nearby_sentence = f"{nearby_name} ({nearby_category}): {nearby_address}, {nearby_city}"
        #map_results_list.append(nearby_sentence)
        map_results_list[f"{site_object.zipcode}"] = nearby_sentence
    return map_results_list



if __name__ == "__main__":

    state_links = build_state_url_dict()
    while True:
        search_1 = input("Enter a state name (E.g. Michigan, michigan) or 'exit': ")
        if search_1.lower() != "exit":
            for key, value in state_links.items():
                if search_1.lower() == key:
                    sites_instances_states = get_sites_for_state(value)
                    sites_for_states = []
                    for instances in sites_instances_states:
                        sites_for_states.append(instances.info())
        else:
            exit()
        print("---------------------------------------")
        print(f"List of national sites in {search_1}")
        print("---------------------------------------")
        for i in range(len(sites_for_states)):
            print(f"[{i+1}] {sites_for_states[i]}")

        search_2 = input("Choose the number for a detailied search or 'exit' or 'back': ")
        if search_2.isnumeric():
            for i in range(len(sites_for_states)):
                if int(search_2) == (i + 1):
                    a = int(search_2) - 1
                    list_nearby = get_nearby_places(sites_instances_states[a])
            print("--------------------------------------")
            print(f"Places near {sites_instances_states[a].name}")
            print("--------------------------------------")
            for i in range(len(list_nearby)):
                print(f"- {list_nearby[i]}")

        elif search_2 == "exit":
            exit()
        elif search_2 == "back":
            continue
