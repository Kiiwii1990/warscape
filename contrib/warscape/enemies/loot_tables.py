"""Exact authoring helpers for reviewed loot packs; no network access or runtime rolls."""
from fractions import Fraction
from math import lcm

HERBS = (("Grimy guam leaf",32),("Grimy marrentill",24),("Grimy tarromin",18),
         ("Grimy harralander",14),("Grimy ranarr weed",11),("Grimy irit leaf",8),
         ("Grimy avantoe",6),("Grimy kwuarm",5),("Grimy cadantine",4),
         ("Grimy lantadyme",3),("Grimy dwarf weed",3))

def gem_table(rate):
    """Members/no wealth/surface/pre-Legends: mega-rare slot becomes Nature talisman."""
    return [(dict(item=name, quantity=quantity), Fraction(rate)*weight/128)
            for name,weight,quantity in (("Nothing",63,1),("Uncut sapphire",32,1),
            ("Uncut emerald",16,1),("Uncut ruby",8,1),("Nature talisman",4,1),
            ("Uncut diamond",2,1),("Rune javelin",1,5),("Loop half of key",1,1),
            ("Tooth half of key",1,1))]

def herb_table(rate):
    return [(dict(item=name, quantity=1), Fraction(rate)*weight/128) for name,weight in HERBS]

def independent_bonus(rows, bonus, probability):
    """Compose an independent bonus with a complete main roll, preserving both marginals."""
    p=Fraction(probability)
    if not 0 < p < 1: raise ValueError("Invalid bonus probability")
    result=[]
    for drop, chance in rows:
        result.append((dict(drop), Fraction(chance)*(1-p)))
        paired=dict(drop)
        paired['additional'] = drop.get('additional', []) + [dict(bonus)]
        result.append((paired, Fraction(chance)*p))
    return result

def compile_weights(rows):
    rows=[(dict(drop),Fraction(chance)) for drop,chance in rows]
    if not rows or any(chance<=0 for _,chance in rows) or sum(c for _,c in rows)!=1:
        raise ValueError("Loot probabilities must be positive and sum to one")
    denominator=lcm(*(chance.denominator for _,chance in rows))
    if denominator>0xFFFFFFFF: raise ValueError("Loot denominator exceeds runtime uint32")
    return [dict(drop,weight=int(chance*denominator)) for drop,chance in rows],denominator

# Reviewed factual weights from Module:GeneralSeedDropLines and Template:UncommonSeedDropLines.
LOW_LEVEL_SEEDS = (("Potato seed",4,368),("Onion seed",4,276),("Cabbage seed",4,184),
                   ("Tomato seed",3,92),("Sweetcorn seed",3,46),("Strawberry seed",2,23),
                   ("Watermelon seed",2,11),("Snape grass seed",2,8))
UNCOMMON_SEEDS = (("Limpwurt seed",137),("Strawberry seed",131),("Marrentill seed",125),
 ("Jangerberry seed",92),("Tarromin seed",85),("Wildblood seed",83),("Watermelon seed",63),
 ("Harralander seed",56),("Snape grass seed",40),("Ranarr seed",39),("Whiteberry seed",34),
 ("Mushroom spore",29),("Toadflax seed",27),("Belladonna seed",18),("Irit seed",18),
 ("Poison ivy seed",13),("Avantoe seed",12),("Cactus seed",12),("Kwuarm seed",9),
 ("Potato cactus seed",8),("Snapdragon seed",5),("Cadantine seed",4),("Lantadyme seed",3),
 ("Dwarf weed seed",2),("Torstol seed",1))

def general_seed_table(rate, combat_level):
    """Reviewed first tier only: integer combat levels 1-48 never cross the 485 threshold."""
    if type(combat_level) is not int or not 1 <= combat_level <= 48:
        raise ValueError("Higher general-seed tiers need a reviewed extension")
    return [(dict(item=name,quantity=count),Fraction(rate)*weight/1008)
            for name,count,weight in LOW_LEVEL_SEEDS]

def uncommon_seed_table(rate):
    # The Wiki lists 1046/1048; the unlisted two slots are empty, not renormalized.
    return [(dict(item=name,quantity=1),Fraction(rate)*weight/1048)
            for name,weight in UNCOMMON_SEEDS] + [(dict(item='Nothing',quantity=1),Fraction(rate)*2/1048)]
