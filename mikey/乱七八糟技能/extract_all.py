import zipfile, re, os

def extract(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8', 'ignore')
    paras = re.split(r'</w:p>', xml)
    out = []
    for p in paras:
        texts = re.findall(r'<w:t[^>]*>(.*?)</w:t>', p)
        line = ''.join(texts)
        if line.strip():
            out.append(line)
    return '\n'.join(out)

SRC = 'D:/BaiduNetdiskDownload/m'
OUT = 'D:/cc/_zb'
os.makedirs(OUT, exist_ok=True)

files = [f for f in os.listdir(SRC) if f.endswith('.docx')]
done = 0
for f in files:
    m = re.search(r'直播(\d+)', f)
    if m:
        num = m.group(1)
        txt = extract(os.path.join(SRC, f))
        with open(f'{OUT}/zb{num}.txt', 'w', encoding='utf-8') as fh:
            fh.write(txt)
        done += 1

with open(f'{OUT}/_manifest.txt', 'w', encoding='utf-8') as fh:
    for n in sorted([int(re.search(r'zb(\d+)', x).group(1)) for x in os.listdir(OUT) if x.startswith('zb')]):
        p = f'{OUT}/zb{n}.txt'
        fh.write(f'直播{n}: {len(open(p, encoding="utf-8").read())} 字\n')
print('extracted', done, '直播')
