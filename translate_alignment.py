import json
import sys
import ollama

ifile = sys.argv[1]
ofile = sys.argv[2]
data = None
with open(ifile, 'r', encoding="UTF-8") as f:
    data = json.load(f)

out = []
for row in data:
    targets = row['target_ids']

    res = ollama.chat(model="alma", messages=[{'role': 'user', 'content': ' '.join(targets)}])['message']['content'].split('\n', 1)[0]
    print(' '.join(targets), '->', res)
    row['target_ids'] = [res]
    out.append(row)

with open(ofile, 'w', encoding="UTF_8") as f:
    json.dump(out, f, ensure_ascii=False)
    print("DONE")
    


