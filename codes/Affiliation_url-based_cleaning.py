import re
import spacy
from geotext import GeoText
import pycountry
from geopy.geocoders import Nominatim
import csv

path = 'affiliations_raw_wiki.txt'
out_path = 'affiliations_wiki.csv'

nlp = spacy.load("en_core_web_sm")
geolocator = Nominatim(user_agent='_user_agent_name_')

repls = ['(', ')', '[', ']', '{', '}', '<br>', '</br>']
usa_sinonyms = ['U.S.', 'USA', 'U.S.A.']
country_repls = {
    'Cape Verde': 'Republic of Cabo Verde',
    'Laos': "Lao People's Democratic Republic",
    'North Korea': "Democratic People's Republic of Korea",
    'South Korea': 'Republic of Korea',
}


def find_url(s):
    url = ''
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?]))"
    try:
        url = re.findall(regex, s)[0][0]
    except IndexError: pass
    return url


def find_date_year(s):
    date = ''
    try:
        date = str(min([int(x) for x in re.findall(r"(\d{4})", s)]))
    except ValueError:
        pass
    return date


def remove_textPar(s):
    to_replace = re.findall(r'\([^]]*\)', s)
    for el in to_replace:
        s = s.replace(el, '')
    return s


def remove_par(s):
    s = s.replace('[', '').replace(']', '')
    return s


def search_for_city(s):
    try:
        standardised_city = GeoText(s).cities[0]
    except IndexError:
        standardised_city = None
    return standardised_city


def search_for_country(s):
    try:
        standardised_country = GeoText(s).countries[0]
        standardised_country_info = pycountry.countries.get(name=standardised_country)
        if not standardised_country_info:
            try:
                standardised_country_info = pycountry.countries.search_fuzzy(standardised_country)
            except LookupError:
                if standardised_country in country_repls.keys():
                    standardised_country = country_repls[standardised_country]
                    try:
                        standardised_country_info = pycountry.countries.search_fuzzy(country_repls[standardised_country])[0]
                    except LookupError:
                        standardised_country_info = None
    except IndexError:
        standardised_country = None
        standardised_country_info = None
    return standardised_country, standardised_country_info


def country_data(cdata, cname):
    try:
        a2 = cdata.alpha_2
        a3 = cdata.alpha_3
        try:
            off = cdata.official_name
        except AttributeError:
            off = cname
        return a2, a3, off
    except AttributeError:
        a2 = cdata[0].alpha_2
        a3 = cdata[0].alpha_3
        try:
            off = cdata[0].official_name
        except AttributeError:
            off = cname
        return a2, a3, off


def main():
    with open(out_path, 'a') as out_csv:
        writer = csv.writer(out_csv)
        header = ['entity_id', 'foundation_date', 'url', 'type_entities', 'acronym',
                  'city_name', 'city_lat', 'city_lon',
                  'state_name', 'country_name', 'alpha_2', 'alpha_3', 'country_official']
        writer.writerow(header)

        with open(path, 'r') as infile:
            next(infile)
            for line in infile:
                lsp = line.split('\t')

                # url: homepage, website, URL
                url = ''
                try:
                    raw_url = [x for x in lsp[1:4] if x][0]
                    url = find_url(raw_url)
                except IndexError:
                    pass

                # foundation: established, foundation, founded_date
                foundation = ''
                try:
                    raw_foundation = [x for x in lsp[4:7] if x][0]
                    foundation = find_date_year(raw_foundation)
                except IndexError:
                    pass

                # type
                raw_type = lsp[7]
                for x in repls:
                    raw_type = raw_type.replace(x, '')
                raw_type_lst = raw_type.split('|')
                type_entities = []
                for el in raw_type_lst:
                    doc = nlp(el)
                    for ent in doc.ents:
                        if ent.label_ in ['ORG', 'NORP']:
                            type_entities.append((ent.text.replace(' ', '_'), ent.label_))
                type_entities = list(set(type_entities))
                type_entities = ','.join(map(lambda x: str(x[0]) + ':' + str(x[1]), type_entities))

                # acronym
                acronym = lsp[8]
                if acronym:
                    acronym = re.findall(r"([A-Z]+-*[A-Z]+)", acronym)[0]

                # city
                city = ''
                try:
                    raw_city = [x.strip() for x in [lsp[9], lsp[12], lsp[13]] if x.strip()][0]
                    city = re.findall(r'\[[^]]*\]', raw_city)[0]
                    city = remove_textPar(city)
                except IndexError: pass
                city = remove_par(city).split(',')[0].split('|')[0]

                # country
                country = remove_par(lsp[10])
                if country in usa_sinonyms:
                    country = 'United States'

                # state
                state_name = remove_par(lsp[11]).split('|')[0]

                # GEO
                city_name = search_for_city(city)
                country_name, country_info = search_for_country(country)

                # State if not country
                if state_name and not country_name:
                    country_name, country_info = search_for_country(state_name)

                # City info - Country if not
                city_info = None
                if city_name:
                    city_info = geolocator.geocode(city_name)
                    if not country_name:
                        city_info_country = city_info.address.split(',')[-1].strip()
                        country_name, country_info = search_for_country(city_info_country)

                # city latitude and longitude
                if city_info:
                    city_lat, city_lon = city_info.latitude, city_info.longitude
                else:
                    city_lat, city_lon = '', ''

                # Country info
                alpha_2, alpha_3, official_name = '', '', ''
                if country_info:
                    alpha_2, alpha_3, official_name = country_data(country_info, country_name)

                out_row = [lsp[0], foundation, url, type_entities, acronym,
                           city_name, city_lat, city_lon,
                           state_name, country_name, alpha_2, alpha_3, official_name]
                out_row = ['' if x is None else x for x in out_row]
                # print(out_row)
                writer.writerow(out_row)


if __name__ == '__main__':
    main()
