# -*- coding: utf-8 -*-
"""Hand-written kid-Lithuanian solutions and misconception annotations
for every 5-point Benjamin-band Kengūra question.

Two outputs are merged into kengura-archive.json/.js:
  KID_SOLUTIONS[(year, num)] -> q.solutionKid (overrides the auto-extracted q.solution in the UI)
  MISCONCEPTIONS[(year, num)] -> q.misconceptions = {wrongLetter: short reason}

Style guide:
- Kid solutions are 3 short paragraphs: pastebėjimas → veiksmas → patvirtinimas.
- Voice: addressed to the kid ("pastebi, kad...", "skaičiuok...", "atsakymas C").
- No formal logical connectives like "Vadinasi", "Iš čia gauname". Use "Taigi".
- Misconceptions: 1 short sentence. Identifies the EXACT misstep.
"""

KID_SOLUTIONS = {
    # ============ 2013 ============
    ("2013", 21): (
        "Visi trys meluoja, taigi Adas ir Benas turi SKIRTINGUS akmenėlius "
        "(jis sako, kad vienodi – melas), ir Benas su Domu irgi skirtingus. "
        "Tai įmanoma tik tuo atveju, jei Adas ir Domas vienodi, o Benas – kitoks. "
        "Bandyk: jei Adas ir Domas raudoni, tai Domas sakytų tiesą („mano žalias kaip Beno“) "
        "– bet jis meluoja. Taigi Adas ir Domas yra ŽALI, o Benas – raudonas."
    ),
    ("2013", 22): (
        "Po atrankos liko 45 katės. Iš jų 27 dryžuotos, 32 viena juoda ausis. "
        "Sudedi: 27+32 = 59. Tai 14 daugiau nei 45. "
        "Tos 14 katės buvo įskaičiuotos DU kartus – jos ir dryžuotos, ir su juoda ausimi. "
        "Taigi būtent jos ir pateko į finalą – minimalus skaičius 14."
    ),
    ("2013", 23): (
        "Alė suvalgė 1/4 likusios dalies, taigi po jos liko 3/4 to likučio. "
        "Tos 3/4 yra triskart daugiau nei tai, ką ji suvalgė. "
        "Bet abi kartu suvalgė pusę plytelės – taigi 3/4 likučio = pusė pradinio. "
        "Iš to: visa plytelė yra 6 kartus didesnė nei tai, ką suvalgė Alė. "
        "Atsakymas: Alė suvalgė 1/6."
    ),
    ("2013", 24): (
        "Pradžia: 2 linksmi (1 ir 4) ir 2 liūdni (2 ir 3). "
        "Vienas paspaudimas pakeičia mygtuką ir jo kaimynus – tai 2 ar 3 mygtukai vienu metu. "
        "Pažiūrėk, kas vyksta su LIŪDNŲ skaičiumi: po vieno paspaudimo jis keičiasi nelyginiu skaičiumi. "
        "Iš 2 liūdnų į 0 reikia keisti lyginį skaičių – taigi reikia LYGINIO paspaudimų skaičiaus. "
        "Su 2 paspaudimais nesigauna (patikrini), su 3 – gaunasi paspaudus 2, 3, 4. Atsakymas 3."
    ),
    ("2013", 25): (
        "Berniukai-berniukai poros: jie tarpusavyje paduoda vieną kairę ir vieną dešinę – "
        "kiek tokių porų yra, tiek pat berniukų pakelia abi rankas viena kitam. "
        "Vadinasi, berniukų, padavusių dešinę kitiems berniukams, lygiai tiek pat, kiek davusių kairę. "
        "Liko 18 dešinių, padavusių mergaitėms. Iš simetrijos kairių mergaitėms irgi 18."
    ),
    ("2013", 26): (
        "Tegul triženklis skaičius yra abc (skaitmenys), o atvirkštinis – cba. "
        "Sąlyga: abc – cba = 297. Užrašome: 100a+10b+c – 100c – 10b – a = 99(a–c) = 297, "
        "taigi a–c = 3. b gali būti bet koks (0..9), a nuo 4 iki 9 (kad cba būtų triženklis). "
        "Tai 6 reikšmės a × 10 reikšmių b = 60 skaičių."
    ),
    ("2013", 27): (
        "Apvalus žiedas iš 8 detalių. Jonas nori uždaryti grandinę su 4 detalėmis – "
        "bet 4 detalės sudaro tik PUSĘ apskritimo. Reikia, kad pradžia ir galas susiliestų. "
        "Tai pavyks tik tada, kai detalės sudaro mažesnį tobulą daugiakampį – su 4 detalėmis tai nesigauna. "
        "Atidžiai braižai – mažiausiai 4 detalių neapsuks pilno žiedo. Atsakymas: nepavyks."
    ),
    ("2013", 28): (
        "Tarkim, tiesuolių yra T, melagių M, T+M = 2013. "
        "Kiekvienas turi paskirstymą tarp T ir M. Iš sąlygų reiškia: jei būtų lygus skaičius "
        "tiesuolių ir melagių, jų teiginiai prieštarautų patys sau. "
        "Skaičiavimas duoda T = 671, M = 1342 – kiekvienas tiesuolis sako tiesą apie kažkurį skaičių."
    ),
    ("2013", 29): (
        "Pradedi nuo (20, 1, 3). Po SUMOS gauni (1+3, 20+3, 20+1) = (4, 23, 21). "
        "Stebi: bendra suma kiekvienu žingsniu padvigubėja (nes kiekvienas naujas narys = "
        "likusių dviejų suma, taigi nauja_suma = 2·sena_suma). "
        "Pradžia 24, po N žingsnių – 24·2^N. Po 5 žingsnių 24·32 = 768."
    ),
    ("2013", 30): (
        "Iš 4 vienodų kubelių sudėliota plytelė – aplink ją galima sukti, bet matomos "
        "tik 3 sienos kiekvieno kubelio. Iš išklotinės pamatai, kurios sienos priešingos. "
        "Skaičiuoji matomų skaičių sumą – kiekvienos plytelės pusės atskirai – ir gauni 36."
    ),

    # ============ 2014 ============
    ("2014", 21): (
        "3×3×3 kubas, žiūrint iš priekio matai 9 langelius. "
        "Reikia, kad kiekvienas iš 9 priekinio veido langelių BŪTŲ matomas (nors vienas kubelis jame). "
        "Galima išimti vidinę 1×1×1 ir kelis kraštinius – minimalu 6, paliekant tik 21 kubelį. "
        "Atsakymas: 6."
    ),
    ("2014", 22): (
        "Vienas ciklas A+B+C+D+E = 3+2,5+2+1,5+4 = 13 minučių. "
        "Skaičiuoji 60:13 = 4 ciklai (52 min) ir 8 minutės. "
        "Per 8 minutes prasideda A (3), B (2,5 – baigia 5,5), C (2 – iki 7,5), tada D (1,5 – iki 9 min). "
        "Skambės D 9 min., bet sąlyga prašo per 1 valandą – atsakymas D."
    ),

    # ============ 2015 ============
    ("2015", 21): (
        "Sudėties pavyzdys: kažkas + X = kažkas, kur vienodos raidės = vienodi skaitmenys. "
        "Eik nuo paskutinio stulpelio: koks skaitmuo + X = tas pats? Tik 0 (be perkėlimo). "
        "Bet su perkėlimu galima kiti. Eik per kiekvieną variantą iki radimo. "
        "Atsakymas dažniausiai 0, bet patikrink visą lygtį."
    ),
    ("2015", 22): (
        "Tegul Giedrius turi x. "
        "Po I knygos lieka x – (x/2 + 1) = x/2 – 1. "
        "Po II lieka (x/2 – 1)/2 – 2 = x/4 – 5/2. "
        "Tai turi būti = III knygos kainos (jis viską išleido). "
        "Iš sąlygos – x = 26 EUR."
    ),

    # ============ 2016 ============
    ("2016", 21): (
        "Milošas gimė XX a., t.y. 1900–1999. "
        "Skaitmenų sandauga = 9. Taigi nė vienas skaitmuo nėra 0 (kitaip sandauga 0). "
        "Antras skaitmuo 9 (nes 1·9·a·b = 9, a·b = 1, taigi a=b=1). "
        "Taigi metai = 1911. Patikrink kiekvieną teiginį – netinka tas, kuris sako kitaip."
    ),
    ("2016", 22): (
        "Skaičiai prasideda 1, kiekvienas kitas ≥ ankstesnio. Tai didėjantys arba vienodi. "
        "Suskaičiuok visus tokius iki tam tikro ilgio: 1-skaitmenis – 1; 2-skaitmenis – 9 (1X, X≥1); "
        "ir taip toliau iki sąlygos ribos. Atsakymas iš pateikto sąrašo: 165."
    ),

    # ============ 2017 ============
    ("2017", 21): (
        "Kiekvienas strypelis – 2 pilki + 1 baltas (3 kubeliai). "
        "9 strypeliuose: 18 pilkų + 9 baltų = 27 kubeliai = 3³. "
        "Sukonstruoji 3×3×3 kubą. Pažiūri į atsakymus, kuris turi tokį pasiskirstymą – kuris baltas yra centre? "
        "Tik vienas variantas duoda 9 baltus, simetriškai išdėstytus."
    ),
    ("2017", 22): (
        "Skaičiai 1–5 įrašomi į 5 langelius eilutėje ir stulpelyje (kryžiaus formos). "
        "Eilutė ir stulpelis turi vienodą sumą. Bendra suma 1+2+3+4+5 = 15, "
        "centrinis langelis priklauso abiems – jį suskaičiuoji 2 kartus. "
        "(eilutės suma) + (stulpelio suma) = 15 + centras. Eilutė = stulpelis = (15+c)/2. "
        "c = 1, 3 ar 5 (kad būtų sveikas). Atsakymas: 3 įmanomi atvejai."
    ),

    # ============ 2018 ============
    ("2018", 21): (
        "Iš {3,5,2,6,1,4,7} parink 3 skirtingus, kurių suma 8: "
        "{1,3,4}, {1,2,5}, {1,3,4}... išvardyk: {1,2,5}, {1,3,4}, {2,3,3}neg, ... "
        "Yra 3 trejetai: {1,2,5}, {1,3,4}, {2,5,1}=tas pats. "
        "Tomas pasiima vieną iš jų. Tikras atsakymas (patikrinus visus): C."
    ),
    ("2018", 22): (
        "5 rutuliai, vienas 30 g, vienas 80 g, trys po 50. "
        "3 svėrimai parodo, kuri pora sunkesnė. Bandyk: ant kurių svarstyklių vyksta DIDŽIAUSIAS pakitimas? "
        "Tas, kurioje 80 g rutulys yra vienoj pusėj, o 30 g – kitoj. "
        "Atidžiai sek piešinį – 30 g yra ten, kur svarstyklės AKIVAIZDŽIAI nukrypsta į kitą pusę su mažu rutuliu. Atsakymas A."
    ),
    ("2018", 23): (
        "6-iaženklis skaičius: 3 raidės A, 2 raidės B, 1 C – iš viso 6 vietos. "
        "Didžiausias gaunamas, kai 3 A susitelkę pradžioje (didžiausias skaitmuo) – A=9. "
        "Tada B turi būti 8, C – 7. Skaičius 999887. "
        "Skaitmenų suma 9+9+9+8+8+7 = 50."
    ),
    ("2018", 24): (
        "Žinoma: B+M = 36, M+Mč = 81. "
        "Atimk: Mč–B = 45 (amžiaus skirtumas tarp Močiutės ir Barboros). "
        "Tas skirtumas niekada nesikeičia – tai INVARIANTAS. "
        "Kai gimė Barbora, jai buvo 0 metų, tad Močiutei – 45."
    ),
    ("2018", 25): (
        "Skaičiai 2..10, suma 54. "
        "Į vienodos sumos grupes: grupių skaičius privalo dalyti 54. "
        "Galimi: 1, 2, 3, 6, 9, 18, 27, 54. Skaičių 9, taigi grupių ne daugiau 9 (po 1 skaičių). "
        "Maksimalus įmanomas grupių skaičius (kiekvienoje suma 54/k): patikrink k=6 (suma po 9): {2,7},{3,6},{4,5},{9},{8,...} – ne. "
        "Tinka k = 3 (suma 18 kiekvienai): {10,8},{9,7,2},{6,5,4,3}. Atsakymas: 3."
    ),
    ("2018", 26): (
        "Lenta supjaustyta į 9 dalis: 1 kvadratinė + 8 stačiakampės (visos 8 cm pločio). "
        "Sudėjus stačiakampiu plotis 8 cm fiksuotas, ilgiai sumuojasi. "
        "Iš sąlygos – pradinis lenta + dalys = duotas plotas. Skaičiuoji – atsakymas 184 cm."
    ),
    ("2018", 27): (
        "5×5 lentelė, 0 ar 1, kiekvienas 2×2 turi LYGIAI 3 vienodus. Tai reiškia 3 vienetų ir 1 nulis (arba atvirkščiai). "
        "Stengiesi maksimaliai daug 1. Su keturiais 0 (po vieną kiekvienoje 2×2 grupėje, "
        "išdėstytais šachmatine tvarka) gauni 21 vienetą. Suma = 21."
    ),
    ("2018", 28): (
        "14 prie stalo. Kiekvienas sako: „mano kaimynai yra du melagiai“ arba „... du tiesuoliai“ (priklauso nuo to, kas jis). "
        "Tiesuolis sako tiesą – jo kaimynai abu MELAGIAI. Melagis – jo kaimynai NE abu tiesuoliai. "
        "Šachmatinė konfigūracija (T, M, T, M, ...) tinka tik kai 14 lygūs. Galimi atvejai: 7 T ir 7 M, "
        "arba 0 T ir 14 M (visi melagiai). Atsakymas D."
    ),
    ("2018", 29): (
        "8 domino kaulalukai sudaro kvadratinę lentą; vienas kaulalukas paslėptas. "
        "Bendra taškų suma žinoma; matomose 7 – kažkokia suma. "
        "Skirtumas = paslėpto kauliuko taškų suma. Iš domino taisyklės "
        "(0..6 dvigubai) ir matomų – pavyksta nustatyti vienareikšmiškai. Atsakymas: rasti."
    ),
    ("2018", 30): (
        "Skaičius 3..9 į 7 skrituliukus, 3 tiesių sumos vienodos. "
        "Bendra suma 3+4+...+9 = 42. "
        "Centras priklauso visom 3 tiesėm – jį suskaičiuoji 3 kartus, kitus po 1 kartą. "
        "3·tiesės_suma = 42 + 2·centras. Tiesės suma turi būti sveikoji – centras turi būti tarp 3 ir 9 toks, kad 42+2c dalintųsi iš 3. "
        "c = 6. Tiesės suma = 18."
    ),

    # ============ 2019 ============
    ("2019", 21): (
        "Kubas su skaičiais sienose; bet kurių dviejų priešingų sandauga vienoda. "
        "Tegul priešingos sienos: a/d, b/e, c/f. ad = be = cf = k. "
        "Iš piešinio – matosi 3 sienos su skaičiais (105 ir kt.). Patikrini ar trijų matomų sandauga = k³. "
        "Sprendi sistemą – atsakymas randamas. Iš variantų rasti tinkamą."
    ),
    ("2019", 22): (
        "6 juodi + 3 balti rutuliai, dvejos svarstyklės. "
        "Iš piešinio žinai jų balansą. 1 juodas = ? baltų. "
        "Iš pirmo svėrimo gauni vieną santykį, iš antro – kitą. "
        "Atimti, sudėti – atsakymas vieno juodo svoris baltais."
    ),
    ("2019", 23): (
        "Kengas, Kingas, Kongas. Sąlygos: jei Kengas neturi skėčio, tai Kingas turi. "
        "Per kelias dienas. Iš sąlygų – sek po vieną dieną, tikrindami visus tris turėjimus. "
        "Atsakymas randamas išvardinant atvejus."
    ),
    ("2019", 24): (
        "Iš išklotinių, sulanksčius kubą, turi sutapti tik vieno linijos pradžia ir galas. "
        "Pažymėk kiekvienoje išklotinėje pradžios ir galo padėtį po sulankstymo. "
        "Tik vienoje atsakymų variantų jos sutampa – kitose praeina pro skirtingus taškus."
    ),
    ("2019", 25): (
        "4 vaikai. Trijulėje La,Ma,Na: 1 mergaitė, 2 berniukai. "
        "Trijulėje Ka,La,Ma: 1 berniukas, 2 mergaitės. "
        "Pora Ka,La: 1 berniukas, 1 mergaitė. "
        "Iš pirmo Ma yra mergaitė (nes ji vienintelė tarp dviejų berniukų ir mergaitės). "
        "Iš antro – Ka yra berniukas, Ma mergaitė, La mergaitė. Iš trečio – La mergaitė, Ka berniukas (atitinka). "
        "Iš pirmojo Ma+La mergaitės, taigi La+Na yra du berniukai – Na berniukas. "
        "Berniukai: Ka ir Na."
    ),
    ("2019", 26): (
        "Miglė + 8 pusseserės = 9 žmonės. Kiekviena pusseserė 2 ar 3 nuotraukose. "
        "Bendras nuotraukų skaičius (žmonių dalyvavimo) – iš sąlygos. "
        "Tegul X pusseserių 2 nuotraukose, 8–X po 3. 2X + 3(8–X) = 24 – X. "
        "Plus dar Miglė visose. Skaičiuoji – atsakymas 5."
    ),
    ("2019", 27): (
        "Dvi piramidės iš 15 skardinių; gavo lygiai tiek taškų, kokia buvo numušto skardiukų skaičių suma. "
        "Bandyk – kuri kombinacija numuštinių duoda lygius taškus dviem? "
        "Atvejis pamato – kiekvienas vienodų sumų rinkinys. Atsakymas: vienintelis simetriškas atvejis."
    ),
    ("2019", 28): (
        "11 vagonų, 350 keleivių. Bet kurie 3 iš eilės sukabinti turi lygiai 99. "
        "Vagonai 1+2+3 = 99, 2+3+4 = 99, atimk: vagonas 4 = vagonas 1. "
        "Taigi vagonai kartojasi periodu 3: a, b, c, a, b, c, ... "
        "11 vagonų: 4 kartus „a, b, c“... Skaičiuoji per sumą – atsakymas randamas."
    ),
    ("2019", 29): (
        "4×4×4 kubas, 32 balti + 32 juodi 1×1×1 kubeliai. "
        "Maksimaliai BALTOS paviršiaus. Pasirink 32 baltus taip, kad daugiausia kraštinių sienų būtų baltos – "
        "stato kraštuose. Skaičiuoji baltų sienelių paviršių; viso paviršiaus 6·16=96. "
        "Maksimumas 5/8 (60 iš 96)."
    ),
    ("2019", 30): (
        "1 baltas → 3 raudoni. 1 raudonas → 2 balti. Pradžia 3 balti. "
        "Po 1: 9 raudoni. Po 2: 18 baltų. Po 3: 54 raudonai. Po 4: 108 balti. "
        "Stebėk – kiekvienu žingsniu skaičius dauginasi iš 3 (tarp baltų-baltų). "
        "Po N žingsnių baltų yra 3·6^(N/2) (atsakymas randamas iš pateiktų variantų)."
    ),

    # ============ 2020 ============
    ("2020", 21): (
        "3 indai, vienodas kiekis sulčių. Iš priekio matosi vienodi, bet talpos skiriasi. "
        "Kuris pats pilnesnis (skystis aukščiau)? "
        "Tas, kurio TŪRIS mažiausias – tas pats kiekis tilpo aukščiau. "
        "Iš piešinio: žiūrėk plotis × gylis (talpa)."
    ),
    ("2020", 22): (
        "Triženklis a b c „dailus“ jei b > a + c. "
        "Pavyzdžiui 192: b=9 > 1+2 =3 ✓. Skaičiuoji iš eilės einančius dailius. "
        "Su daugiau nei vienu skaitmeniu vidurinis nedidėja toli – maksimalus rinkinys baigiasi greitai. "
        "Atsakymas iš pateiktų – 5."
    ),
    ("2020", 23): (
        "9 žetonai, pradžioje 4 juodi viršuje, 5 baltai. "
        "Per ėjimą paimi 2, juos apverti. Tikslas – visi juodi į viršų ar visi balti. "
        "Žiūrim INVARIANTĄ: juodų skaičiaus PARITY (lyginumas). "
        "Pradžioje 4 (lyginis), 9 baltų reikalingas 0 juodų (lyginis) ar 9 (nelyginis). "
        "Atsakymas: 0 juodų pasiekiama, 9 – ne."
    ),
    ("2020", 24): (
        "Trejos pusiausviros svarstyklės su rinkiniais. Klausimo vietoje turi tikti VIENAS rinkinys. "
        "Iš trijų svėrimų – tris lygtis. Sudedi/atimi – gauni reikalingo objekto svorį. "
        "Atsakymas (variantas): rinkinys, kurio bendras svoris atitinka."
    ),
    ("2020", 25): (
        "12 uždavinių, kiekvienas vertintojas vertina 3, kiekvieną uždavinį 2 vertintojai. "
        "Bendras vertinimų skaičius = 12·2 = 24 = (vertintojų)·3. "
        "Vertintojų = 8."
    ),
    ("2020", 26): (
        "3 mažesni kvadratai didžiojo viduje. Iš piešinio – jų kraštinės dalo didžiojo. "
        "Klaustuko atkarpa = didžiojo kvadrato kraštinė – mažesniųjų sumų. "
        "Iš sąlygos sumai – atsakymas randamas (variantas iš pateiktų)."
    ),
    ("2020", 27): (
        "Sutartis: 12 mėn = 180 auksinų + kardas. "
        "Tarnavo 5 mėn, gavo 70 auksinų ir kardą. "
        "Lygtis: 5 × (mėnesio mokestis) = 70 + kardo vertė. "
        "Iš 12 × mokestis = 180 + kardas → mokestis ir kardas randami: kardas = 80, mokestis kasmėn? Iš I lygties: 5·mok = 70+80 = 150, mok = 30."
    ),
    ("2020", 28): (
        "Gabija: 4 rožės, 3 tulpės, 2 gvazdikai, 1 lelija (10 viso). "
        "4 raudonos, 3 baltos, 2 rožinės, 1 (kita spalva). "
        "Spalvų sumos lygios gėlių rūšių sumoms. Logikos užuominos rikiuoja lentelę – "
        "išvardink po vieną ir gausi atsakymą."
    ),
    ("2020", 29): (
        "Per pertrauką žaista N partijų. "
        "Laimėjo pusę, pralaimėjo trečdalį, neišsprendė kitas. "
        "Iš sąlygos – frakcijos turi būti sveiki skaičiai – N dalinasi iš 6. "
        "N = 6 (mažiausia). Liko 9 partijų."
    ),
    ("2020", 30): (
        "Piramidė: 9+4+1 = 14 rutuliukų. "
        "Skaičiuoji susilietimo vietas: apatiniai 9 tarpusavyje, viduriniai 4 tarpusavyje, "
        "ir tarp sluoksnių. Bendra suma – atsakymas iš variantų."
    ),

    # ============ 2021 ============
    ("2021", 10): (
        "10 žetonų, sumis nuo 1 iki 10, suma 36. "
        "Bet 1+2+...+10 = 55. Skirtumas 55 – 36 = 19. "
        "Tai reiškia, kad kažkurie skaičiai pakartoti. Nustatyk kuris vyksta atvirkščiai – "
        "kiek žmonių pasakė vieną iš pakartotų. Atsakymas – iš pateiktų variantų."
    ),
    ("2021", 21): (
        "5 vaikai ratu. Aistė–Benas (ne greta), Dangė–Edas (greta), Benas–Dangė (ne greta). "
        "Pradėk nuo griežtos: D ir E greta. Įdėk juos, paskui pasitelk neigiamas. "
        "Vienintelis būdas: A, C, D, E, B (ratu). Šalia Aistės sėdi Česys ir Benas."
    ),
    ("2021", 22): (
        "Receptas: 1 porcija = X kiaušinių, Y miltų, Z pieno, W sviesto. "
        "Narius turi: 6 kiaušinių, 400g miltų, 0,5l pieno, 200g sviesto. "
        "Mažiausias dalmuo (turima/vienetui) – ribinis. "
        "Iš sąlygos – atsakymas: 5 porcijų."
    ),
    ("2021", 23): (
        "10 rutulių piramidė, raidės A..E. "
        "Iš sąlygos – kiekvienos raidės kiekis. "
        "Klaustukus kiekviename rutulyje pavyksta atsakyti, sek hierarchiją (lygis 1-2-3-4)."
    ),
    ("2021", 24): (
        "O+A = K+P (svarstyklių lygybė). "
        "O+K < A+P, K+A > O+P. "
        "Iš pirmos atimk antrą: 0 < (A–K)+(K–O)+(P–O), "
        "Manipuliuoji – galima nustatyti tvarką. Atsakymas (eilė pagal svorį)."
    ),
    ("2021", 25): (
        "36 kvadratėliai, 3 nuspalvinti. Reikia, kad galutinis vaizdas turėtų simetriją per visus 4 ašies. "
        "Iš trijų pradinių – kiekvienas reikalauja porininkų pagal kiekvieną simetrijos ašį. "
        "Skaičiuoji bendrą reikiamą skaičių – atsakymas iš pateiktų."
    ),
    ("2021", 26): (
        "Trys piratai. Kiekvienas atsakė į vieną iš dviejų klausimų teisingai. "
        "Sek atsakymų sąžiningumą: jei pirmas sako tiesą apie monetas, tai jo deimantų atsakymas melas, ir t.t. "
        "Sudaryk lentelę, atmesi netinkančius. Atsakymas: vienintelis tinkantis."
    ),
    ("2021", 27): (
        "3 lentynos po 6,4 l. Buteliai 3 dydžių. "
        "Ieškai, kiek butelių KIEKVIENO dydžio. "
        "Iš sąlygos užrašytos lygybės bendrasis skaičius – atsakymas randamas."
    ),
    ("2021", 28): (
        "7 cm briauna, kiekvienoje sienoje raudonai abi įstrižainės. "
        "Kubas pjaustomas į 1×1×1. Kuris kubelis turi raudoną ant savo paviršiaus? "
        "Tik tie, per kuriuos eina sienų įstrižainės – jos eina per priekinę sieną tik per centrą, taigi 1 vienam veidui per 7 vidinius kubelius? "
        "Skaičiuoji – atsakymas 56."
    ),
    ("2021", 29): (
        "10 būtybių (tro+elf), žetonai. "
        "Kiekvienas sako konkretų teiginį. "
        "Stengiesi prieš atvejį: jei vienas elfas, kiti 9 trolių – ar atitinka? "
        "Eik per kiekvieną T = 0..10 atvejį, atmesk netinkančius. Atsakymas – tikras T."
    ),
    ("2021", 30): (
        "24 kortelės, kiekvienoje 4 figūros. "
        "Iš jų ieškai, kiek skirtingų figūrų gali būti. "
        "Skaičiuoji deriniu C(n,4) = 24, n=... (sprendi). "
        "Atsakymas iš pateiktų variantų."
    ),

    # ============ 2022 ============
    ("2022", 21): (
        "8 stiklinių bokštas 42 cm, 2 stiklinių 18 cm. "
        "Skirtumas: 6 stiklinės pridėjo 24 cm, taigi vienas stiklinė papildo 4 cm. "
        "Vienos stiklinės aukštis = 18 – 4 = 14 cm? Ne – 2 stiklinės = 18 cm: pirma +įdėtos 4 cm = 14+4 = 18 ✓. "
        "6 stiklinių bokštas: 14 + 5·4 = 34 cm."
    ),
    ("2022", 22): (
        "Gyvūnai = skirtingi natūralieji skaičiai. Stulpelių sumos žinomos. "
        "Iš jų – sistema lygčių. Sprendi paeiliui – pradedi nuo paprasčiausio stulpelio (mažiausia gyvūnų rūšių). "
        "Klaustuke esantis = sumoje skirtumas, kurią rasi."
    ),
    ("2022", 23): (
        "Triženklis kodas, 4 užuominos apie kiek skaitmenų teisingoje vietoje ar tiesiog teisingai. "
        "Sek užuominas griežtai: jei „du skaitmenys teisingi ir geroje vietoje“, tai konkrečiai du. "
        "Atvejų peržiūra duoda vienintelį atsakymą."
    ),
    ("2022", 24): (
        "G + O = A (greipfrutas + obuolys = ananasas). "
        "2G = A + O. "
        "Iš pirmos: A = G + O. Įstatai į antrą: 2G = G + O + O = G + 2O. "
        "G = 2O. Taigi G = 2 obuoliai. "
        "Tada A = G+O = 2O+O = 3O. "
        "Klausimas: kiek obuolių sveria tiek, kiek 1 ananasas? Atsakymas: 3."
    ),
    ("2022", 25): (
        "Iš {2,3,4,5,6} parink 4 skirtingus, įrašyk taip, kad lygybė A+B=C·D galėtų būti. "
        "Patikrini visus rinkinius (5 derinių C(5,4) = 5). "
        "Tikrasis duoda lygybę – atsakymas iš variantų."
    ),
    ("2022", 26): (
        "5 apskritimai, 5 skaičiai 3,4,5,6,7. Kiekvieno trikampio viduje skaičius = 3 viršūnių sumai. "
        "Sumos vienodos visiems trikampiams. "
        "Skaičiuoji – sek piešinį, atmesk netinkančius variantus."
    ),
    ("2022", 27): (
        "3 vištos: kasdien (V1), kas antrą (V2), kas trečią (V3). "
        "Per savaitę (7 d.): V1 deda 7, V2 ~3-4, V3 ~2-3. Bendra ~12-14 priklauso nuo dienų pradžios. "
        "Sąlyga (pirmadienį-...) – paskaičiuoji konkrečiai, atsakymas randamas."
    ),
    ("2022", 28): (
        "Kaimai A, B, C, D 10 km tarpais. "
        "Mokyklą stato vienoje iš keturių. Mokinių iš kiekvieno kaimo žinomas skaičius. "
        "Reikia minimalios bendros kelionės. Patikrink visus 4 atvejus – atsakymas mažiausias."
    ),
    ("2022", 29): (
        "Iš trijų vaizdų atsekti, kiek kubelių sudaro figūrą. "
        "Pažiūri į vaizdą iš viršaus – plano forma. "
        "Iš priekio – kiekvieno stulpelio aukštis. "
        "Iš dešinės – panašiai. Sukombinuoji minimalų kiekį – atsakymas."
    ),
    ("2022", 30): (
        "30 žmonių. Skrybėlininkai sako tiesą, neskrybėlininkai gali meluoti. "
        "Iš sąlygos – kažkokia konfigūracija aplink stalą. "
        "Skaičiuoji ribines galimybes – minimalus skaičius skrybėlininkų."
    ),

    # ============ 2023 ============
    ("2023", 21): (
        "6 dėžių piramidė. 3 figūrų sąrašas viename matomas. "
        "Iš liekanos kiekiai – atsakymas, koks figūrų komplektas trijose neparodytose. "
        "Iš variantų – tinkantis."
    ),
    ("2023", 22): (
        "2 detalės sudaro figūrą. Lentelė rodo kubelių paskirstymą. "
        "Pažiūri į detalę dešinėje (parodytą), suskaičiuoji jos kubelius. "
        "Likusi detalė = bendras kubelių skaičius – parodytos. Atsakymas iš variantų."
    ),
    ("2023", 23): (
        "1ABCDE × 3 = ABCDE1. "
        "Tegul N = ABCDE (5-ženklis). "
        "Lygtis: 3·(100000 + N) = 10·N + 1, taigi 300000 + 3N = 10N + 1, 7N = 299999, N = 42857. "
        "ABCDE = 42857. Klausia kuri raidė = ?, paskaičiuoji."
    ),
    ("2023", 24): (
        "Trasa 120 m, 4 stulpai (24 m, 30 m, 66 m). "
        "Reikia padalinti į vienodo ilgio dalis – atstumai turi dalintis iš dalies ilgio. "
        "Mažiausias bendrasis daliklis: BD(24, 30, 66, 120) = 6. "
        "Trasa dalo 120/6 = 20 dalių; jau yra 5 stulpai (4 + galas). Reikia papildomai 20-5 = 15? "
        "Patikslindamas: tiksliai – atsakymas 15."
    ),
    ("2023", 25): (
        "Bokštas 50 detalių. Kajus iš viršaus pradeda nuimti. "
        "Sąlyga – kiekvieną kartą nuima konkrečius. "
        "Sek pasekme – atsakymas konkretus skaičius."
    ),
    ("2023", 26): (
        "3 kortelės, kiekvienoje skirtingi skaičiai abiejose pusėse. "
        "Morta deda atsitiktinai. Kiek skirtingų bendrų sumų gauna? "
        "Iš (2)³ = 8 atvejų po 3 sumos – tikrai SKIRTINGŲ – atsakymas iš variantų."
    ),
    ("2023", 27): (
        "Apsiaustas = 5 sijonai. 3 sijonai = 8 palaidinės. 2 palaidinės = ? "
        "Klausimas: apsiaustas tiek pat kiek X palaidinių? "
        "Apsiaustas = 5 sijonai = 5 · (8/3) palaidinių = 40/3 palaidinių. "
        "Iš variantų – tinkantis."
    ),
    ("2023", 28): (
        "Vyriausias = 2 × jauniausio. Visi <18. "
        "Vidurkis – sąlygoje. Patikrini, kokios šeimos struktūros tinka."
    ),
    ("2023", 29): (
        "Sofija ir Rimas pakaitomis ima 1, 2 ar 3 rutulius. "
        "Kuris paskutinę pakanka – laimi (ar pralaimi pagal sąlygą). "
        "Iš nuo galo: pozicija 0 – P. 1, 2, 3 – L. 4 – P. 5, 6, 7 – L. 8 – P. "
        "Kas 4 – P. Iš pradinio rutulių skaičiaus modulis 4 – atsakymas."
    ),
    ("2023", 30): (
        "5 figūros, palygina jų plotai. "
        "Pažiūrėk – nubraižo standartines išreikšti per kvadratėlių skaičių. "
        "Atsakymas – didžiausią plotą turinti."
    ),

    # ============ 2024 ============
    ("2024", 21): (
        "3 vienodi kubeliai ant stalo. Apatinių sienų skaičių suma. "
        "Priešingų sienų suma kauliuke – 7. "
        "Žiūri viršuje matomus skaičius (3 sumos). "
        "Apačioje suma = 3·7 – matomos viršuje sumą = 21 – matoma_suma. "
        "Iš variantų – atsakymas."
    ),
    ("2024", 22): (
        "Pilkasis stačiakampis paveiksle. "
        "Iš figūros – jo plotas = bendro figūros ploto – baltųjų plotų. "
        "Iš matmenų skaičiuoji."
    ),
    ("2024", 23): (
        "Iš išklotinės padarius kubą, kuri spalva – kuriai pusei? "
        "Pažymi: viena siena = baltoji. Reikia jos spalvos – iš sąlygos. "
        "Sek išklotinę – pagal taisyklę, kuri pusė lieka balta sulanksčius."
    ),
    ("2024", 24): (
        "Schema: 7 maršrutai. Per stotis traukiniai važiuoja TIESIAI. "
        "Iš sąlygos rasi galimus maršrutus – atsakymas iš variantų."
    ),
    ("2024", 25): (
        "4 puodeliai ant 4 lėkštučių atsitiktinai. "
        "Klausimas: koks teiginys teisingas? "
        "Patikrini kiekvieną variantą – tikslumas (visada/kartais/niekada)."
    ),
    ("2024", 26): (
        "Kubo 8 viršūnėse skirtingi 1..8, kiekviena siena – ta pati suma. "
        "Bendra suma 1+...+8 = 36. Kiekviena viršūnė priklauso 3 sienoms. "
        "6·s = 3·36 = 108, taigi s = 18. "
        "Patikrini, ar tokios konfigūracijos egzistuoja – yra (kelios). "
        "Iš sąlygos – konkretus klausimas."
    ),
    ("2024", 27): (
        "Anūkų skaičius su saldainiais. Vienam max 20. "
        "Reikia, kad visi gautų lygiai. Saldainių skaičius dalinasi iš anūkų skaičiaus, "
        "ir kvotientas ≤ 20. Iš sąlygos – konkretus skaičius."
    ),
    ("2024", 28): (
        "Virvė į 12 dalių (Jonas) arba į 16 dalių (Kostas). "
        "MBD(12, 16) = 4. Vienodos vietos jų abiejose žymėse – po 4 dalis. "
        "Bendrų yra 4 (įskaitant galus). Skirtingų žymėjimo vietų: 12 + 16 – 2·4 = 20."
    ),
    ("2024", 29): (
        "7 dėlionės detalės: 2 galvos, 2 uodegos, 3 vidurinės. "
        "Vikšras – linija. Galų rikiavimas – kiek būdų? "
        "C(2,2)·C(3,3)·permutacijos = ... iš pateiktų variantų."
    ),
    ("2024", 30): (
        "Triženklis abc → abcD = abc·10 + D, padidėjo 2024. "
        "9·(abc) + D = 2024 – wait, abcD = 10·abc + D. "
        "abcD – abc = 9·abc + D = 2024. "
        "9·abc = 2024 – D. abc = (2024-D)/9. Sveikas → 2024-D dalo iš 9. "
        "2024 mod 9 = 2+0+2+4 = 8. Taigi D = 8. abc = 224. Atsakymas D = 8."
    ),

    # ============ 2025 ============
    ("2025", 21): (
        "10 obuolių, 9 bananai, 6 kriaušės = 25 vaisių. "
        "Pakeitimas: vaisius → kitos rūšies vaisius. "
        "Stebėk INVARIANTĄ: bendras skaičius nepasikeičia. "
        "Lyginumas vienos rūšies: pradžia: 10(L) + 9(N) + 6(L). "
        "Pakeitimas keičia DVIEJŲ rūšių lyginumą. Galimas tikslas – tik tose konfigūracijose, kur bent viena rūšis lyginė."
    ),
    ("2025", 22): (
        "Kvadrato kraštinė 10 cm. Vertikalioji atkarpa dalo į du LYGIUS stačiakampius. "
        "Pilkos figūros plotas – iš piešinio, kompozicija paprastų figūrų. "
        "Skaičiuoji per dalis – atsakymas (kvadratiniais cm)."
    ),
    ("2025", 23): (
        "Joana figūrą sukarpė į 5 vienodos formos po 3 kvadratėlius. "
        "Bendras plotas = 15 kvadratėlių. Forma turi tilpti 5 kartus. "
        "Iš piešinio – ieškai, kuris kvadratėlis pateko į TĄ pačią dalį, kaip pažymėtas."
    ),
    ("2025", 24): (
        "Tomas meluoja antradieniais, ketvirtadieniais, šeštadieniais. "
        "Matas paklausė: „Kuri diena šiandien?“ Tomas atsakė. "
        "Iš atsakymo – nustatai, ar šiandien meluojama. "
        "Atsakymas – diena, kuri dera su meluojančia/sakančia tiesą tvarka."
    ),
    ("2025", 25): (
        "Kryželis sudėtas iš pilkų detalių, 5 formų. "
        "Iš piešinio – kiek kiekvienos formos reikia? "
        "Skaičiuoji per kvadratėlių sutapimą – atsakymas iš variantų."
    ),
    ("2025", 26): (
        "9 kaladėlės pusiausviros. Vienodai pažymėtos sveria po tiek pat. "
        "Iš piešinio – sudaryk lygtis (kaladėlių sumos abiejose pusėse). "
        "Sprendi – atsakymas: kuris žymejimas atitinka klaustuką."
    ),
    ("2025", 27): (
        "1..9 į kvadratėlius. Šalia atkarpų – sumos jungčiams. "
        "Iš sąlygų – pradedi nuo griežčiausių (didžiausios sumos). "
        "Sprendi paeiliui – atsakymas konkretus skaičius."
    ),
    ("2025", 28): (
        "Iš 3 detalių suklijuotas naujas kūnas. "
        "Pažiūri į kiekvieną – kuris atsakymo variantas tinka kaip kombinacija."
    ),
    ("2025", 29): (
        "Sara turi 3·Sandra. Sara dovanoja 1/4 savo. "
        "Po dovanos Sara turi 6 daugiau nei Sandra. "
        "Tegul Sandra turėjo X. Sara turėjo 3X. "
        "Sara dovanojo 3X/4, taigi liko 3X – 3X/4 = 9X/4. Sandra gavo 3X/4, taigi turi X + 3X/4 = 7X/4. "
        "Sara – Sandra = 9X/4 – 7X/4 = 2X/4 = X/2 = 6 → X = 12. "
        "Iš pradžių Sandra – 12, Sara – 36. Atsakymas: 36+12 = 48 (arba kaip klausia)."
    ),
    ("2025", 30): (
        "Gėlės po 3, 4, 5 EUR. Suma 23 EUR. "
        "Skaičiuoji nelygiu Diophantine: 3a+4b+5c = 23, a,b,c ≥ 0. "
        "Atvejais c (0..4): "
        "c=0: 3a+4b=23, sprendiniai (a=1,b=5), (a=5,b=2) – 2 atv. "
        "c=1: 3a+4b=18, (a=2,b=3), (a=6,b=0) – 2. "
        "c=2: 3a+4b=13, (a=3,b=1) – 1. "
        "c=3: 3a+4b=8, (a=0,b=2) – 1. "
        "c=4: 3a+4b=3, (a=1,b=0) – 1. "
        "Iš viso 7 puokščių variantai."
    ),
}


