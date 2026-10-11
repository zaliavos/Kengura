"""Trick-category (mechanic) corrections from the 2026-10-11 review of the
149 re-banded 5-point questions: each agent read the figure and the
solution and retagged the question when the stored tag (from the old
keyword tagger) named the wrong trick. Applied by running this file."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
MECHANIC = {
    "2000-21": "divisibility",   # was counting-ways
    "2000-23": "iteration",   # was geometry-misc
    "2000-25": "mixture-fraction",   # was arith-compute
    "2000-26": "logic-clues",   # was arith-compute
    "2000-28": "weighing",   # was arith-compute
    "2000-29": "geometry-misc",   # was arith-compute
    "2001-26": "digit-puzzle",   # was digit-properties
    "2001-28": "area-decomp",   # was area-compute
    "2001-30": "place-value",   # was digit-properties
    "2002-24": "rate-time",   # was arith-compute
    "2002-25": "casework",   # was arith-compute
    "2002-26": "partition",   # was multistep-money
    "2002-30": "counting-ways",   # was partition
    "2003-21": "cube-net",   # was geometry-misc
    "2003-22": "tiling",   # was geometry-misc
    "2003-23": "sequence-pattern",   # was casework
    "2003-24": "tiling",   # was area-decomp
    "2003-28": "digit-puzzle",   # was digit-properties
    "2004-22": "divisibility",   # was arith-compute
    "2004-26": "sequence-pattern",   # was geometry-misc
    "2004-28": "divisibility",   # was casework
    "2005-30": "logic-clues",   # was casework
    "2007-22": "place-value",   # was projection
    "2007-27": "area-decomp",   # was geometry-misc
    "2007-30": "digit-puzzle",   # was arith-compute
    "2008-21": "digit-puzzle",   # was casework
    "2008-22": "logic-clues",   # was casework
    "2008-23": "invariant",   # was casework
    "2008-24": "geometry-misc",   # was casework
    "2008-25": "projection",   # was arith-compute
    "2008-26": "logic-clues",   # was arith-compute
    "2008-27": "area-compute",   # was arith-compute
    "2009-27": "counting-ways",   # was tiling
    "2009-28": "iteration",   # was arith-compute
    "2009-30": "casework",   # was area-decomp
    "2010-22": "counting-ways",   # was casework
    "2010-23": "iteration",   # was clock
    "2010-26": "casework",   # was area-decomp
    "2010-27": "symmetry",   # was casework
    "2010-28": "sequence-pattern",   # was arith-compute
    "2011-21": "divisibility",   # was arith-compute
    "2011-22": "casework",   # was arith-compute
    "2011-24": "truth-tellers",   # was arith-compute
    "2011-25": "tiling",   # was area-decomp
    "2011-27": "counting-ways",   # was casework
    "2012-21": "mixture-fraction",   # was arith-compute
    "2012-23": "arith-compute",   # was age-relations
    "2012-24": "divisibility",   # was arith-compute
    "2012-25": "arrangement",   # was arith-compute
    "2012-27": "logic-clues",   # was arith-compute
    "2012-28": "geometry-misc",   # was iteration
    "2012-29": "digit-puzzle",   # was arith-compute
    "2014-23": "casework",   # was arith-compute
    "2014-24": "counting-ways",   # was arith-compute
    "2014-28": "casework",   # was arith-compute
    "2014-30": "partition",   # was casework
    "2015-23": "casework",   # was arith-compute
    "2015-24": "divisibility",   # was arith-compute
    "2015-28": "counting-ways",   # was arith-compute
    "2016-23": "tiling",   # was arith-compute
    "2016-24": "arith-compute",   # was geometry-misc
    "2016-25": "tiling",   # was casework
    "2016-27": "arith-compute",   # was geometry-misc
    "2016-28": "digit-puzzle",   # was arith-compute
    "2016-29": "divisibility",   # was casework
    "2017-27": "logic-clues",   # was arith-compute
    "2017-30": "invariant",   # was casework
}
if __name__ == "__main__":
    J = os.path.join(HERE, "kengura-archive.json")
    data = json.load(open(J, encoding="utf-8"))
    for y in data["archive"]:
        for q in y["questions"]:
            m = MECHANIC.get(f"{y['year']}-{q['num']}")
            if m: q["mechanic"] = m
    json.dump(data, open(J, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    subprocess.run([sys.executable, os.path.join(HERE, "_regen_js.py")], cwd=HERE, check=True)
    print("retagged", len(MECHANIC))
