from collections import Counter, defaultdict
from pathlib import Path
import csv
import sys
import json


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
    return data
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


def loop_apply(xs, f):
    out = []
    for x in xs:
        if type(x) == list:
            out.append(loop_apply(x, f))
        else:
            if not x.strip():
                out.append('')
            else:
                out.append(f(x))
    return out



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
source_map = {row['identifier']:row['text'] for row in csv_reader(tgt)}

out = []

for row in json_file:
    source = row.get('source_ids', [])
    targets = row.get('target_ids', [])
    if source and source  != ['']:
        try:
            out.append({
            'id': row['id'],
            'source_ids': loop_apply(source, lambda x: source_map[x]),
            'target_ids': loop_apply(targets, lambda x: tgt_file[x])
            })
        except KeyError:
            print(source, targets)
            exit()

with open(('hebrew' if hebrew else 'greek') + '-map.json', 'w', encoding="UTF-8") as f:
    #dump json file with pretty printing of 2 spaces
    json.dump(out, f, ensure_ascii=False)
print("DONE")