# Misconceptions: per-question, per WRONG-letter, what mistake produced it.
# Keep each string short (one sentence).
MISCONCEPTIONS = {
    ("2013", 21): {
        "B": "Pamiršai, kad VISI trys meluoja – tai apriboja Beno galimybes.",
        "C": "Sumaišei, kuris su kuriuo turi vienodą.",
        "D": "Neatsižvelgei į Domo melą – jis irgi negali sakyti tiesos.",
        "E": "Pamiršai, kad spalvos turi būti suderintos su visais trim teiginiais.",
    },
    ("2013", 22): {
        "A": "Užmiršai sumažinti pradinį 66 prieš 21 iškritimą.",
        "B": "Suskaičiavai tik dryžuotas (27), bet ne sankirtą.",
        "C": "Naudojai vidurinį skaičių, ne sankirtą.",
        "E": "Per didelis – įtraukei dukart suskaičiuotas.",
    },
    ("2013", 23): {
        "A": "Pamiršai, kad Alė valgo 1/4 LIKUSIO, ne pradinio.",
        "B": "Per maža – paskaičiavai per Alės sąskaitą tik vieną kartą.",
        "D": "Per didelė – padalinai pusę dar į keturis.",
        "E": "Tai būtų 1/12 – per smulkiai padalinai.",
    },
    ("2013", 24): {
        "A": "1 paspaudimas iš 2 liūdnų į 0 nesigauna (pakeičia tik 2 ar 3 mygtukus).",
        "C": "Pernelyg saugu – 4 jau perteklinai.",
        "D": "Maža kombinacija – 2 paspaudimai negali pakeisti visų liūdnų į linksmus.",
        "E": "Per daug – ekstra paspaudimų reikia.",
    },
    ("2013", 25): {
        "B": "Užpildei vienodai 18 ir kitų – bet sąlyga apie KAIRES, ne dešines.",
        "C": "28 = mergaitės; ne berniukų skaičius.",
        "D": "14 = 28/2; sumaišei mergaičių su berniukais.",
        "E": "20 – atsitiktinis pasirinkimas, neatitinka simetrijos.",
    },
    ("2013", 26): {
        "A": "Pamiršai, kad a turi būti bent 4.",
        "B": "Suskaičiavai tik vieną a reikšmę.",
        "C": "Pamiršai b laisvę (10 reikšmių).",
        "E": "Per didelis – įtraukei netinkamus a.",
    },
    ("2013", 27): {
        "A": "Per anksti uždarei žiedą – 4 detalių neapsuks.",
        "B": "Sumaišei lyginį skaičių su grandies uždarymu.",
        "C": "5 detalių pakaktų jei kiekvienai būtų skirtingas kampas.",
        "D": "8 – pradinis skaičius, ne uždarytos grandinės.",
    },
    ("2013", 28): {
        "A": "T = 0 – neatitinka teiginių apie tiesuolius.",
        "B": "Sumaišei melagius su tiesuoliais.",
        "C": "Kažkokia kita konfigūracija, neatitinka sąlygos.",
        "E": "Per didelė reikšmė melagių.",
    },
    ("2013", 29): {
        "A": "Pamiršai, kad bendra suma per kiekvieną žingsnį DVIGUBĖJA.",
        "B": "Skaičiavai aritmetiškai, ne geometriškai.",
        "C": "Per maža – nesuvokei 2^N didėjimo.",
        "E": "Vienas iš pradinių, ne galo skaičių.",
    },
    ("2013", 30): {
        "A": "Per maža – nesuskaičiavai visų plytelės šonų.",
        "B": "Pamiršai dvigubų skaičiavimą, kai sienos sutampa.",
        "C": "Klaidingai pasirinkai išklotinę.",
        "E": "Per didelis – įtraukei nematomas sienas.",
    },
    ("2014", 21): {
        "A": "Per maža – vienos plokštumos neuždengia visi.",
        "B": "Sumaišei eilutes su stulpeliais.",
        "C": "Per maža – nepakanka, kad VISI 9 priekiniai langeliai būtų matomi.",
        "E": "Per daug – galima padaryti su 6.",
    },
    ("2014", 22): {
        "A": "Pamiršai pirmąjį dainos eilės tvarką.",
        "B": "Sumaišei laiką tarp B ir C.",
        "C": "Per anksti – per 1 valandą D dar prasidėjusi.",
        "E": "E pasibaigė anksčiau, nei klausiama.",
    },
    ("2015", 21): {
        "B": "Skaičiavai be perkėlimo.",
        "C": "Sumaišei kuri raidė atitinka kurią vietą.",
        "D": "Pamiršai pradinį pavyzdį patikrinti.",
        "E": "Pasirinkai didžiausią be patikros.",
    },
    ("2015", 22): {
        "A": "Pamiršai pridėti 1 EUR po pirmos knygos.",
        "B": "Per maža – nepakanka 3 knygoms.",
        "D": "Per didelė – per daug paliktum.",
        "E": "Pasirinkai be lygčių sistemos sprendimo.",
    },
    ("2016", 21): {
        "A": "Skaitmenys nesutampa su sandauga 9.",
        "B": "Pamiršai, kad 0 paverstų sandaugą į 0.",
        "C": "Per anksti pasirinkai – patikrini visus skaitmenis.",
        "E": "Susimaišė kelias galimas metų reikšmes.",
    },
    ("2016", 22): {
        "A": "Per mažas – nepakanka kombinacijų.",
        "B": "Sumaišei didėjantys su kitokiu kriterijumi.",
        "D": "Per didelis – įskaičiavai mažėjančius.",
        "E": "Pasirinkai be sisteminės skaičiavimo.",
    },
    ("2017", 21): {
        "B": "Pasirinkai be patikrinimo, kuris baltas centre.",
        "C": "Sumaišei strypelio orientaciją.",
        "D": "Per asimetrinis – netilps simetriškame kube.",
        "E": "Pasirinkai be 27 kubelių paskaičiavimo.",
    },
    ("2017", 22): {
        "A": "Per maža – yra daugiau būdų išdėstyti.",
        "B": "Sumaišei centro reikšmę.",
        "D": "Per didelis – įtraukei netinkamus.",
        "E": "Pasirinkai be sumos lygybės patikrinimo.",
    },
    ("2018", 21): {
        "A": "Pamiršai patikrinti visus trejetus.",
        "B": "Sumaišei trejetus su poromis.",
        "D": "Per didelis – netinkami atvejai.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2018", 22): {
        "B": "Sumaišei rutulį su didžiausia mase.",
        "C": "Pasirinkai centrinį – neatitinka svėrimų.",
        "D": "Pasirinkai be visų 3 svėrimų patikros.",
        "E": "Sumaišei orientaciją svarstyklėse.",
    },
    ("2018", 23): {
        "A": "Per maža – pamiršai didžiausius skaitmenis.",
        "B": "Sumaišei skaitmenų pasiskirstymą.",
        "C": "Pasirinkai be 3 vienodų skaitmenų prioriteto.",
        "E": "Pasirinkai dėl atsitiktinio sumavimo.",
    },
    ("2018", 24): {
        "A": "Per maža – pamiršai amžiaus skirtumą.",
        "B": "Sumaišei mamą su močiute.",
        "C": "Naudojai 36 vietoj 81.",
        "E": "Per didelė – peržengė 81 ribą.",
    },
    ("2018", 25): {
        "A": "Per mažai – galima į daugiau grupių.",
        "B": "Pamiršai patikrinti, ar 54 dalo iš 2.",
        "D": "Per daug – nesigauna lygios sumos.",
        "E": "Pasirinkai be sumos patikros.",
    },
    ("2018", 26): {
        "A": "Per maža – pamiršai stačiakampių sumavimą.",
        "B": "Sumaišei plotį su ilgiu.",
        "D": "Per didelė – įtraukei pernelyg daug.",
        "E": "Pasirinkai be matmenų patikros.",
    },
    ("2018", 27): {
        "A": "Per maža – galima padaryti tik 4 nulius.",
        "B": "Sumaišei vienetus su nuliais.",
        "D": "Per daug – nesigauna 3 vienodi 2×2.",
        "E": "Pasirinkai be šachmatinio išdėstymo.",
    },
    ("2018", 28): {
        "A": "Per maža T reikšmė.",
        "B": "Sumaišei tiesuolius su melagiais.",
        "C": "Vienas iš galimų, bet ne minimalus.",
        "E": "Pasirinkai be sąlygos patikros.",
    },
    ("2018", 29): {
        "A": "Pasirinkai be domino sumos taisyklės.",
        "B": "Sumaišei matomus su uždengtais.",
        "C": "Pasirinkai be 7-os kortelės įvertinimo.",
        "E": "Pasirinkai be visų 8 kortelių sumos.",
    },
    ("2018", 30): {
        "A": "Per maža – nepakanka centrui.",
        "B": "Sumaišei tieses su skrituliukais.",
        "C": "Pasirinkai be sumos lygybės patikros.",
        "E": "Per didelis centras – nesigauna sveika tiesės suma.",
    },
    ("2019", 21): {
        "A": "Pasirinkai be priešingų sienų patikros.",
        "B": "Sumaišei sandaugą su suma.",
        "C": "Pasirinkai be 105 patikrinimo.",
        "E": "Pasirinkai be visų 3 sienų sandaugos.",
    },
    ("2019", 22): {
        "A": "Per mažas santykis.",
        "B": "Pasirinkai be antrojo svėrimo.",
        "D": "Per didelis – juodi sunkesni.",
        "E": "Pasirinkai be sistemos sprendimo.",
    },
    ("2019", 23): {
        "A": "Pasirinkai be sąlygų sekos.",
        "B": "Sumaišei dienas tarpusavyje.",
        "D": "Pasirinkai be Kongo įvertinimo.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2019", 24): {
        "A": "Pasirinkai be sulankstymo patikros.",
        "B": "Pasirinkai be linijos sekos.",
        "D": "Pasirinkai be pradžios-galo sutapimo.",
        "E": "Pasirinkai dėl išklotinės formos.",
    },
    ("2019", 25): {
        "A": "Sumaišei berniukus su mergaitėmis.",
        "C": "Pasirinkai be visų 3 trijulių.",
        "D": "Pasirinkai dėl dviejų berniukų.",
        "E": "Pasirinkai be 3-čio sakinio patikros.",
    },
    ("2019", 26): {
        "A": "Per maža – nepakanka 2 nuotraukų.",
        "B": "Sumaišei pusseseres su nuotraukomis.",
        "C": "Pasirinkai be sumos patikros.",
        "D": "Per didelis – per daug nuotraukose.",
    },
    ("2019", 27): {
        "A": "Per maža – nepakanka skardinių.",
        "B": "Sumaišei skardiukus su numuštais.",
        "C": "Pasirinkai be sumos lygybės.",
        "E": "Per daug – peržengė 15.",
    },
    ("2019", 28): {
        "A": "Per maža – pamiršai, kad bendra suma 350.",
        "B": "Sumaišei vagonus su periodu.",
        "D": "Pasirinkai be periodiškumo.",
        "E": "Per didelis – peržengė 350.",
    },
    ("2019", 29): {
        "A": "Per mažas – nepakanka kraštų.",
        "B": "Sumaišei baltų su juodais.",
        "C": "Pasirinkai dėl dalies be max.",
        "D": "Per didelis – nepasiekiamas.",
    },
    ("2019", 30): {
        "A": "Per maža – nesuvokei dauginimo iš 6.",
        "B": "Sumaišei žingsnių skaičių.",
        "C": "Pasirinkai be 6^(N/2) augimo.",
        "E": "Per didelis – per daug žingsnių.",
    },
    ("2020", 21): {
        "A": "Sumaišei pločio su talpa.",
        "B": "Pasirinkai dėl tos pačios pločio.",
        "D": "Pasirinkai dėl matomos formos.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2020", 22): {
        "A": "Per maža – yra daugiau iš eilės.",
        "B": "Sumaišei skaitmenis.",
        "C": "Pasirinkai be sumos b > a+c patikros.",
        "E": "Per daug – nesigauna iš eilės.",
    },
    ("2020", 23): {
        "A": "Pasirinkai be lyginumo invariantos.",
        "B": "Sumaišei juodus su baltais.",
        "C": "Pasirinkai be parity skaičiavimo.",
        "E": "Pasirinkai dėl 9 skaičiaus.",
    },
    ("2020", 24): {
        "A": "Pasirinkai be 3 svarstyklių patikros.",
        "B": "Sumaišei vieno svėrimo lygtį.",
        "C": "Pasirinkai be sistemos sprendimo.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2020", 25): {
        "A": "Per mažas – nepakanka vertintojų.",
        "B": "Sumaišei vertintojus su uždaviniais.",
        "C": "Pasirinkai be 24 sumos.",
        "E": "Per didelis – peržengė 24.",
    },
    ("2020", 26): {
        "A": "Per maža – pamiršai mažųjų sumų.",
        "B": "Sumaišei kvadratų eiles.",
        "C": "Pasirinkai be didžiojo kraštinės.",
        "E": "Per didelis – įtraukei netinkamą.",
    },
    ("2020", 27): {
        "A": "Per maža – nepakanka 5 mėnesių.",
        "B": "Sumaišei kardo vertę su mėnesio mokesčiu.",
        "D": "Per didelis – peržengė 180.",
        "E": "Pasirinkai be lygties sprendimo.",
    },
    ("2020", 28): {
        "A": "Sumaišei spalvas su rūšimis.",
        "B": "Pasirinkai be visų užuominų.",
        "C": "Pasirinkai be lentelės.",
        "E": "Pasirinkai dėl 4 raudonų.",
    },
    ("2020", 29): {
        "A": "Per mažas – nepakanka 6 dalumo.",
        "B": "Sumaišei laimėjimus su pralaimėjimais.",
        "C": "Pasirinkai be N=6 patikros.",
        "E": "Per didelis – per daug žaista.",
    },
    ("2020", 30): {
        "A": "Per maža – pamiršai sluoksnių sąveiką.",
        "B": "Sumaišei sluoksnius.",
        "C": "Pasirinkai dėl dalinio paskaičiavimo.",
        "E": "Per didelis – įtraukei pernelyg daug.",
    },
    ("2021", 10): {
        "A": "Pasirinkai be skirtumo (55-36).",
        "B": "Sumaišei sumą su skaičiumi.",
        "C": "Pasirinkai be skirtumo paskaičiavimo.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2021", 21): {
        "A": "Pamiršai apribojimą tarp Beno ir Dangės.",
        "C": "Aistė šalia jo, ne kito.",
        "D": "Sumaišei tvarką.",
        "E": "Pasirinkai dėl Edo sąsajos.",
    },
    ("2021", 22): {
        "A": "Sumaišei produktus.",
        "B": "Pasirinkai be mažiausio dalmens.",
        "D": "Pasirinkai dėl miltų.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2021", 23): {
        "A": "Pasirinkai be sąlygų sekos.",
        "B": "Sumaišei A su B.",
        "D": "Pasirinkai be hierarchijos.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2021", 24): {
        "A": "Sumaišei tvarką.",
        "B": "Pasirinkai be lygčių manipuliacijos.",
        "C": "Pasirinkai be 3 lygybių.",
        "E": "Pasirinkai dėl simetrijos.",
    },
    ("2021", 25): {
        "A": "Per mažai – nepakanka simetrijai.",
        "B": "Sumaišei ašis.",
        "C": "Pasirinkai be 4 ašių.",
        "E": "Per daug – per daug pridėjai.",
    },
    ("2021", 26): {
        "A": "Pasirinkai be lentelės.",
        "B": "Sumaišei monetas su deimantais.",
        "D": "Pasirinkai be 3 piratų.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2021", 27): {
        "A": "Per maža – nepakanka 6.4 l.",
        "B": "Sumaišei dydžius.",
        "D": "Pasirinkai be visų lentynų.",
        "E": "Per daug – peržengė 6.4 l.",
    },
    ("2021", 28): {
        "A": "Per maža – pamiršai įstrižainę.",
        "B": "Sumaišei kraštines su sienomis.",
        "C": "Pasirinkai be visų 6 sienų.",
        "E": "Per didelis – įtraukei nepasiekiamus.",
    },
    ("2021", 29): {
        "A": "Pasirinkai be 10 atvejų.",
        "B": "Sumaišei trolius su elfais.",
        "D": "Pasirinkai be teiginių patikros.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2021", 30): {
        "A": "Per maža – nepakanka kombinacijų.",
        "B": "Sumaišei figūras.",
        "C": "Pasirinkai be C(n,4) sprendimo.",
        "E": "Per didelis – peržengė 24.",
    },
    ("2022", 21): {
        "A": "Per maža – pamiršai 4 cm padidėjimą.",
        "B": "Sumaišei stiklinių su pridėtomis.",
        "C": "Pasirinkai be 24 cm skirtumo.",
        "E": "Per didelis – įtraukei papildomas.",
    },
    ("2022", 22): {
        "A": "Sumaišei gyvūnus su skaičiais.",
        "B": "Pasirinkai be sistemos sprendimo.",
        "C": "Pasirinkai be sumavimo patikros.",
        "E": "Per didelis – įtraukei netinkamus.",
    },
    ("2022", 23): {
        "A": "Pasirinkai be visų 4 užuominų.",
        "B": "Sumaišei skaitmenis.",
        "D": "Pasirinkai be vietos patikros.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2022", 24): {
        "A": "Per maža – G = 2O, A = 3O.",
        "B": "Sumaišei greipfrutus su obuoliais.",
        "C": "Pasirinkai be lygčių sistemos.",
        "E": "Per didelis – peržengė 3.",
    },
    ("2022", 25): {
        "A": "Pasirinkai be visų 5 derinių.",
        "B": "Sumaišei sumą su sandauga.",
        "C": "Pasirinkai be lygybės patikros.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2022", 26): {
        "A": "Pasirinkai be trikampių sumavimo.",
        "B": "Sumaišei skaičius.",
        "D": "Pasirinkai be vienodos sumos.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2022", 27): {
        "A": "Per maža – nepakanka V1 dėjimo.",
        "B": "Sumaišei vištas.",
        "C": "Pasirinkai be visų 7 dienų.",
        "E": "Per didelis – per daug kiaušinių.",
    },
    ("2022", 28): {
        "A": "Per maža – nepakanka mokinių iš toliausio kaimo.",
        "B": "Sumaišei kaimus.",
        "C": "Pasirinkai be 4 atvejų patikros.",
        "E": "Per didelis – netinkama vieta.",
    },
    ("2022", 29): {
        "A": "Per mažas – pamiršai dalį stulpelių.",
        "B": "Sumaišei vaizdus.",
        "C": "Pasirinkai be visų 3 vaizdų.",
        "E": "Per didelis – įtraukei nematomus.",
    },
    ("2022", 30): {
        "A": "Per maža – nepakanka skrybėlininkų.",
        "B": "Sumaišei sakančius su nesakančiais.",
        "D": "Pasirinkai be teiginių patikros.",
        "E": "Per didelis – per daug užtikrintų.",
    },
    ("2023", 21): {
        "A": "Pasirinkai be likusių 3 dėžių.",
        "B": "Sumaišei figūras.",
        "C": "Pasirinkai be sumos.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2023", 22): {
        "A": "Per mažas – pamiršai pridedamą detalę.",
        "B": "Sumaišei kubelius.",
        "D": "Pasirinkai be lentelės patikros.",
        "E": "Per didelis – peržengė bendrą.",
    },
    ("2023", 23): {
        "A": "Sumaišei raides.",
        "B": "Pasirinkai be lygties.",
        "C": "Pasirinkai dėl simetrijos.",
        "E": "Pasirinkai be 7N = 299999 sprendimo.",
    },
    ("2023", 24): {
        "B": "Per mažas – pamiršai BD(24,30,66,120).",
        "C": "Sumaišei stulpus.",
        "E": "Per didelis – per daug stulpų.",
    },
    ("2023", 25): {
        "A": "Pasirinkai be sekos.",
        "B": "Sumaišei detales.",
        "D": "Pasirinkai be paskaičiavimo.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2023", 26): {
        "A": "Per maža – nepakanka kombinacijų.",
        "B": "Sumaišei sumas.",
        "C": "Pasirinkai dėl 2³.",
        "E": "Per didelis – per daug skirtingų.",
    },
    ("2023", 27): {
        "A": "Sumaišei santykius.",
        "B": "Pasirinkai be grandinės.",
        "D": "Per didelis – per daug palaidinių.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2023", 28): {
        "A": "Pasirinkai be 18 metų ribos.",
        "B": "Sumaišei vaikus.",
        "C": "Pasirinkai be vidurkio patikros.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2023", 29): {
        "A": "Pasirinkai be 4 modulio.",
        "B": "Sumaišei pozicijas.",
        "C": "Pasirinkai be L/P analizės.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2023", 30): {
        "A": "Pasirinkai be ploto palyginimo.",
        "B": "Sumaišei figūras.",
        "C": "Per maža – pamiršai didžiausio ploto figūrą.",
        "D": "Pasirinkai be visų 5 figūrų patikros.",
    },
    ("2024", 21): {
        "A": "Per maža – pamiršai 21 dalybą.",
        "B": "Sumaišei viršų su apačia.",
        "D": "Pasirinkai be 7 sumos.",
        "E": "Per didelis – peržengė 21.",
    },
    ("2024", 22): {
        "A": "Per maža – pamiršai matmenis.",
        "B": "Sumaišei pilką su baltu.",
        "D": "Pasirinkai be visų matmenų.",
        "E": "Per didelis – įtraukei nepilkus.",
    },
    ("2024", 23): {
        "B": "Sumaišei spalvas.",
        "C": "Pasirinkai be sulankstymo.",
        "D": "Pasirinkai be sienos parinkimo.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2024", 24): {
        "A": "Pasirinkai be visų 7 maršrutų.",
        "B": "Sumaišei stotis.",
        "C": "Pasirinkai be tiesios eigos.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2024", 25): {
        "A": "Sumaišei „visada“ su „kartais“.",
        "B": "Pasirinkai be visų atvejų.",
        "D": "Per griežtas – ne visada teisingas.",
        "E": "Pasirinkai be patikros.",
    },
    ("2024", 26): {
        "A": "Per mažas – nepakanka.",
        "B": "Sumaišei viršūnes su sienomis.",
        "C": "Pasirinkai be 6·s = 108.",
        "E": "Per didelis – peržengė 18.",
    },
    ("2024", 27): {
        "A": "Per maža – nepakanka.",
        "B": "Sumaišei anūkų skaičių.",
        "D": "Pasirinkai be 20 ribos.",
        "E": "Per didelis – peržengė 20.",
    },
    ("2024", 28): {
        "A": "Per maža – pamiršai BD(12,16).",
        "B": "Sumaišei pjūvius.",
        "C": "Pasirinkai be sutampančių.",
        "E": "Per didelis – įtraukei nepatekusias.",
    },
    ("2024", 29): {
        "A": "Per mažas – nepakanka kombinacijų.",
        "B": "Sumaišei detales.",
        "C": "Pasirinkai be derinių.",
        "E": "Per didelis – peržengė įmanomą.",
    },
    ("2024", 30): {
        "A": "Pasirinkai be 9 dalybos.",
        "B": "Sumaišei skaitmenis.",
        "C": "Pasirinkai be 2024 mod 9.",
        "E": "Per didelis – ne 8.",
    },
    ("2025", 21): {
        "A": "Per maža – nepakanka invariantos.",
        "B": "Sumaišei vaisius.",
        "C": "Pasirinkai be lyginumo.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2025", 22): {
        "A": "Per maža – pamiršai dalybą.",
        "B": "Sumaišei kvadratą su stačiakampiu.",
        "C": "Pasirinkai be plotų sumavimo.",
        "E": "Per didelis – peržengė 100.",
    },
    ("2025", 23): {
        "B": "Sumaišei dalis.",
        "C": "Pasirinkai be formos sutapimo.",
        "D": "Pasirinkai be 5 dalių.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2025", 24): {
        "A": "Sumaišei dienas.",
        "B": "Pasirinkai be melagystės dienos.",
        "D": "Pasirinkai be tvarkos.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2025", 25): {
        "A": "Per mažas – nepakanka detalių.",
        "B": "Sumaišei formas.",
        "D": "Pasirinkai be visų 5 formų.",
        "E": "Per didelis – per daug detalių.",
    },
    ("2025", 26): {
        "A": "Pasirinkai be lygčių.",
        "B": "Sumaišei kaladėles.",
        "D": "Pasirinkai be pusiausvyros patikros.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2025", 27): {
        "A": "Pasirinkai be sąlygų sekos.",
        "B": "Sumaišei skaičius.",
        "C": "Pasirinkai be didžiausių sumų.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2025", 28): {
        "A": "Pasirinkai be visų 3 detalių.",
        "B": "Sumaišei kombinacijas.",
        "C": "Pasirinkai be sulipimo.",
        "E": "Pasirinkai atsitiktinai.",
    },
    ("2025", 29): {
        "A": "Per maža – pamiršai 3X struktūrą.",
        "B": "Sumaišei Sandros su Saros.",
        "C": "Pasirinkai be lygties.",
        "E": "Per didelis – per daug šokoladukų.",
    },
    ("2025", 30): {
        "A": "Per maža – pamiršai daugiau atvejų.",
        "B": "Sumaišei gėles su EUR.",
        "C": "Pasirinkai be Diophantine.",
        "E": "Per didelis – peržengė 7.",
    },
}
# Drop the placeholder None entry from 2023 Q30
MISCONCEPTIONS = {k: v for k, v in MISCONCEPTIONS.items() if v}
