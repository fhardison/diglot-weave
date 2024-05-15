from gnt_data import get_tokens
from collections import Counter
import pythonbible as bible
import csv
import sys

#c = Counter(get_tokens(TokenType.lemma))

def bcvid(x):
    #010010010011
    book = x[0:2]
    cpt = x[2:5]
    verse = x[5:8]
    id = x[8:]
    return (book, cpt, verse, id)


def csv_reader(fpath):
    data = []
    with open(fpath, 'r', encoding="UTF-8") as file:
        for row in csv.DictReader(file, delimiter='\t'):
            data.append(row)
    return data


def group_counts(data, group_size):
    sorted_data = data.most_common()
    groups = []
    current_group = []
    for element, count in sorted_data:
        current_group.append(element)
        if len(current_group) == group_size:
            groups.append(current_group)
            current_group = []
    if current_group:
        groups.append(current_group)
    return groups
# {'identifier': '40001001001', 'alt-id': 'Βίβλος-1', 'text': 'Βίβλος', 'strongs': '976', 'gloss': '[The] book', 'gloss2': 'book', 'pos': 'noun', 'morph': 'N-NSF'}


def reversed(x):
    return x[::-1]


LEVEL = int(sys.argv[1])
LANG = sys.argv[2]
BOOK = sys.argv[3]

tgt = './SBLGNT-BSB.tsv' if LANG.upper().strip().startswith('G') else './WLC-LEB.txt'
cur_verse = ''
buffer = []
data = csv_reader(tgt)
c = Counter([x['strongs'] for x in data])
counts = {}
groups = group_counts(c, 7)
for i, g in enumerate(groups):
    counts[i] = g
print(len(groups))
print('\n- '.join(counts[int(LEVEL /7)]))
hebrew = tgt == './WLC-LEB.txt'
for row in data:
    if row['identifier'].startswith(BOOK):
        b, cp, v, _ = bcvid(row['identifier'])
        print(bible.format_single_reference(bible.convert_verse_ids_to_references([int(b + cp + v)])[0]))
        if v != cur_verse:
            cur_verse = v
            if hebrew:
                print(reversed(' '.join(buffer) if buffer else ''))
            else:
                print(' '.join(buffer) if buffer else '')
            buffer = []
            if hebrew:
                buffer.append(reversed(str(int(v)) + '.'))
            else:
                buffer.append(str(int(v)) + '.')
        if c[row['strongs']] > LEVEL:
            if hebrew:
                buffer.append(row['text'])
            else:
                buffer.append(row['text'])
        else:
            if hebrew:
                buffer.append(reversed(row['gloss']))
            else:
                buffer.append(row['gloss'])
if buffer:
    if hebrew:
        print(reversed(' '.join(buffer)))
    else:
        print(' '.join(buffer))

