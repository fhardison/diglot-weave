from collections import Counter, defaultdict
from pathlib import Path
import csv
import sys

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
    return x[::-1]


LANG = sys.argv[1]
tgt = './SBLGNT-BSB.tsv' if LANG.upper().strip().startswith('G') else './WLC-LEB.txt'
hebrew = tgt == './WLC-LEB.txt'

books = defaultdict(list)
index_type = f'{"hebrew" if hebrew else "greek"}-index.html'

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
            chapter.append(f"<p class='verse{cl}'><sup>{int(cur_verse)}</sup> {' '.join(buffer)}</p>")
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
        cur_book = b
    gloss = row['gloss']
    text = row['text']
    count_lem = c[row['strongs']]
    dir = 'dir="rtl"' if hebrew else ''
    buffer.append(f'<span class="wrapper" x-count="{count_lem}"><span class="word visible" {dir}>{text}</span><span class="gloss hidden">{gloss}</span></span>')
if buffer:
    cl = ' greek'
    if hebrew:
        buffer = reversed(buffer)
        cl = ' hebrew'
    chapter.append(f"<p class='verse {cl}'><sup>{int(cur_verse)}</sup> {' '.join(buffer)}</p>")
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
