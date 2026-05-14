"""Hand-curated prompt fixes for the worst residual 2000-2001 questions.

Each entry is (year, num, original_prompt, corrected_prompt). The script
verifies the original_prompt matches EXACTLY before replacing, so a
mismatch fails loudly rather than silently corrupting a different
question.

These are the strings the bootstrapped segmenter couldn't fix because
the corruption was a mix of merged AND mis-placed spaces (e.g.
`Piešinyjepavaizduotailgapopieriausjuo stelė` — both ends broken).
"""
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_JSON = os.path.join(HERE, 'kengura-archive.json')
ARCHIVE_JS   = os.path.join(HERE, 'kengura-archive.js')

FIXES = [
    ('2000', 5,
     'Vienas litras limonado turi 80% vandens. Kiek procentųvandens turės likęs limo- nadas, kai bus iš gerta pusė litro?',
     'Vienas litras limonado turi 80 % vandens. Kiek procentų vandens turės likęs limonadas, kai bus išgerta pusė litro?'),
    ('2000', 11,
     'Kiek dviženklių skaičiųdalijasi ir iš 2, ir iš 7?',
     'Kiek dviženklių skaičių dalijasi ir iš 2, ir iš 7?'),
    ('2000', 14,
     'Kiek laiko truks parašyti milijonąraidžių, jei per 1 minutę parašome 100 raidžių?',
     'Kiek laiko truks parašyti milijoną raidžių, jei per 1 minutę parašome 100 raidžių?'),
    ('2000', 19,
     'Vieno mamos kengūros šuolio ilgis yra 3 metrai ir trunka 1 sekundę; jos mažo sūnausšuolio ilgis yra 1 metras ir trunka pusę sekundės. Abi kengūro svienu metu iš tos pačios vietos pradeda šuoliuoti link eukalipto. Atstumas nuo pradinio taško ikimedžioyra 180 metrų. Kiek sekundžių mama kengūra prieeukali ptoturėslaukti savo sūnaus?',
     'Vieno mamos kengūros šuolio ilgis yra 3 metrai ir trunka 1 sekundę; jos mažo sūnaus šuolio ilgis yra 1 metras ir trunka pusę sekundės. Abi kengūros vienu metu iš tos pačios vietos pradeda šuoliuoti link eukalipto. Atstumas nuo pradinio taško iki medžio yra 180 metrų. Kiek sekundžių mama kengūra prie eukalipto turės laukti savo sūnaus?'),
    ('2000', 21,
     'O rganizuojantvasarosstovyklą, kurioje vienu metu poilsiaus 96 vaikai, reikia pasi- rinkti, į kokio didumo grupes suskirstyti vaikus taip, kad kiekvienoje grupėje būtų tiek pat vaikų. Kiekvienoje grupėje turi būti daugiau kaip 5, bet mažiau kaip 20 vaikų. Keliais būdais tai galima padaryti?',
     'Organizuojant vasaros stovyklą, kurioje vienu metu poilsiaus 96 vaikai, reikia pasirinkti, į kokio didumo grupes suskirstyti vaikus taip, kad kiekvienoje grupėje būtų tiek pat vaikų. Kiekvienoje grupėje turi būti daugiau kaip 5, bet mažiau kaip 20 vaikų. Keliais būdais tai galima padaryti?'),
    ('2000', 23,
     'Piešinyjepavaizduotailgapopieriausjuo stelė, padalytąi 2000 trikampių brūkšninė- mis linijomis. Ta rkime, kad juostelė (žr. kairįjį brėžinį) lankstoma per brūkšnines linijas skaičiais pažymėta tvarka taip, kad juostelė visą laiką užima horizontalią padėtį, ojau sulankstytakairėje juostelėsdalisužlenkiamaantdešinės(dešiniajame brėžinyje pavaizduota viršūnių K, L, M padėtis po pirmo lenkimo). L L K 2 4 6 8 1,2 4 6 8 1 3 5 7 3 5 7 K M M Kuriąiš žemiau pavaizduotųpadėčiųužims viršūnės K, L, M po 1999 lenkimų? L L M K M L K',
     'Piešinyje pavaizduota ilga popieriaus juostelė, padalyta į 2000 trikampių brūkšninėmis linijomis. Tarkime, kad juostelė (žr. kairįjį brėžinį) lankstoma per brūkšnines linijas skaičiais pažymėta tvarka taip, kad juostelė visą laiką užima horizontalią padėtį, o jau sulankstyta kairėje juostelės dalis užlenkiama ant dešinės (dešiniajame brėžinyje pavaizduota viršūnių K, L, M padėtis po pirmo lenkimo). Kurią iš žemiau pavaizduotų padėčių užims viršūnės K, L, M po 1999 lenkimų?'),
    ('2000', 28,
     'Kelių skirtingųmasiųdaiktus jūs galite pas verti vienu svėrimu dvilė kštėmis svars- tyklėmis turėdami tris svarsčius – 1, 3 ir 9 kg?',
     'Kelių skirtingų masių daiktus jūs galite pasverti vienu svėrimu dvilėkštėmis svarstyklėmis turėdami tris svarsčius – 1, 3 ir 9 kg?'),
    ('2000', 30,
     'Natūralusis skaičius N padalytas su liekana iš skaičių 11 ir 14. Kuris iš žemiau nurodytų skaičiųnegali būti gautųliekanųsuma?',
     'Natūralusis skaičius N padalytas su liekana iš skaičių 11 ir 14. Kuris iš žemiau nurodytų skaičių negali būti gautų liekanų suma?'),
    ('2001', 2,
     'Kuris iš žemiau pavaizduotų lapų atitinka sulankstytą lapą, pavaizduotądešinėje?',
     'Kuris iš žemiau pavaizduotų lapų atitinka sulankstytą lapą, pavaizduotą dešinėje?'),
    ('2001', 9,
     'Skaičius 14 užrašyta skaip pavaizduotapirmame pavei kslėlyje, skaičius 123–– kaip pavaizduotaantrame pavei kslėlyje. Koks skaičius užrašyta strečiame pavei kslėlyje? 1 1 2 1 4 2 3 6 4',
     'Skaičius 14 užrašytas kaip pavaizduota pirmame paveikslėlyje, skaičius 123 – kaip pavaizduota antrame paveikslėlyje. Koks skaičius užrašytas trečiame paveikslėlyje?'),
    ('2001', 10,
     'Kiekmažiausiaidegtukųreikia pridėti priepavaizduotos konfigūracijos, kad joje būtųlygiai 11 kvadratų?',
     'Kiek mažiausiai degtukų reikia pridėti prie pavaizduotos konfigūracijos, kad joje būtų lygiai 11 kvadratų?'),
    ('2001', 13,
     'Bėgimo varžybose buvo apdovanojami tik tie berniukai, kurie įveikė 10 kilometrų. Greitutis Trepsėnassugebėjoįveikti 9641 metrą,3456 decimetrusir 12340 milimetrų ir visiškai iš sekęs sustojo. Kiek centime trųjam pritrūko iki finišo linijos?',
     'Bėgimo varžybose buvo apdovanojami tik tie berniukai, kurie įveikė 10 kilometrų. Greitutis Trepsėnas sugebėjo įveikti 9641 metrą, 3456 decimetrus ir 12340 milimetrų ir visiškai išsekęs sustojo. Kiek centimetrų jam pritrūko iki finišo linijos?'),
    ('2001', 15,
     'Jeigu raudonasis slibinas turėtų 6 galvomis daugiau negu žaliasis, tai jiekartuturėtų 34 galvas. Bet iš tikrųjųraudonasis slibinas turi 6 galvomis mažiau negu žaliasis. Kiek galvųturi raudonasis slibinas?',
     'Jeigu raudonasis slibinas turėtų 6 galvomis daugiau negu žaliasis, tai jie kartu turėtų 34 galvas. Bet iš tikrųjų raudonasis slibinas turi 6 galvomis mažiau negu žaliasis. Kiek galvų turi raudonasis slibinas?'),
    ('2001', 18,
     'Prieštreji smetu strynukų Pauliaus, Simoir Viliausbeijųke tveriai smetaisvyresnės sesers Ulos amžiųsuma buvo 24 metai. Kiek metų Ulai dabar?',
     'Prieš trejus metus trynukų Pauliaus, Simo ir Viliaus bei jų ketveriais metais vyresnės sesers Ulos amžių suma buvo 24 metai. Kiek metų Ulai dabar?'),
    ('2001', 19,
     'Sodoplane kraštiniųilgiai nurodytime trais. Sodo 5 5 plotas kvadratiniais metrais lygus 5 10',
     'Sodo plane kraštinių ilgiai nurodyti metrais. Sodo plotas kvadratiniais metrais lygus'),
    ('2001', 21,
     'Pavaizduotųse ptyniųlazdelių ilgiai vienodi; vienodi ir tarpai tarp lazdelių. Koks yra ilgis kiekvienos iš vienodo ilgio dalių, pažymėtų klaustukais? 80cm 14cm ?cm ?cm',
     'Pavaizduotų septynių lazdelių ilgiai vienodi; vienodi ir tarpai tarp lazdelių. Koks yra ilgis kiekvienos iš vienodo ilgio dalių, pažymėtų klaustukais? (80 cm, 14 cm, ? cm, ? cm)'),
    ('2001', 22,
     'Atrakcionųparko apžvalgos rato kabinos sužymėtos nu- meriais 1, 2, 3 irt. t., tarp aitarpjųvienodi. Tuomomen- tu, kai 25-ta kabina atsiduria žemiausioje padėtyje, 8-ta kabinaatsiduriaau kščiausioje padėtyje. Kiekkabinųturi apžvalgos ratas?',
     'Atrakcionų parko apžvalgos rato kabinos sužymėtos numeriais 1, 2, 3 ir t. t., tarpai tarp jų vienodi. Tuo momentu, kai 25-ta kabina atsiduria žemiausioje padėtyje, 8-ta kabina atsiduria aukščiausioje padėtyje. Kiek kabinų turi apžvalgos ratas?'),
    ('2001', 23,
     'Šimtametis bukas per valandąišskiria 1,7 kg deguonies. Kiek tokių bukų reikia, kad jųišskirto deguonies užtektų 34 mokiniams vienai valandai, jeigu kiekvienam mokiniui per valandąreikia 0,7 kg deguonies?',
     'Šimtametis bukas per valandą išskiria 1,7 kg deguonies. Kiek tokių bukų reikia, kad jų išskirto deguonies užtektų 34 mokiniams vienai valandai, jeigu kiekvienam mokiniui per valandą reikia 0,7 kg deguonies?'),
]


