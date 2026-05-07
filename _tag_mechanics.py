"""Tag every archive question with a `mechanic` (and optional `mechanic2`)
field. Hand-tagged 5-point questions take precedence; everything else uses
keyword/regex heuristics on prompt text.

Mechanic vocabulary (Benjamin-relevant):

  Number / arithmetic
    arith-compute       bare computation, brackets, order of ops
    digit-puzzle        cryptarithm, find digit X, AB×N=BA, digit substitution
    digit-properties    digit sum, product, palindrome, digits sorted
    place-value         append/prepend digit, reverse digits, "padidėjo"
    divisibility        div by N, parity of result, primes/composites
    mixture-fraction    fraction-of-fraction, "pusę pinigų ir 2 €"

  Logic
    truth-tellers       liars/truth puzzles, melagiai, tiesuoliai
    logic-clues         clue-based "who did X" / who is in which trijulė
    casework            small-case enumeration, find max/min by trying
    invariant           parity/coloring/conserved quantity arguments
    state-game          turn-taking games, who wins, terminal state
    iteration           apply operation N times → final / fixed state

  Counting / combinatorial
    counting-ways       how-many-ways, factorials, combinations
    partition           split N items into groups w/ constraint, packs

  Geometry
    area-decomp         shaded area by piece counting / equal pieces
    area-compute        direct area / perimeter formula
    geometry-misc       lengths, angles, intersections, drawings
    tiling              fitting pieces, dominoes, cuts of board
    symmetry            mirror, rotation, reflection
    cube-net            net folds into cube, find which net
    cube-color          painted small cubes / opposite faces / dice
    projection          top/front/side views, view-from

  Word problems
    age-relations       ages now/then/future
    rate-time           speed, work, recipe scaling
    weighing            balance scales, compare weights
    arrangement         seating, race order, queue
    multistep-money     prices, change, multistep cost
    clock               clock readings, hand overlaps, time arithmetic
    calendar            weekday/date arithmetic
    sequence-pattern    arithmetic seq, periodic, telescoping, next-in-pattern
"""
import json, re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_JSON = os.path.join(HERE, 'kengura-archive.json')
ARCHIVE_JS   = os.path.join(HERE, 'kengura-archive.js')

