"""Revert the 4 hand-guessed answer keys to null until a Mažylis solution PDF
verifies them.

These were ~60-70 % confidence guesses, not extracted from a primary source.
For contest prep, a wrong key is worse than no key — the kid would see a
correct answer marked wrong and start mistrusting their own reasoning.
"""
import json

UNVERIFIED = {
    ('2000',  8),   # ribbon-wrapped box: best guess A (3-axis wrap, 200 cm)
    ('2000', 15),   # longest fence: best guess C (I-beam shape)
    ('2000', 24),   # hexagon - diamond area: best guess C (12)
    ('2001', 10),   # matchsticks for 11 squares: best guess C (4)
}

with open('kengura-archive.json', encoding='utf-8') as f:
    data = json.load(f)

for tier in data['archive']:
    for q in tier['questions']:
        if (tier['year'], q['num']) in UNVERIFIED:
            print(f'  reverting {tier["year"]}-Q{q["num"]} (was {q.get("correct")!r})')
            q['correct'] = None

with open('kengura-archive.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('done')
