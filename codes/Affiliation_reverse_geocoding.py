from geopy.geocoders import Nominatim
import reverse_geocoder
import pandas as pd
import pycountry
import csv
from datetime import datetime

path = '01.Affiliations.csv'
out_path = 'affiliations_reverse_geocoding.csv'
geo_locator = Nominatim(user_agent="_user_agent_")


def geopy_data(loc):
    city, state, post_code, country, country_code = '', '', '', '', ''

    if loc:
        try:
            city, state, post_code, country = list([x.strip() for x in loc.address.split(',')[-4:]])
        except ValueError: # some loc do not have postcode
            try:
                city, state, country = list([x.strip() for x in loc.address.split(',')[-3:]])
                post_code = ''
            except ValueError:
                city, state, post_code, country, country_code = '', '', '', '', ''
        try:
            country_code = pycountry.countries.search_fuzzy(country)[0].alpha_2
        except LookupError:
            country_code = ''

    return city, state, post_code, country, country_code


def geo(lat, lon):
    if lat and lon:
        try:
            loc_geopy = geo_locator.reverse('%s, %s' % (lat, lon), exactly_one=True)
        except ValueError:
            loc_geopy = None
        try:
            loc_rg = reverse_geocoder.search((lat, lon))
        except IndexError:
            loc_rg = None

        city, state, post_code, country, country_code = geopy_data(loc_geopy)
        country_code1 = loc_rg[0]['cc']
        country2 = ''

        if country_code and country_code1:
            if country_code != country_code1:
                country2 = country_code1
        else:
            if country_code1:
                country_code = country_code1
                city, state, post_code, country = loc_rg[0]['name'], loc_rg[0]['admin1'], '', ''
                try:
                    country = loc_rg[0]['country']
                except KeyError:
                    pass
                # FUZZY COUNTRY
        country_info = pycountry.countries.get(alpha_2=country_code)
        alpha2, alpha3, official, standardised_country = country_data(country_info, country)

        if not standardised_country:
            standardised_country = country
            print('ERROR * ' * 5)

        return [city, state, post_code, standardised_country, country_code, alpha3, official, country2]
    else:
        return ['', '', '', '', '', '', '', '']


def country_data(cdata, cname):
    try:
        a2 = cdata.alpha_2
        a3 = cdata.alpha_3
        standard_name = cdata.name
        try:
            off = cdata.official_name
        except AttributeError:
            off = cname
        return a2, a3, off, standard_name
    except AttributeError:
        try:
            a2 = cdata[0].alpha_2
            a3 = cdata[0].alpha_3
            standard_name = cdata[0].name
            try:
                off = cdata[0].official_name
            except AttributeError:
                off = cname
            return a2, a3, off, standard_name
        except TypeError:
            return '', '', '', ''


def main():
    df = pd.read_csv(path)
    df = df.fillna('')

    with open(out_path, 'a') as out_csv:
        writer = csv.writer(out_csv)
        header = ['entity_id', 'class', 'foaf_name',
                  'pos#lat', 'pos#long',
                  'city_name', 'state_name', 'postcode', 'country_name', 'country_alpha2', 'country_alpha3', 'country_official_name',
                  'country_2']
        writer.writerow(header)

        for index, row in df.iterrows():
            latitude, longitude = row['pos#lat'], row['pos#long']

            # city_name, state_name, postcode, country_name, country_alpha2, country_alpha3, country_official_name = geo(lat=latitude, lon=longitude)
            geo_data = geo(lat=latitude, lon=longitude)

            out_row = []
            out_data_list = ['entity_id', 'class', 'foaf_name',
                  'pos#lat', 'pos#long']
            for x in out_data_list:
                out_row.append(row[x])
            out_row = out_row + geo_data

            writer.writerow(out_row)

    # merging data
    result_path = '/Volumes/LauraExt/MAKG20200619/dataset/Affiliations_geolocalised.csv'

    df = pd.read_csv(path)
    df1 = pd.read_csv(out_path)

    result = pd.merge(df, df1[['city_name', 'state_name', 'postcode', 'country_name', 'country_alpha2',
                               'country_alpha3', 'country_official_name', 'entity_id', 'country_2']], on="entity_id")

    result = result[['entity_id', 'class', 'rank', 'foaf_name', 'foaf_homepage', 'wiki', 'paperCount',
                     'paperFamilyCount', 'citationCount', 'pos#lat', 'pos#long', 'city_name', 'state_name', 'postcode',
                     'country_name', 'country_alpha2', 'country_alpha3', 'country_official_name', 'country_2']]
    result.to_csv(result_path, index=False)


if __name__ == '__main__':
    main()
