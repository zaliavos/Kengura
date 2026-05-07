# Kengūros Treniruoklio asmenybė — kid-facing voice & style guide

This file describes *how* the app talks to its user. Pair it with `CLAUDE.md`,
which describes *what* the app does and why. If you (human or AI) are about
to write any string the kid will read — a hint, a methodology blurb, a kid
solution, a button label, a results-page line — read this first.

## Who the user is

A Lithuanian 5–6 grader (~11–12 years old) preparing for the Bičiulis tier
of the Kengūros konkursas. Smart enough to be doing contest math at all,
not yet patient enough to read a wall of text. Probably has a parent
hovering somewhere — but the parent has their own view (`/parent`); the
kid view is *for the kid*.

The kid is here voluntarily 90 % of the time. Every condescending word
costs trust. Every wasted sentence costs the next click.

## Voice

- **Lithuanian, always.** Even mathematical idioms (`carry`, `mod`, `parity`)
  get a Lithuanian gloss in parentheses on first use; the English term is
  fine after. Code identifiers (`MECHANIC_HINTS`, `mech`, `band`) stay
  English — the kid never sees them.
- **2nd person singular, informal: „tu", „tavo", „pažymėk", „bandyk".**
  Never the polite plural „jūs" / „pažymėkite". Never the impersonal
  „reikia pažymėti". The kid is being addressed personally, not lectured.
- **Imperative, not subjunctive.** „Užrašyk lentelę." Not „Galėtum užrašyti
  lentelę." Not „Vertėtų pamėginti užrašyti lentelę."
- **Short sentences.** A hint that runs past two sentences is a hint that
  isn't a hint anymore — it's a solution leak. Methodology blurbs get three
  parts (`trick`, `keyStep`, `pitfalls`); each is one tight paragraph.
- **No emoji in body copy.** Buttons may carry one functional symbol
  (👁 Tėvams, ⏱ Kontrolinis) for visual anchoring. Nowhere else.
- **No exclamation marks except where genuinely warranted.** "Šaunu!" after
  a single right answer is exactly the kind of fake gamification that makes
  contest training feel like a phone game. The kid notices.

## Tone

- **Respect Benjamin-grade work.** A 5-point question hides an invariant or
  a parity argument or a clever bijection — that is real math, not "tricky
  arithmetic." The voice never implies otherwise. Don't soften 5-pointers
  with "sunkutis uždavinukas" diminutives. Don't pad them with encouragement
  before the kid has even tried.
- **Strategy first, answer never (in hints).** A hint says *what kind of
  problem this is* and *which move to make first*. It does not name the
  answer, the answer letter, or the final number. The 4-tier ladder
  (`notice → ask → suggest → tell`) makes this concrete: only tier 4 (the
  full per-question solution, shown after submission) is allowed to give
  away the punchline.
- **Name the misstep, not the kid.** When a wrong option has a known
  misconception, surface it: „Pamiršai, kad Alė valgo 1/4 *likusio*, ne
  pradinio." Never „Tu suklydai" / „Neteisingai pagalvojai." The error is
  in the move, not in the kid.
- **Calibrated praise.** Praise the *process move* the kid actually made —
  „Gerai pasirinkai pradėti nuo paskutinio skaitmens" — not the outcome
  („Teisingai!"). The confidence-calibration system already flags blanket
  overconfidence; the copy should not feed it.
- **No empty filler.** „Tikiuosi, gerai sekasi!", „Nepasiduok!", „Tu gali!"
  — out. Replace with something concrete or remove entirely.

## What the app *does*, in one breath each

These are voice anchors — the mental model the copy should reinforce
every time it appears.

- **Methodology blurb** = the unified frame. „Melagių uždaviniai *visada*
  reikalauja prielaidos + prieštaravimo paieškos." Hand-written, short,
  authoritative. The blurb's job is to make the kid recognise the
  *category* the next time they see one.
- **Užuomina (hint)** = a nudge along the right path, never the path
  itself. Three reveal levels before submission, full solution after.
- **Sprendimas (solution)** = post-submit. `solutionKid` (3 short
  paragraphs: pastebėjimas → veiksmas → patvirtinimas, 2nd person) is
  preferred over the auto-extracted official `solution` whenever present.
- **Praktikuotis šio tipo** = same mechanic, same difficulty band. The
  pedagogical contract is: if I just struggled with a 5-point parity
  problem, the next thing I see is *also* 5-point and *also* parity-
  shaped. Never a 3-point arithmetic warm-up dressed up as practice.
- **Kontrolinis (contest sim)** = strict mode. No hints, no playlists, no
  confidence picker, no "practice similar." 75 minutes, hard timer.
  −25 % penalty per wrong answer. The voice in this mode is *minimal*
  and *neutral* — the kid is performing, not learning.

## What the app never does

- **Never mentions other Kangaroo tiers.** No Mažylis, no Kadetas, no
  Junioras. The app is Bičiulis-only and the copy reflects that — no
  "kai būsi vyresnis", no "Mažyliams būna lengviau", no comparisons.
- **Never recommends a wrong-band practice.** If no generator produces
  Benjamin-grade work for a mechanic, the recommendation copy says so
  explicitly („Tikslaus generatoriaus dar nėra — tai kito tipo to paties
  sudėtingumo uždavinys") rather than silently downgrading.
- **Never gamifies for gamification's sake.** No streaks-as-pressure
  („Tu prarasi 7 dienų streaką!"), no XP, no levels, no badges. Mastery
  marks (`store.masteredMech`) and the spaced-repetition queue are
  pedagogical tools, not score-chase mechanics — the copy treats them
  that way.
- **Never apologises for the math being hard.** It's supposed to be hard.
  That is the entire point of the 5-point band.
- **Never blames the kid for a hint use, a confidence miscall, or a
  wrong answer.** The parent dashboard surfaces patterns; the kid view
  surfaces the *next move*.
- **Never uses placeholder copy in shipped strings.** „Lorem ipsum",
  „TODO: better wording", „[insert hint here]" — these have to go before
  the file is saved, not before the next release.

## When you write new copy

Run it through this checklist:

1. Is it in the kid's voice — 2nd person singular, imperative, short?
2. Does it name the *strategy* without naming the *answer*?
3. Would an 11-year-old read all of it, or skim past sentence two?
4. Does it assume the kid is capable, or does it pre-apologise for the
   difficulty?
5. If it's a hint: is it strictly less informative than the next tier?
6. If it's praise: is it praising a specific move, not a generic „šaunu"?
7. If it mentions a mechanic: is the mechanic name the same as the one
   in `MECHANIC_METHODOLOGY` so the kid sees consistent vocabulary?

If any answer is "no", rewrite before you ship.
