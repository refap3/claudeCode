"""
puzzles.py - Library of built-in Sudoku puzzles for the Sudoku tutor app.

Each puzzle is stored as a list of 9 strings of 9 characters (0 = empty cell).

Tier definitions (human-strategy difficulty):
  Tier 1: Full House, Naked Single, Hidden Single only
  Tier 2: Naked/Hidden Pairs/Triples, Pointing Pairs, Box-Line Reduction
  Tier 3: X-Wing, Swordfish, Y-Wing, XYZ-Wing, Simple Coloring
  Tier 4: Unique Rectangle, W-Wing, Skyscraper, 2-String Kite, BUG+1
"""

from __future__ import annotations


def _rows(flat: str) -> list[str]:
    """Convert a flat 81-char string into a list of 9 strings of length 9."""
    assert len(flat) == 81, f"Expected 81 chars, got {len(flat)}"
    return [flat[i * 9:(i + 1) * 9] for i in range(9)]


# ---------------------------------------------------------------------------
# PUZZLES list  –  each entry: {name, tier, rows}
# rows: list of 9 strings of 9 chars (0 = empty)
# ---------------------------------------------------------------------------

PUZZLES: list[dict] = [

    # -----------------------------------------------------------------------
    # TIER 1  –  Full House / Naked Single / Hidden Single
    # -----------------------------------------------------------------------

    {
        "name": "Tier 1 – Classic Easy #1",
        "tier": 1,
        "rows": _rows(
            "003020600"
            "900305001"
            "001806400"
            "008102900"
            "700000008"
            "006708200"
            "002609500"
            "800203009"
            "005010300"
        ),
    },
    {
        "name": "Tier 1 – Classic Easy #2",
        "tier": 1,
        "rows": _rows(
            "200080300"
            "060070084"
            "030500209"
            "000105408"
            "000000000"
            "402706000"
            "301007040"
            "720040060"
            "004010003"
        ),
    },
    {
        "name": "Tier 1 – Classic Easy #3",
        "tier": 1,
        "rows": _rows(
            "000000907"
            "000420180"
            "000705026"
            "100904000"
            "050000040"
            "000507009"
            "920108000"
            "034059000"
            "507000000"
        ),
    },
    {
        "name": "Tier 1 – Easy Beginner #4",
        "tier": 1,
        "rows": _rows(
            "800930007"
            "000076090"
            "370004060"
            "198000025"
            "020000030"
            "450000781"
            "080300014"
            "040750000"
            "500019003"
        ),
    },
    {
        "name": "Tier 1 – Easy Beginner #5",
        "tier": 1,
        "rows": _rows(
            "020608000"
            "580009700"
            "000040000"
            "370000500"
            "600000004"
            "008000013"
            "000020000"
            "009800036"
            "000306090"
        ),
    },
    {
        "name": "Tier 1 – Easy Beginner #6",
        "tier": 1,
        "rows": _rows(
            "530070000"
            "600195000"
            "098000060"
            "800060003"
            "400803001"
            "700020006"
            "060000280"
            "000419005"
            "000080079"
        ),
    },
    {
        "name": "Tier 1 – Easy Beginner #7",
        "tier": 1,
        "rows": _rows(
            "096040001"
            "000600730"
            "804070006"
            "030080070"
            "600000008"
            "070060020"
            "200050403"
            "051004000"
            "400010580"
        ),
    },

    # -----------------------------------------------------------------------
    # TIER 2  –  Naked/Hidden Pairs/Triples, Pointing Pairs, Box-Line
    # -----------------------------------------------------------------------

    {
        "name": "Tier 2 – Moderate #1",
        "tier": 2,
        "rows": _rows(
            "010020300"
            "004005060"
            "070000054"
            "900000020"
            "060010090"
            "050000007"
            "340000080"
            "090700400"
            "008060030"
        ),
    },
    {
        "name": "Tier 2 – Moderate #2",
        "tier": 2,
        "rows": _rows(
            "040100050"
            "107003960"
            "520008000"
            "000000017"
            "000906800"
            "803050620"
            "090060543"
            "600080700"
            "250097100"
        ),
    },
    {
        "name": "Tier 2 – Moderate #3",
        "tier": 2,
        "rows": _rows(
            "600120384"
            "008459072"
            "000006005"
            "000264030"
            "070080006"
            "940003000"
            "310000050"
            "089700000"
            "502000190"
        ),
    },
    {
        "name": "Tier 2 – Moderate #4 (Pointing Pairs focus)",
        "tier": 2,
        "rows": _rows(
            "000030086"
            "000020040"
            "340000900"
            "700600000"
            "060080030"
            "000003007"
            "003000024"
            "010060000"
            "850090000"
        ),
    },
    {
        "name": "Tier 2 – Moderate #5 (Naked Pairs)",
        "tier": 2,
        "rows": _rows(
            "100489006"
            "720000080"
            "080700025"
            "000200030"
            "940030058"
            "050004000"
            "360008090"
            "010000037"
            "200794001"
        ),
    },
    {
        "name": "Tier 2 – Moderate #6 (Hidden Pairs)",
        "tier": 2,
        "rows": _rows(
            "000000000"
            "903060050"
            "068050930"
            "006190000"
            "715000603"
            "000047100"
            "037080460"
            "080030709"
            "000000000"
        ),
    },
    {
        "name": "Tier 2 – Moderate #7 (Box-Line)",
        "tier": 2,
        "rows": _rows(
            "090000070"
            "405030001"
            "007040568"
            "080000090"
            "300964002"
            "070000080"
            "839070500"
            "100020306"
            "020000040"
        ),
    },

    # -----------------------------------------------------------------------
    # TIER 3  –  X-Wing, Swordfish, Y-Wing, XYZ-Wing, Simple Coloring
    # -----------------------------------------------------------------------

    {
        "name": "Tier 3 – Hard #1 (X-Wing)",
        "tier": 3,
        "rows": _rows(
            "000600400"
            "700003600"
            "000091080"
            "000000060"
            "025010340"
            "000000010"
            "900007000"
            "008539070"
            "042000100"
        ),
    },
    {
        "name": "Tier 3 – Hard #2 (Swordfish)",
        "tier": 3,
        "rows": _rows(
            "000000000"
            "000003085"
            "001020000"
            "000507000"
            "004600200"
            "700090100"
            "090000006"
            "000800007"
            "005730040"
        ),
    },
    {
        "name": "Tier 3 – Hard #3 (Y-Wing)",
        "tier": 3,
        "rows": _rows(
            "100007090"
            "030020008"
            "009600500"
            "005300900"
            "010080002"
            "600004000"
            "300000010"
            "040000007"
            "007000300"
        ),
    },
    {
        "name": "Tier 3 – Hard #4 (XYZ-Wing)",
        "tier": 3,
        "rows": _rows(
            "000003017"
            "000100400"
            "500000000"
            "040060000"
            "600080004"
            "000010050"
            "000000900"
            "009007000"
            "420300000"
        ),
    },
    {
        "name": "Tier 3 – Hard #5 (Simple Coloring)",
        "tier": 3,
        "rows": _rows(
            "093004006"
            "006003100"
            "710600000"
            "000900700"
            "100070003"
            "007006000"
            "000008051"
            "008300200"
            "200100830"
        ),
    },
    {
        "name": "Tier 3 – Hard #6 (X-Wing / Swordfish)",
        "tier": 3,
        "rows": _rows(
            "200000600"
            "050200000"
            "000076510"
            "000000700"
            "800050003"
            "007000000"
            "095780000"
            "000003040"
            "003000001"
        ),
    },
    {
        "name": "Tier 3 – Hard #7 (Y-Wing chains)",
        "tier": 3,
        "rows": _rows(
            "000080702"
            "060035000"
            "070000008"
            "000600900"
            "038070520"
            "007002000"
            "400000060"
            "000940080"
            "603020000"
        ),
    },

    # -----------------------------------------------------------------------
    # TIER 4  –  Unique Rectangle, W-Wing, Skyscraper, 2-String Kite, BUG+1
    # -----------------------------------------------------------------------

    {
        "name": "Tier 4 – Expert #1 (Arto Inkala 2006)",
        "tier": 4,
        "rows": _rows(
            "003008000"
            "010030000"
            "000004700"
            "070060008"
            "000000023"
            "000900600"
            "500300000"
            "000080091"
            "000700040"
        ),
    },
    {
        "name": "Tier 4 – Expert #2 (Unique Rectangle)",
        "tier": 4,
        "rows": _rows(
            "000700000"
            "100000000"
            "000430200"
            "000000006"
            "000509000"
            "000000418"
            "000081000"
            "002000050"
            "040000300"
        ),
    },
    {
        "name": "Tier 4 – Expert #3 (Skyscraper)",
        "tier": 4,
        "rows": _rows(
            "400000805"
            "030000000"
            "000700000"
            "020000060"
            "000080400"
            "000010000"
            "000603070"
            "500200000"
            "104000000"
        ),
    },
    {
        "name": "Tier 4 – Expert #4 (W-Wing)",
        "tier": 4,
        "rows": _rows(
            "052000060"
            "000900007"
            "004002100"
            "080006290"
            "000000000"
            "017300040"
            "003500800"
            "600007000"
            "090000410"
        ),
    },
    {
        "name": "Tier 4 – Expert #5 (2-String Kite)",
        "tier": 4,
        "rows": _rows(
            "000004028"
            "600000000"
            "030600000"
            "200010700"
            "070000030"
            "004050009"
            "000005060"
            "000000001"
            "840200000"
        ),
    },
    {
        "name": "Tier 4 – Expert #6 (BUG+1 / Hardest)",
        "tier": 4,
        "rows": _rows(
            "800000000"
            "003600000"
            "070090200"
            "060005300"
            "004010070"
            "200400090"
            "500070006"
            "000000419"
            "000080052"
        ),
    },
    {
        "name": "Tier 4 – Expert #7 (Unique Rect + Skyscraper)",
        "tier": 4,
        "rows": _rows(
            "000006000"
            "009050700"
            "600900010"
            "008000031"
            "040000080"
            "290000400"
            "030007006"
            "007080900"
            "000300000"
        ),
    },

]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_puzzles_by_tier(tier: int) -> list[dict]:
    """Return all puzzles for the given tier number."""
    return [p for p in PUZZLES if p["tier"] == tier]


def get_all_tiers() -> list[int]:
    """Return a sorted list of all tier numbers present in PUZZLES."""
    return sorted(set(p["tier"] for p in PUZZLES))


# ---------------------------------------------------------------------------
# Quick sanity check when run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Total puzzles: {len(PUZZLES)}")
    for tier in get_all_tiers():
        puzzles = get_puzzles_by_tier(tier)
        print(f"  Tier {tier}: {len(puzzles)} puzzles")
        for p in puzzles:
            flat = "".join(p["rows"])
            given = sum(1 for c in flat if c != "0")
            assert len(flat) == 81, f"Wrong length for {p['name']}"
            print(f"    {p['name']}  ({given} givens)")
