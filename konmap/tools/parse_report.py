"""Split a research report into site blocks with labelled fields.
usage: parse_report.py <report.md> <out blocks.json>
Site starts: '### A1. Name', '**12. Name** — A', or compact '- **A1 Name** — text'.
Fields are '- **Label:** text' lines inside a block."""
import re, json, sys
lines = open(sys.argv[1]).read().split('\n')
cat = None; blocks = []; cur = None
def close():
    global cur
    if cur: blocks.append(cur); cur = None
for ln in lines:
    h2 = re.match(r'^##\s+(?:Category\s+)?([ABC])\b', ln)
    if h2: close(); cat = h2.group(1); continue
    if re.match(r'^##\s', ln): close(); cat = None; continue
    m = re.match(r'^###\s+([ABC]\d+)\.?\s+(.*)', ln)
    m2 = re.match(r'^\*\*(\d+)\.\s+(.+?)\*\*\s*(?:—\s*([ABC]))?', ln)
    m3 = re.match(r'^- \*\*([ABC]\d+)\s+(.+?)\*\*\s*(?:\(([^)]*)\))?\s*—\s*(.*)', ln)
    if m and cat:
        close(); cur = {'key': m.group(1), 'cat': m.group(1)[0], 'title': m.group(2).strip(), 'f': {}, 'raw': ''}; continue
    if m2 and cat:
        close(); cur = {'key': (m2.group(3) or cat) + m2.group(1), 'cat': m2.group(3) or cat, 'title': m2.group(2).strip(), 'f': {}, 'raw': ''}; continue
    if m3:
        close(); cur = {'key': m3.group(1), 'cat': m3.group(1)[0], 'title': m3.group(2).strip(), 'note': m3.group(3), 'f': {'text': m3.group(4)}, 'raw': m3.group(4)}
        close(); continue
    if re.match(r'^###\s', ln): close(); continue
    if cur is None: continue
    f = re.match(r'^-\s+\*\*([^*]+?):\*\*\s*(.*)', ln)
    if f: cur['f'][f.group(1).strip()] = f.group(2).strip()
    cur['raw'] += ln + '\n'
close()
for b in blocks:
    t = ' '.join([b['raw']] + list(b['f'].values()))
    c = re.search(r'(-?\d{1,2}\.\d{2,6})\s*,\s*(-?\d{1,3}\.\d{2,6})', t)
    b['ll'] = [float(c.group(1)), float(c.group(2))] if c else None
json.dump(blocks, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
print(len(blocks), 'blocks;', sum(1 for b in blocks if b['ll']), 'with coords')
for b in blocks: print(' ', b['key'], (b['ll'] or ''), b['title'][:70])