# ---------------------------------------------------------------------------
# Hand-tagged 5-point questions. (year, qnum) -> [mechanic, ...]
# First mechanic is primary; second is secondary if relevant.
# ---------------------------------------------------------------------------
HAND_5PT = {
    ("2013", 21): ["truth-tellers"],
    ("2013", 22): ["casework"],          # inclusion-exclusion-ish on cats
    ("2013", 23): ["mixture-fraction"],
    ("2013", 24): ["invariant"],         # button parities
    ("2013", 25): ["invariant"],         # boys/girls handholds
    ("2013", 26): ["digit-puzzle"],
    ("2013", 27): ["tiling", "geometry-misc"],
    ("2013", 28): ["truth-tellers"],
    ("2013", 29): ["iteration", "invariant"],
    ("2013", 30): ["cube-net"],

    ("2014", 21): ["projection"],
    ("2014", 22): ["sequence-pattern"],   # cycle period

    ("2015", 21): ["digit-puzzle"],
    ("2015", 22): ["mixture-fraction"],

    ("2016", 21): ["casework", "digit-properties"],
    ("2016", 22): ["counting-ways", "casework"],

    ("2017", 21): ["cube-color"],
    ("2017", 22): ["casework"],

    ("2018", 21): ["counting-ways", "partition"],
    ("2018", 22): ["weighing"],
    ("2018", 23): ["digit-puzzle"],
    ("2018", 24): ["age-relations"],
    ("2018", 25): ["partition"],
    ("2018", 26): ["tiling"],
    ("2018", 27): ["casework"],          # 5x5 with 2x2 constraints
    ("2018", 28): ["truth-tellers"],
    ("2018", 29): ["tiling"],            # dominoes
    ("2018", 30): ["casework"],          # magic-line

    ("2019", 21): ["cube-color"],
    ("2019", 22): ["weighing"],
    ("2019", 23): ["logic-clues"],
    ("2019", 24): ["cube-net"],
    ("2019", 25): ["logic-clues"],
    ("2019", 26): ["partition", "counting-ways"],
    ("2019", 27): ["casework"],
    ("2019", 28): ["partition", "casework"],
    ("2019", 29): ["cube-color"],        # surface area painted fraction
    ("2019", 30): ["state-game", "iteration"],

    ("2020", 21): ["mixture-fraction"],
    ("2020", 22): ["casework"],          # max consecutive "dailūs"
    ("2020", 23): ["invariant"],         # token flips parity
    ("2020", 24): ["weighing"],
    ("2020", 25): ["counting-ways"],     # graph/hypergraph counting
    ("2020", 26): ["area-decomp"],
    ("2020", 27): ["rate-time"],
    ("2020", 28): ["logic-clues", "casework"],
    ("2020", 29): ["casework"],
    ("2020", 30): ["casework"],          # piramidė taisyklės

    ("2021", 10): ["casework"],          # special 5pt at Q10
    ("2021", 21): ["logic-clues", "arrangement"],
    ("2021", 22): ["rate-time"],
    ("2021", 23): ["logic-clues"],
    ("2021", 24): ["weighing"],
    ("2021", 25): ["invariant", "area-decomp"],
    ("2021", 26): ["truth-tellers"],
    ("2021", 27): ["casework", "partition"],
    ("2021", 28): ["cube-color"],        # diagonals on cube
    ("2021", 29): ["truth-tellers"],
    ("2021", 30): ["counting-ways"],

    ("2022", 21): ["sequence-pattern", "rate-time"],   # stacking-of-cups arithmetic seq
    ("2022", 22): ["digit-puzzle"],
    ("2022", 23): ["casework", "logic-clues"],
    ("2022", 24): ["weighing"],
    ("2022", 25): ["casework"],
    ("2022", 26): ["casework"],
    ("2022", 27): ["casework", "calendar"],
    ("2022", 28): ["casework"],          # extremal kelias
    ("2022", 29): ["projection"],
    ("2022", 30): ["truth-tellers"],

    ("2023", 21): ["logic-clues"],
    ("2023", 22): ["projection", "cube-color"],
    ("2023", 23): ["digit-puzzle"],
    ("2023", 24): ["divisibility", "partition"],   # 120 m, equal pieces → factors
    ("2023", 25): ["iteration"],
    ("2023", 26): ["counting-ways"],
    ("2023", 27): ["weighing"],          # ratio chain — same shape as balance
    ("2023", 28): ["age-relations"],
    ("2023", 29): ["state-game"],
    ("2023", 30): ["area-decomp", "area-compute"],

    ("2024", 21): ["cube-color"],        # opposite faces on dice
    ("2024", 22): ["area-decomp"],
    ("2024", 23): ["cube-net"],
    ("2024", 24): ["counting-ways", "logic-clues"],
    ("2024", 25): ["counting-ways"],
    ("2024", 26): ["cube-color"],
    ("2024", 27): ["divisibility"],      # daugiausiai po 20 → divisors
    ("2024", 28): ["divisibility"],      # virvė LCM/GCD
    ("2024", 29): ["counting-ways"],
    ("2024", 30): ["digit-puzzle", "place-value"],

    ("2025", 21): ["invariant"],         # parities of fruit conversions
    ("2025", 22): ["area-decomp"],
    ("2025", 23): ["tiling"],
    ("2025", 24): ["truth-tellers"],
    ("2025", 25): ["tiling"],
    ("2025", 26): ["weighing"],
    ("2025", 27): ["casework"],
    ("2025", 28): ["cube-net"],
    ("2025", 29): ["mixture-fraction"],
    ("2025", 30): ["counting-ways", "casework"],
}


