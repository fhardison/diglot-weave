from collections import Counter, defaultdict
from pathlib import Path
import csv
import sys
import json

#c = Counter(get_tokens(TokenType.lemma))
books_of_the_bible = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
    "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah",
    "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel",
    "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
    "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John",
    "Acts of the Apostles", "Romans", "1 Corinthians", "2 Corinthians",
    "Galatians", "Ephesians", "Philippians", "Colossians",
    "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy",
    "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude",
    "Revelation"
]
book_map = {i+1: n for i, n in enumerate(books_of_the_bible)}
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
    return x
    return x[::-1]


strongs_map = {}
with open('strongs_map.tsv', 'r', encoding="UTF-8") as f:
    for line in f:
        if not line.strip():
            continue
        if '\t' in line.strip():
            strongs, lemma = line.strip().split('\t', maxsplit=1)
            strongs_map[strongs] = lemma
        else:
            strongs_map[line.strip()] = ''

def get_strongs(x, hebrew):
    if hebrew:
        strongs = 'H' + x
    else:
        strongs = 'G' + x
    return strongs_map.get(strongs, strongs)


def do_file(tgt, hebrew):
    words_by_cpt = defaultdict(set)
    data = csv_reader(tgt)
    c = Counter([get_strongs(row['strongs'], hebrew) for row in data])
    for row in data:
        b, cp, v, _ = bcvid(row['identifier'])
        strongs = row['strongs']
        if hebrew:
            strongs = 'H' + strongs
        else:
            strongs = 'G' + strongs
        words_by_cpt[strongs_map.get(strongs, strongs)].add(f"{b}{cp}")
    with open(('hebrew-' if hebrew else 'greek-') + 'vocabulary_data.tsv', 'w', encoding="UTF-8") as f:
        for word, cpts, freq in sorted([(k, str(len(v)), c[k]) for k,v in words_by_cpt.items()], key=lambda x:int(x[1]), reverse=True):
            f.write('\t'.join((word, cpts, str(freq))) + '\n')

do_file('./WLC-LEB.txt', True)
do_file('./SBLGNT-BSB.tsv', False)

print("DONE")
