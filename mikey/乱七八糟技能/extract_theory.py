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

# precise prefix matches (full-width colon disambiguates 直播1 from 直播10)
targets = {
    'shenwei': '1.第一章.三伪神',
    'neizai': '第三章 内在价值',
    'ziwo': '第四章 自我',
    'why_nodate': '第五章 你为什么没有约会',
    'fenjue': '第二十四章 搭讪心态',
    'zb6_neihe': '直播6：',
    'zb2_chat': '直播2：',
    'zb3_bianjie': '直播3：',
    'zb17_invest': '直播17',
    'zb4_result': '直播4：',
    'zb37_bottom': '直播37：',
    'zb42_xintai': '直播42：',
    'zb1_jiben': '直播1：',
}

os.makedirs('D:/cc/_theory_extract', exist_ok=True)
files = [f for f in os.listdir('.') if f.endswith('.docx')]
manifest = []
for key, prefix in targets.items():
    matches = [f for f in files if prefix in f]
    if not matches:
        manifest.append(f'{key}: NOT FOUND ({prefix})')
        continue
    f = matches[0]
    txt = extract(f)
    out = f'D:/cc/_theory_extract/{key}.txt'
    with open(out, 'w', encoding='utf-8') as fh:
        fh.write(txt)
    manifest.append(f'{key}: {len(txt)} chars <- {f[:40]}')

with open('D:/cc/_theory_extract/_manifest.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(manifest))
print('done', len(manifest))
