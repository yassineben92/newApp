from typing import List, Dict, Any, Optional

class Champion:
    def __init__(self,
                 id: str,
                 key: str,
                 name: str,
                 title: str,
                 blurb: str,
                 info: Dict[str, float], # Typically numbers like attack, defense, magic, difficulty
                 image: Dict[str, Any], # e.g., full, sprite, group, x, y, w, h
                 tags: List[str],
                 partype: str,
                 stats: Dict[str, float], # e.g., hp, hpperlevel, mp, etc.
                 spells: List[Dict[str, Any]], # List of spell dictionaries
                 passive: Dict[str, Any] # Passive ability dictionary
                ):
        self.id = id
        self.key = key
        self.name = name
        self.title = title
        self.blurb = blurb
        self.info = info
        self.image = image
        self.tags = tags
        self.partype = partype
        self.stats = stats
        self.spells = spells
        self.passive = passive

class Item:
    def __init__(self,
                 id: str, # Item IDs are usually strings from data dragon (e.g., "1001")
                 name: str,
                 description: str,
                 colloq: str,
                 plaintext: str,
                 image: Dict[str, Any],
                 gold: Dict[str, int],
                 tags: List[str],
                 maps: Dict[str, bool],
                 stats: Dict[str, float],
                 into: Optional[List[str]] = None,
                 from_items: Optional[List[str]] = None, # Renamed from 'from'
                 depth: Optional[int] = None,
                 effect: Optional[Dict[str, str]] = None,
                 in_store: Optional[bool] = True
                ):
        self.id = id
        self.name = name
        self.description = description
        self.colloq = colloq
        self.plaintext = plaintext
        self.into = into if into is not None else []
        self.from_items = from_items if from_items is not None else []
        self.image = image
        self.gold = gold
        self.tags = tags
        self.maps = maps
        self.stats = stats
        self.depth = depth
        self.effect = effect if effect is not None else {}
        self.in_store = in_store

class Rune: # Representing a single rune/keystone
    def __init__(self,
                 id: int, # Rune IDs are integers
                 key: str, # Rune keys are strings (e.g., "PressTheAttack")
                 icon: str,
                 name: str,
                 shortDesc: str,
                 longDesc: str
                ):
        self.id = id
        self.key = key
        self.icon = icon
        self.name = name
        self.shortDesc = shortDesc
        self.longDesc = longDesc

class SummonerSpell:
    def __init__(self,
                 id: str, # Internal ID, e.g., "SummonerFlash"
                 name: str, # Display name, e.g., "Flash"
                 description: str,
                 tooltip: str,
                 maxrank: int,
                 cooldown: List[float], # Can be a single value list
                 cooldownBurn: str,
                 cost: List[int], # Can be a single value list
                 costBurn: str,
                 effect: List[Optional[List[float]]], # List of effects, each can be a list of numbers
                 effectBurn: List[Optional[str]],
                 image: Dict[str, Any],
                 key: str, # Numerical key as a string, e.g., "4"
                 modes: Optional[List[str]] = None # Game modes it's available in
                ):
        self.id = id
        self.name = name
        self.description = description
        self.tooltip = tooltip
        self.maxrank = maxrank
        self.cooldown = cooldown
        self.cooldownBurn = cooldownBurn
        self.cost = cost
        self.costBurn = costBurn
        self.effect = effect
        self.effectBurn = effectBurn
        self.image = image
        self.key = key
        self.modes = modes if modes is not None else []

# Example of how Rune Path/Tree structure might be handled later (not part of this task)
# class RunePath:
#     def __init__(self, id: int, key: str, icon: str, name: str, slots: List[Dict[str, Any]]):
#         self.id = id
#         self.key = key
#         self.icon = icon
#         self.name = name
#         self.slots = slots # Each slot contains a list of Runes
