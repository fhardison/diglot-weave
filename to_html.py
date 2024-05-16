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


def parse_target_file(fpath):
    out = {} 
    with open(fpath, 'r', encoding="UTF-8") as f:
        for line in f:
            parts = line.strip().split('\t')
            id = parts[0]
            text = parts[2]
            out[id] = text
    return out


def read_json_to_source_target_dict(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    source_target_dict = {}
    for item in data:
        source_id = item.get("source_ids")
        target_ids = item.get("target_ids", [])  # Handle missing "target_ids":

        if source_id:
            if type(source_id[0]) == list:
                for sid in source_id[0]:
                    source_target_dict[sid] = sorted(target_ids)
            else:
                source_target_dict[source_id[0]] = sorted(target_ids)
    return source_target_dict


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


def to_p(vnum, buff, hebrew):
    dir = 'dir="rtl"' if hebrew else 'dir="ltr"'
    return f"<p class='verse{cl}' {dir}><sup>{int(vnum)}</sup> {' '.join(buff)}</p>"


LANG = sys.argv[1]
hebrew = LANG.upper().startswith("H")
tgt = './SBLGNT-BSB.tsv' if not hebrew else './WLC-YLT.txt'
json_tgt = './SBLGNT-BSB_alignment.json' if not hebrew else './WLC-YLT-manual.json'
target_file = './SBLGNT-BSB-target.txt' if not hebrew else './WLC-YLT-target.txt'
#hebrew = tgt == './WLC-LEB.txt'
books = defaultdict(list)
index_type = f'{"hebrew" if hebrew else "greek"}-index.html'
json_file = read_json_to_source_target_dict(json_tgt)
tgt_file = parse_target_file(target_file)


def get_text(id, gloss):
    tgt_ids = json_file.get(id, [])
    return '_'.join([tgt_file.get(x, '-') for x in tgt_ids])


cur_verse = None
cur_book = None
cur_chapter = None
buffer = []
data = csv_reader(tgt)
c = Counter([x['strongs'] for x in data])
chapter = []
for row in data:
    b, cp, v, _ = bcvid(row['identifier'])
    if v != cur_verse:
        if buffer:
            cl = ' greek'
            if hebrew:
                buffer = reversed(buffer)
                cl = ' hebrew'
            chapter.append(to_p(cur_verse, buffer, hebrew))
        buffer = []
        cur_verse = v
    if cp != cur_chapter:
        if cur_chapter:
            bk = book_map[int(cur_book)]
            template = Path('./template.html').read_text()
            fpath = f'./docs/{bk}-{int(cur_chapter)}.html'
            print(fpath)
            books[bk].append(fpath)
            Path(fpath).write_text(template.replace('$body$', '\n'.join(chapter)).replace('$index$', index_type))
            chapter = []
        cur_chapter = cp
    if b != cur_book:
        if chapter != []:
            bk = book_map[int(cur_book)]
            template = Path('./template.html').read_text()
            fpath = f'./docs/{bk}-{int(cur_chapter)}.html'
            print(fpath)
            books[bk].append(fpath)
            Path(fpath).write_text(template.replace('$body$', '\n'.join(chapter)).replace('$index$', index_type))
            chapter = []
        cur_book = b
    gloss = row['gloss']
    text = row['text']
    gloss = get_text(row['identifier'], gloss)
    count_lem = c[row['strongs']]
    dir = 'dir="rtl"' if hebrew else 'dir="ltr"'
    buffer.append(f'<span class="wrapper" x-count="{count_lem}"><span class="word visible" {dir}>{text}</span><span class="gloss hidden" dir="ltr">{gloss}</span></span>')
if buffer:
    cl = ' greek'
    if hebrew:
        buffer = reversed(buffer)
        cl = ' hebrew'
    chapter.append(to_p(cur_verse, buffer, hebrew))
    bk = book_map[int(cur_book)]
    template = Path('./template.html').read_text()
    fpath = f'./docs/{bk}-{int(cur_chapter)}.html'
    books[bk].append(fpath)
    Path(fpath).write_text(template.replace('$body$', '\n'.join(chapter)).replace('$index$', index_type))

index = []
for book, links in books.items():
    index.append(f'<h2>{book}</h2>')
    index.append('\n'.join([f"<a href='{l.replace('docs/', '')}'>{l.replace('docs/', '').replace('-', ' ').replace('.html', '')[2:]}</a>" for l in links]))


index_template = Path('./template.html').read_text()

Path(f'docs/{"hebrew" if hebrew else "greek"}-index.html').write_text(index_template.replace('$body$', '\n'.join(index)).replace('$index$', index_type))