def main():
    with open(ARCHIVE_JSON, encoding='utf-8') as f:
        data = json.load(f)
    applied = 0
    skipped = 0
    for year, num, before, after in FIXES:
        # find the year + question
        yt = next((y for y in data['archive'] if y['year'] == year), None)
        if not yt:
            print(f'SKIP {year}-Q{num}: year not in archive')
            skipped += 1; continue
        q = next((q for q in yt['questions'] if q['num'] == num), None)
        if not q:
            print(f'SKIP {year}-Q{num}: question not in year')
            skipped += 1; continue
        if q.get('prompt') != before:
            print(f'SKIP {year}-Q{num}: prompt does not match expected')
            print(f'  actual: {q.get("prompt","")[:120]}')
            print(f'  exp:    {before[:120]}')
            skipped += 1; continue
        q['prompt'] = after
        applied += 1
        print(f'OK   {year}-Q{num}')

    print(f'\nApplied {applied} / Skipped {skipped}')
    if applied:
        with open(ARCHIVE_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        with open(ARCHIVE_JS, 'w', encoding='utf-8') as f:
            f.write('window.KENGURA_ARCHIVE = ')
            json.dump(data, f, ensure_ascii=False)
            f.write(';\n')
        print(f'Wrote {ARCHIVE_JSON} and {ARCHIVE_JS}')


if __name__ == '__main__':
    main()
