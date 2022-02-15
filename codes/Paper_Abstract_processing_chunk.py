import csv
from langdetect import detect
import spacy
import html
import string
from datetime import datetime
from collections import Counter

# SPACY LANGUAGE MODULES
nlp_en = spacy.load('en_core_web_sm')
nlp_da = spacy.load('da_core_news_sm')
nlp_de = spacy.load('de_core_news_sm')
nlp_fr = spacy.load('fr_core_news_sm')
nlp_es = spacy.load('es_core_news_sm')
nlp_it = spacy.load('it_core_news_sm')
nlp_pt = spacy.load('pt_core_news_sm')
nlp_pl = spacy.load('pl_core_news_sm')
nlp_nl = spacy.load('nl_core_news_sm')
nlp_ro = spacy.load('ro_core_news_sm')
nlp_ja = spacy.load('ja_core_news_sm')

#
chunk_n_start, chunk_n_end = 0,1
folder = '_folder_name_'
outf = '_out_folder_name_'
field_names = ['entity_id', 'text', 'language', 'tokens', 'types']

allowed_langs = ['da', 'de', 'fr', 'en', 'it', 'pt', 'es', 'pl', 'nl', 'ro', 'ja']
allowed_postags = ['NOUN', 'VERB', 'ADV', 'ADJ']
lang_models = {
    'en': nlp_en,
    'de': nlp_de,
    'da': nlp_da,
    'fr': nlp_fr,
    'es': nlp_es,
    'it': nlp_it,
    'pt': nlp_pt,
    'pl': nlp_pl,
    'nl': nlp_nl,
    'ja': nlp_ja,
    'ro': nlp_ro
}


def main():
    lst_c = [x for x in range(chunk_n_start, chunk_n_end)]

    for chunk_n in lst_c:

        print(datetime.now(), 'chunk started', chunk_n)

        namefile = outf + 'Abstracts_chunk_%s.csv' % chunk_n
        outrows = list()
        with open(folder + 'abs_chunk_%s.txt' % chunk_n, 'r') as infile:
            for line in infile:
                paper, abstract = line.strip().split('\t')[0], line.strip().split('\t')[1]

                try:
                    lang = detect(abstract)
                except:
                    lang = 'unk'

                formatted_tokens, types = [''], ['']

                if lang in allowed_langs:
                    preprocessed_abs = (html.unescape(abstract)).translate(str.maketrans('', '', string.punctuation))
                    nlp = lang_models[lang]

                    doc_tokens = nlp(preprocessed_abs.lower())
                    tokens = [token.orth_ for token in doc_tokens if not token.is_punct | token.is_space]
                    tokens_str = ' '.join(list(set(tokens)))
                    tokens_counter = Counter(tokens).most_common()
                    formatted_tokens = [x + '_' + str(y) for (x, y) in tokens_counter]

                    doc_lemmas = nlp(tokens_str.lower())
                    types = [i.lemma_ for i in doc_lemmas if i.pos_ in allowed_postags and i.is_alpha]
                    types = [x for x in list(set(types)) if len(x) > 1]

                out_list = [paper, abstract, lang, ','.join(formatted_tokens), ','.join(list(set(types)))]
                outrows.append(out_list)


        print(datetime.now(), len(outrows))
        csv_file = open(namefile, 'w')
        write = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        write.writerow(field_names)
        for el in outrows:
            write.writerow(el)

        csv_file.close()

        print(datetime.now(), 'chunk terminated', chunk_n)


if __name__ == '__main__':
    main()