# ---------------------------------------------------------------------------
# Keyword rules for 3- and 4-point questions. Earlier rules win.
# Each rule: (mechanic, [keyword_or_regex, ...])
# ---------------------------------------------------------------------------
KEYWORD_RULES = [
    # very specific rules first
    ("clock",            [r"laikrod", r"valandinė rodyklė", r"minutinė rodyklė", r"veidrodyje matome laikrod"]),
    ("calendar",         [r"savaitės dieno", r"savaitės d\.", r"pirmadien", r"savait", r"mėnesi[oų]", r"liepos", r"rugpj", r"kalend"]),
    ("age-relations",    [r"\bamži", r"metų\b.+(jaunes|vyres|gimė)", r"sūnui.+metai", r"yra .+ metai.+po"]),
    ("rate-time",        [r"\bgreit", r"km/h", r"per valand", r"sekund.+per", r"minu.+per", r"recept", r"ridena", r"ridenant", r"trunka.+minu", r"trunka.+sek"]),
    ("weighing",         [r"svarstykl", r"sveria", r"sveriantis", r"pusiausvyr", r"pusiausvir"]),
    ("truth-tellers",    [r"melag", r"tieso", r"tiesa.+sako", r"sako.+tiesą", r"meluo"]),
    ("digit-puzzle",     [r"raid[ėeę].+skaitm", r"skirting.+skaitm.+lyg", r"skaitmen.+atitinka", r"vieno.+raid.+ skaitmen"]),
    ("digit-properties", [r"skaitmen.+suma", r"skaitmen.+sandauga", r"palindrom", r"skaitmen.+didžiausi", r"skaitmen.+mažiausi"]),
    ("place-value",      [r"prirašė.+skaitmen", r"prijung.+skaitmen", r"atvirkš.+tvark", r"sukeisti vietomis", r"didėja.+vienetai", r"padidėjo \d+ vienet"]),
    ("divisibility",     [r"dalijasi iš", r"dalijasi su liekana", r"liekan", r"pirmin", r"\bpirminis", r"\bne pirminis", r"daliklių", r"kartot"]),
    ("mixture-fraction", [r"\bpus[eęė] +(?:savo|likusi|li[eki])", r"pus[eęė] litr", r"trečdal", r"ketvirtad.+likus", r"% van", r"procent.+van"]),
    ("cube-net",         [r"išklotin.+kub", r"kub.+išklotin", r"sulenk.+kub", r"sulanksti.+kub"]),
    ("cube-color",       [r"\bkubeli.+nudažy", r"\bkubeli.+spalv", r"\bkubeli.+sien", r"kauliuk.+priešing", r"kauliuk.+sien"]),
    ("projection",       [r"iš viršaus", r"iš priekio", r"iš šono", r"iš dešinės", r"vaizdas iš", r"projekcij"]),
    ("symmetry",         [r"veidrod", r"atspindys", r"simetrij"]),
    ("tiling",           [r"domin", r"plytel.+sudėt", r"sukarp.+vienod", r"susklij.+vienod", r"plyt.+klijuoj", r"\bdetal[eę]s.+sudėt"]),
    ("area-decomp",      [r"užtušu", r"pilkos.+plot", r"plotas.+kvadrat", r"plotas.+stačiakam", r"plot.+rombo", r"figūr.+sudaryta"]),
    ("area-compute",     [r"figūr.+plot", r"\bplotas\b", r"\bperimet"]),
    ("counting-ways",    [r"\bkeli.+būd", r"\bkeliais būd", r"galima.+pasi", r"\bkomb", r"derini", r"\bišrik"]),
    ("partition",        [r"pakuot", r"\bkrūveles po", r"\bgrupes", r"padalink.+lygi", r"sudėl.+lygi", r"vienodos sumo"]),
    ("invariant",        [r"paspaud.+pasikei", r"perkel.+vis.+ vien", r"keičia.+priešing"]),
    ("state-game",       [r"\bžaidim", r"laimi tas", r"laimi.+kuris", r"prarado", r"strategij"]),
    ("iteration",        [r"\bkartoja", r"vis dar", r"po.+ėjim", r"po.+kart"]),
    ("logic-clues",      [r"\b(Adas|Benas|Domas|Gilė|Petras|Ąžuolas|Rugilė|Kenga|Riukas|Adelė|Barbora|Karolis|Diana|Ernestas|Felicija|Janina|Aistė|Tomas|Matas|Tautė|Sara|Sandra|Rūta|Mėta|Žilabarzdis|Sofija|Rimas)\b.+\b(Adas|Benas|Domas|Gilė|Petras|Ąžuolas|Rugilė|Kenga|Riukas|Adomas|Berta|Domas)\b"]),
    ("arrangement",      [r"susė.+ratu", r"sėdi ratu", r"eilėje", r"eilė.+vaiku", r"lenktyni"]),
    ("multistep-money",  [r"\beur", r"litai", r"\bcent", r"sumokė", r"kainuoj", r"grąž", r"\bkain"]),
    ("sequence-pattern", [r"\bsek", r"\beilė", r"toliau.+sek", r"kitas narys", r"\baritmetin"]),
    ("arith-compute",    [r"\bapskaičiuok", r"\b\d+ \+ \d+", r"\b\d+ \- \d+", r"\b\d+ ?× ?\d+", r"\b\d+ ?· ?\d+", r"= ?\?"]),
    ("casework",         [r"\bdaugiausia", r"\bmažiausia", r"didžiausi.+gali", r"mažiausi.+gali"]),
    ("geometry-misc",    [r"trikamp", r"kvadrat", r"stačiakamp", r"daugiakamp", r"apskritim", r"skritul", r"kamp.+laip", r"kamp.+lyg"]),
]


