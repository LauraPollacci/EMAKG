
from collections import defaultdict
import pandas as pd
import csv
import unidecode

path_wiki = 'affiliations_wiki.csv'
path_geo = 'Affiliations_geolocalised.csv'

path_out = 'Affiliations_geo_integrated.csv'


def save_data(path_to_data):
    data = dict()
    with open(path_to_data, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            id_aff = row['entity_id']
            data[id_aff] = row
    return data


def add_geo_info(aff_dict, aff_id, wiki_aff_dict):
    for el in ['city_name', 'state_name', 'country_name']:
        aff_dict[aff_id][el] = wiki_aff_dict[aff_id][el]
    aff_dict[aff_id]['country_alpha2'] = wiki_aff_dict[aff_id]['alpha_2']
    aff_dict[aff_id]['country_alpha3'] = wiki_aff_dict[aff_id]['alpha_3']
    aff_dict[aff_id]['country_official_name'] = wiki_aff_dict[aff_id]['country_official']

    return aff_dict


def main():
    data_wiki = save_data(path_wiki)
    data_aff = save_data(path_geo)

    for aff, data in data_aff.items():
        geo_check = False
        if not data['pos#lat'] or not data['country_alpha2']:
            geo_check = True
        if geo_check:
            data_aff = add_geo_info(data_aff, aff, data_wiki)

        city_lat, city_lon = '', ''
        if data['country_alpha2'] and data['country_alpha2'] == data_wiki[aff]['alpha_2']:
            if not data_aff[aff]['city_name']:
                data_aff[aff]['city_name'] = data_wiki[aff]['city_name']
            if data_aff[aff]['city_name'] == data_wiki[aff]['city_name']:
                city_lat, city_lon = data_wiki[aff]['city_lat'], data_wiki[aff]['city_lon']
            if not data_aff[aff]['state_name']:
                data_aff[aff]['state_name'] = data_wiki[aff]['state_name']

        data_aff[aff]['city_lat'] = city_lat
        data_aff[aff]['city_lon'] = city_lon

        for el in ['foundation_date', 'type_entities', 'acronym']:
            data_aff[aff][el] = data_wiki[aff][el]

    res = pd.DataFrame(data_aff.values())
    cols = ['entity_id', 'class', 'foaf_name', 'foundation_date', 'type_entities', 'acronym',
            'pos#lat', 'pos#long',
            'city_name', 'city_lat', 'city_lon',
            'state_name', 'postcode', 'country_name', 'country_alpha2', 'country_alpha3', 'country_official_name',
            'country_2']
    res = res[cols]
    res = res.fillna('')

    res.to_csv(path_out, index=False)


if __name__ == '__main__':
    main()
