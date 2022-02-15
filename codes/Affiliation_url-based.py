from datetime import datetime
import pandas as pd
import wptools

path = '_path_'
outpath = '_outpath_'

filename = '01.Affiliations.csv.gzip'

wiki_attributes = [
    'homepage', 'website', 'URL',
    'established', 'foundation', 'founded_date',
    'type',
    'acronym',
    'city', 'country', 'state', 'location', 'headquarters'
]


def wiki_info(query):
    tmp = {}
    for feature in wiki_attributes:
        tmp[feature] = ''
    try:
        so = wptools.page(query, verbose=False).get_parse()
        infobox = so.data['infobox']
        # title = so.data['title']
        if infobox:
            for feature in wiki_attributes:
                try:
                    tmp[feature] = infobox[feature]
                except KeyError:
                    pass
    except LookupError:
        pass
    return tmp


def main():
    with open(outpath + 'affiliations_raw_wiki.txt', 'w') as out:
        header = ['entity_id']
        for feature in wiki_attributes:
            header.append(feature)
        out.write('\t'.join(header) + '\n')

        df = pd.read_csv(path + filename, compression='gzip')
        
        for i in df.index:
            data = {}
            query = ''
            try:
                query = df['wiki'][i].split('/')[-1]
            except:
                pass
            if query:
                if not pd.isnull(query):
                    data = wiki_info(query)

            if not data:
                for feature in wiki_attributes:
                    data[feature] = ''
            data = {k: v.replace('\t', '').replace('\n', '') for k, v in data.items()}
            if not len(data) == 13:
                break

            olist = [str(df['entity_id'][i])]
            for feature in wiki_attributes:
                olist.append(data[feature].strip().encode('utf-8'))
            out.write('\t'.join(olist) + '\n')

            
if __name__ == '__main__':
    main()
