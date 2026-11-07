"""Exact authoring helpers for reviewed loot packs; no network access or runtime rolls."""
from fractions import Fraction
from math import lcm

HERBS = (("Grimy guam leaf",32),("Grimy marrentill",24),("Grimy tarromin",18),
         ("Grimy harralander",14),("Grimy ranarr weed",11),("Grimy irit leaf",8),
         ("Grimy avantoe",6),("Grimy kwuarm",5),("Grimy cadantine",4),
         ("Grimy lantadyme",3),("Grimy dwarf weed",3))

def gem_table(rate, talisman="Nature talisman"):
    """Members/no wealth/surface/pre-Legends: mega-rare slot becomes Nature talisman."""
    if talisman not in ('Nature talisman','Chaos talisman'): raise ValueError('Unsupported talisman policy')
    return [(dict(item=name, quantity=quantity), Fraction(rate)*weight/128)
            for name,weight,quantity in (("Nothing",63,1),("Uncut sapphire",32,1),
            ("Uncut emerald",16,1),("Uncut ruby",8,1),(talisman,4,1),
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
    if denominator>0xFFFFFFFFFFFFFFFF: raise ValueError("Loot denominator exceeds runtime uint64")
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

GENERAL_SEED_GROUPS = (
 (485,1008,LOW_LEVEL_SEEDS),
 (728,1000,(("Barley seed",4,229),("Hammerstone seed",3,228),("Asgarnian seed",3,172),
            ("Jute seed",2,171),("Yanillian seed",2,114),("Krandorian seed",2,57),("Wildblood seed",1,29))),
 (850,1000,(("Marigold seed",1,376),("Nasturtium seed",1,249),("Rosemary seed",1,161),("Woad seed",1,119),("Limpwurt seed",1,95))),
 (947,1000,(("Redberry seed",1,400),("Cadavaberry seed",1,280),("Dwellberry seed",1,200),("Jangerberry seed",1,80),("Whiteberry seed",1,29),("Poison ivy seed",1,11))),
 (995,1000,(("Guam seed",1,320),("Marrentill seed",1,218),("Tarromin seed",1,149),("Harralander seed",1,101),
            ("Ranarr seed",1,69),("Toadflax seed",1,47),("Irit seed",1,32),("Avantoe seed",1,22),("Kwuarm seed",1,15),
            ("Snapdragon seed",1,10),("Cadantine seed",1,7),("Lantadyme seed",1,5),("Dwarf weed seed",1,3),("Torstol seed",1,2))),
 (99999,1100,(("Mushroom spore",1,500),("Belladonna seed",1,300),("Cactus seed",1,200),("Potato cactus seed",1,100))))

def general_seed_table(rate, combat_level):
    """Exact tier selection from the Wiki module, without rounded displayed denominators."""
    if type(combat_level) is not int or not 1 <= combat_level <= 255:
        raise ValueError("Invalid general-seed combat level")
    size=combat_level*10;previous=0;rows=[]
    for threshold,denominator,seeds in GENERAL_SEED_GROUPS:
        width=min(threshold,size)-previous
        if width>0:
            rows.extend((dict(item=name,quantity=count),Fraction(rate)*width*weight/(size*denominator))
                        for name,count,weight in seeds)
        if threshold>=size:break
        previous=threshold
    return rows

def rare_seed_table(rate):
    seeds=(("Toadflax seed",216),("Irit seed",148),("Belladonna seed",143),("Poison ivy seed",103),
       ("Avantoe seed",101),("Cactus seed",96),("Potato cactus seed",70),("Kwuarm seed",69),
       ("Snapdragon seed",46),("Cadantine seed",32),("Lantadyme seed",23),("Snape grass seed",20),
       ("Dwarf weed seed",14),("Torstol seed",9))
    return [(dict(item=name,quantity=3 if name=="Snape grass seed" else 1),Fraction(rate)*weight/1090) for name,weight in seeds]


def uncommon_seed_table(rate):
    # The Wiki lists 1046/1048; the unlisted two slots are empty, not renormalized.
    return [(dict(item=name,quantity=1),Fraction(rate)*weight/1048)
            for name,weight in UNCOMMON_SEEDS] + [(dict(item='Nothing',quantity=1),Fraction(rate)*2/1048)]


def rare_table(rate, gem_rate=0, talisman="Nature talisman"):
    """Native RDT: its direct mega branch is not quest-gated; embedded gem branch is pre-Legends."""
    rate=Fraction(rate)
    rows=[(dict(item=name,quantity=q),rate*w/128) for name,q,w in (
      ("Coins",3000,21),("Loop half of key",1,20),("Tooth half of key",1,20),
      ("Runite bar",1,5),("Nature rune",67,3),("Rune 2h sword",1,3),
      ("Rune battleaxe",1,3),("Law rune",45,2),("Death rune",45,2),
      ("Steel arrow",150,2),("Rune arrow",42,2),("Adamant javelin",20,2),
      ("Rune sq shield",1,2),("Dragonstone",1,2),("Silver ore",100,2),
      ("Rune kiteshield",1,1),("Dragon med helm",1,1))]
    rows += gem_table(rate*20/128 + Fraction(gem_rate), talisman)
    rows += [(dict(item=name,quantity=1),rate*15*weight/(128*128)) for name,weight in
             (("Nothing",113),("Rune spear",8),("Shield left half",4),("Dragon spear",3))]
    return rows
