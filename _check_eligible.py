"""Mirror of the kengura.html contest filter. Prints the picker as the kid sees it."""
import json

with open('kengura-archive.json', encoding='utf-8') as f:
    data = json.load(f)

elig = []
for t in data['archive']:
    qs = t['questions']
    has_all_keys = all(q.get('correct') for q in qs)
    has_garbled = any(q.get('hasMissingOptionText') for q in qs)
    is_2006 = t['year'] == '2006'
    if (not is_2006) and len(qs) >= 28 and has_all_keys:
        elig.append(t['year'])
    n_garbled = sum(1 for q in qs if q.get('hasMissingOptionText'))
    n_no_key = sum(1 for q in qs if not q.get('correct'))
    flag = 'OK' if t['year'] in elig else '--'
    note = []
    if is_2006: note.append('Mažylis (excluded by rule)')
    if n_no_key: note.append(f'{n_no_key} unkeyed')
    if n_garbled: note.append(f'{n_garbled} garbled')
    print(f'  {t["year"]}: {len(qs)}qs  [{flag}]  {", ".join(note) if note else ""}')

print(f'\nEligible years ({len(elig)}): {", ".join(elig)}')
