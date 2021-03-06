import requests
from bs4 import BeautifulSoup as bs


def get_connection(url):
    """Create connection and use bs for parse data"""
    try:
        r = requests.get(url)
    except requests.exceptions.HTTPError as err:
        raise exit(err)
    soup = bs(r.text, "html.parser")
    return soup


def get_cities_url(district_url):
    """Create a list of urls of all cities in chosen district"""
    soup = get_connection(district_url)

    links = []
    for a in soup.find_all('a', href=True):
        if "vyber" in a['href']:
            links.append('https://volby.cz/pls/ps2017nss/' + a['href'])
        else:
            continue
    format_links = list(dict.fromkeys(links))

    return format_links


def get_location_code(district_url):
    """Create a dictionary that contains cities codes as keys and cities names as values"""
    soup = get_connection(district_url)

    codes = [code.text for code in soup.find_all("td", {"class": "cislo"})]
    locations = [location.text for location in soup.find_all("td", {"class": "overflow_name"})]
    sorted_codes_locations = zip(codes, locations)

    return dict(sorted_codes_locations)


def get_vote_data(city_url):
    """
    Scrape needed data - registered, envelopes, valid
    """
    soup = get_connection(city_url)
    # format data because of unwanted characters
    format_data = soup.find_all(text=True)
    for d in format_data:
        clean_data = d.replace("\xa0", "")
        d.replace_with(clean_data)

    # get registered, envelopes, valid
    registered = soup.find("td", {"class": "cislo", "headers": "sa2", "data-rel": "L1"})
    envelopes = soup.find("td", {"class": "cislo", "headers": "sa3", "data-rel": "L1"})
    valid = soup.find("td", {"class": "cislo", "headers": "sa6", "data-rel": "L1"})

    return registered.text, envelopes.text, valid.text


def get_political_parties_dict(city_url):
    """
        Scrape needed data from city_url to get number of votes for each political party
    """
    soup = get_connection(city_url)

    # format data because of unwanted characters
    format_data = soup.find_all(text=True)
    for d in format_data:
        clean_data = d.replace("\xa0", "")
        d.replace_with(clean_data)

    parties_names = [name.text for name in soup.find_all("td", {"class": "overflow_name"})]
    number_votes_table_1 = [vote.text for vote in soup.find_all("td", {"class": "cislo", "headers": "t1sa2 t1sb3"})]
    number_votes_table_2 = [vote.text for vote in soup.find_all("td", {"class": "cislo", "headers": "t2sa2 t2sb3"})]
    number_votes = number_votes_table_1 + number_votes_table_2

    return parties_names, number_votes


def get_data_all_url(cities_url):
    """
        Scrape from all urls - one url = one city
        I use generator because of amount of data
    """
    for data in cities_url:
        registered, envelopes, valid = get_vote_data(data)
        parties_names, number_votes = get_political_parties_dict(data)
        yield registered, envelopes, valid, parties_names, number_votes
