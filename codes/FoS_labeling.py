import csv
from collections import defaultdict
from collections import Counter
from datetime import datetime

path_fos = '15.FieldsOfStudy.csv'
path_fos_children = '13.FieldOfStudyChildren.csv'

out_path = 'FoS_labeled.csv'


def get_fos():
    f = dict()
    with open(path_fos, 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        next(csv_reader)
        for row in csv_reader:
            entity, eclass, name, rank, lvl, pfcount, ccount, pcount = row
            f[entity] = [name, lvl]
    return f


def get_children():
    c = defaultdict(lambda: list())
    # p = defaultdict(lambda: list())
    with open(path_fos_children, 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        next(csv_reader)
        for row in csv_reader:
            entity, parent = row
            c[entity].append(parent)
            # p[parent].append(entity)
    return c


def main():
    fos = get_fos()
    fos_children = get_children()

    print(datetime.now(), 'FoS', len(fos), 'Children:', len(fos_children))

    res = defaultdict(lambda: list())
    for level in range(0, 5 + 1):

        for k, v in fos.items():
            if level == 0 and v[1] == str(level): # level 0 fields are directly added
                res[k] = [v[0]]
            elif str(level) == v[1]:
                if len(fos_children[k]) > 0:
                    for parent in fos_children[k]:
                        for fos_parent in res[parent]:
                            res[k].append(fos_parent)
                else: # no parents
                    res[k].append('-') # thus, no fos

    print(datetime.now(), 'FoS', len(fos), 'Children:', len(fos_children), 'Res:', len(res))

    with open(out_path, 'w') as out_csv:
        writer = csv.writer(out_csv)
        header = ['entity_id', 'fos_list']
        writer.writerow(header)

        for k, v in res.items():
            lst = [el for el in v if el != '-'] # exclude - to not bias percentages
            if len(lst) == 0:
                out_perc = ['-:0.0']  # no parents, 0.0 fos
            else:
                counter_fos = Counter(lst)
                fos_scores = [(i, counter_fos[i] / len(lst)) for i in counter_fos] # percentages
                fos_scores_sorted = sorted(fos_scores, key=lambda x: x[1], reverse=True)

                out_perc = ['%s:%s' % (f, round(fp, 2)) for f, fp in fos_scores_sorted]
            out_list = [k, '_'.join(out_perc)]
            writer.writerow(out_list)


if __name__ == '__main__':
    main()
