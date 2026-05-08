"""Regenerate kengura-archive.js from kengura-archive.json (single-line)."""
import json

with open('kengura-archive.json', encoding='utf-8') as f:
    data = json.load(f)

with open('kengura-archive.js', 'w', encoding='utf-8') as f:
    f.write('window.KENGURA_ARCHIVE = ')
    json.dump(data, f, ensure_ascii=False, separators=(', ', ': '))
    f.write(';')

print('Wrote kengura-archive.js.')