def auto_tag(prompt: str):
    """Return a single primary mechanic tag from keyword rules, or
    'arith-compute' as a last-resort default for prompts that look like
    pure computation."""
    p = prompt.lower()
    for mech, kws in KEYWORD_RULES:
        for kw in kws:
            if re.search(kw, p):
                return mech
    # last-resort fallback
    if re.search(r"\d", p):
        return "arith-compute"
    return "casework"


def main():
    with open(ARCHIVE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    n_hand = 0
    n_auto = 0
    by_mech = {}
    for y in data["archive"]:
        yr = y["year"]
        for q in y["questions"]:
            key = (yr, q["num"])
            if key in HAND_5PT:
                mechs = HAND_5PT[key]
                q["mechanic"] = mechs[0]
                if len(mechs) > 1:
                    q["mechanic2"] = mechs[1]
                else:
                    q.pop("mechanic2", None)
                n_hand += 1
            else:
                q["mechanic"] = auto_tag(q["prompt"])
                q.pop("mechanic2", None)
                n_auto += 1
            by_mech[q["mechanic"]] = by_mech.get(q["mechanic"], 0) + 1

    # write back
    with open(ARCHIVE_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(ARCHIVE_JS, "w", encoding="utf-8") as f:
        f.write("window.KENGURA_ARCHIVE = ")
        json.dump(data, f, ensure_ascii=False)
        f.write(";\n")

    print(f"Hand-tagged: {n_hand}")
    print(f"Auto-tagged: {n_auto}")
    print(f"\nMechanic distribution:")
    for m, c in sorted(by_mech.items(), key=lambda x: -x[1]):
        print(f"  {m:>20} : {c}")

    # also show 5-point distribution by mechanic
    print(f"\n5-point distribution:")
    bm5 = {}
    for y in data["archive"]:
        for q in y["questions"]:
            if q.get("points") == 5:
                bm5[q["mechanic"]] = bm5.get(q["mechanic"], 0) + 1
    for m, c in sorted(bm5.items(), key=lambda x: -x[1]):
        print(f"  {m:>20} : {c}")


if __name__ == "__main__":
    main()
