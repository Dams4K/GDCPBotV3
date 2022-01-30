
def xp_to_level(xp_calc: str, xp: int) -> int:
    level = 0
    xp_needed = eval(xp_calc.format(l=level))
    while xp_needed <= xp:
        level += 1
        xp -= xp_needed
        xp_needed = eval(xp_calc.format(l=level))

    return level

def level_to_xp(xp_calc: str, level: int) -> int:
    xp = 0
    for l in range(level):
        xp += eval(xp_calc.format(l=l))
    return xp