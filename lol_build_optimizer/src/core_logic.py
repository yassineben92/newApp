from typing import List, Dict, Any
# Assuming models.py and data_loader.py are in the same directory (src)
# Adjust imports if your structure or execution context differs
try:
    from .models import Champion, Item
except ImportError: # Fallback for direct script execution
    from models import Champion, Item

# Define preferred stats for champion archetypes (simplified)
# These are examples; actual stat names from Data Dragon should be used.
# We'll need to map these generic names to actual stat names from item data later.
ARCHETYPE_PREFERRED_STATS = {
    "Mage": {"FlatMagicDamageMod": 2.0, "FlatMPPoolMod": 0.5, "PercentCooldownMod": 1.5},
    "Fighter": {"FlatPhysicalDamageMod": 1.5, "FlatHPPoolMod": 1.0, "PercentAttackSpeedMod": 1.0, "FlatArmorMod": 0.5},
    "Tank": {"FlatHPPoolMod": 2.0, "FlatArmorMod": 2.0, "FlatSpellBlockMod": 2.0, "PercentTenacityMod": 1.0},
    "Marksman": {"FlatPhysicalDamageMod": 2.0, "PercentAttackSpeedMod": 2.0, "PercentCritChanceMod": 1.5}, # Changed FlatCritChanceMod to PercentCritChanceMod for consistency if it's a percentage
    "Assassin": {"FlatPhysicalDamageMod": 1.8, "FlatMagicDamageMod": 1.8, "FlatArmorPenetrationMod": 1.5, "FlatMagicPenetrationMod": 1.5}, # Hybrid example
    "Support": {"PercentHealAndShieldPowerMod": 2.0, "FlatHPPoolMod": 1.0, "FlatManaRegenMod": 1.0, "PercentCooldownMod": 1.0}
}

# Generic to Data Dragon stat name mapping (example, needs to be comprehensive)
# This mapping is crucial and needs to be accurate based on Data Dragon item stats names
STAT_NAME_MAPPING = {
    "AbilityPower": "FlatMagicDamageMod",
    "AttackDamage": "FlatPhysicalDamageMod",
    "Health": "FlatHPPoolMod",
    "Armor": "FlatArmorMod",
    "MagicResist": "FlatSpellBlockMod",
    "AttackSpeed": "PercentAttackSpeedMod", # Note: DDragon often uses Percent for AS
    "CooldownReduction": "PercentCooldownMod", # Placeholder, DDragon might have specific names like 'FlatCDRReduction_PARSED' or similar
    "CriticalStrikeChance": "PercentCritChanceMod", # Changed from FlatCritChanceMod for example consistency
    # Add more mappings as identified from item.json
}


def get_champion_archetype(champion: Champion) -> List[str]:
    """
    Determines the archetype(s) of a champion based on their tags.
    Returns a list of archetypes. A champion can fit into multiple archetypes.
    """
    tags = champion.tags
    archetypes = []
    if "Mage" in tags:
        archetypes.append("Mage")
    if "Fighter" in tags:
        archetypes.append("Fighter")
    if "Tank" in tags:
        archetypes.append("Tank")
    if "Marksman" in tags:
        archetypes.append("Marksman")
    if "Assassin" in tags:
        archetypes.append("Assassin")
    if "Support" in tags:
        archetypes.append("Support")

    # if not archetypes and "Fighter" in tags : # This logic seems redundant given the above checks
    #     archetypes.append("Fighter")
    if not archetypes: # Fallback if no clear tags or if primary tags don't make an archetype
        # Check for secondary indicators if primary archetypes list is empty
        if "Fighter" in tags : # Example: if only "Fighter" tag, ensure it's added
             archetypes.append("Fighter")
        elif len(tags) > 0: # If tags exist but none mapped, could default or log
            # print(f"Warning: Champion {champion.name} has tags {tags} but no archetype mapped. Defaulting to Fighter.")
            archetypes.append("Fighter") # Defaulting for now
        else: # No tags at all
            # print(f"Warning: Champion {champion.name} has no tags. Defaulting to Fighter.")
            archetypes.append("Fighter") # Default to Fighter if no tags found

    return list(set(archetypes)) # Ensure unique archetypes


def evaluate_build_simple(champion: Champion, items: List[Item]) -> float:
    """
    Evaluates a given build (list of items) for a specific champion based on simple heuristics.
    Returns a numerical score. Higher is better.
    """
    total_score = 0.0
    aggregated_stats: Dict[str, float] = {}

    # 1. Aggregate stats from items
    for item in items:
        for stat_name, stat_value in item.stats.items():
            aggregated_stats[stat_name] = aggregated_stats.get(stat_name, 0.0) + stat_value

    # 2. Determine champion archetype(s)
    archetypes = get_champion_archetype(champion)

    # 3. Score based on archetype preferences
    stats_contribution_to_score = 0.0

    for archetype in archetypes:
        preferred_stats = ARCHETYPE_PREFERRED_STATS.get(archetype, {})
        for stat_from_build, build_value in aggregated_stats.items():
            if stat_from_build in preferred_stats:
                weight = preferred_stats[stat_from_build]
                stats_contribution_to_score += build_value * weight
            # The STAT_NAME_MAPPING logic as written in the prompt is not actively used here
            # if ARCHETYPE_PREFERRED_STATS directly uses Data Dragon names.
            # It would be useful if ARCHETYPE_PREFERRED_STATS used generic names.

    total_score += stats_contribution_to_score

    return total_score

if __name__ == '__main__':
    # This block is for basic testing of the core_logic.py file.
    print("--- Testing core_logic.py ---")

    # Mock Champion (simplified for testing)
    mock_mage_stats = {"hp": 550.0, "mp": 350.0, "attackdamage": 50.0, "movespeed": 340.0} # Ensure float for stats
    mock_mage = Champion(id="TestMage", key="1001", name="Test Mage", title="the Magical", blurb="",
                         info={"attack":1.0,"defense":1.0,"magic":1.0,"difficulty":1.0}, image={"full":"TestMage.png"}, tags=["Mage"], partype="Mana", stats=mock_mage_stats,
                         spells=[], passive={"name":"TestPassive"})

    mock_fighter_stats = {"hp": 600.0, "mp": 200.0, "attackdamage": 65.0, "movespeed": 345.0}
    mock_fighter = Champion(id="TestFighter", key="1002", name="Test Fighter", title="the Brawler", blurb="",
                            info={"attack":1.0,"defense":1.0,"magic":1.0,"difficulty":1.0}, image={"full":"TestFighter.png"}, tags=["Fighter", "Tank"], partype="Mana", stats=mock_fighter_stats,
                            spells=[], passive={"name":"TestPassive"})

    # Mock Items (simplified for testing, using actual Data Dragon stat names)
    item1_stats = {"FlatMagicDamageMod": 80.0, "FlatMPPoolMod": 500.0}
    item1 = Item(id="3089", name="Rabadon's Deathcap (Mock)", description="High AP", colloq="", plaintext="",
                 gold={"base": 100, "purchasable": True, "total": 3600, "sell": 100}, tags=["MagicDamage", "Mana"], image={"full":"item1.png"}, maps={"11":True}, stats=item1_stats)

    item2_stats = {"FlatPhysicalDamageMod": 50.0, "PercentAttackSpeedMod": 0.35} # Assuming 0.35 means 35%
    item2 = Item(id="3072", name="Bloodthirster (Mock)", description="High AD and Lifesteal", colloq="", plaintext="",
                 gold={"base": 100, "purchasable": True, "total": 3400, "sell": 100}, tags=["Damage", "AttackSpeed", "LifeSteal"], image={"full":"item2.png"}, maps={"11":True}, stats=item2_stats)

    item3_stats = {"FlatHPPoolMod": 400.0, "FlatArmorMod": 60.0}
    item3 = Item(id="3075", name="Thornmail (Mock)", description="Health and Armor", colloq="", plaintext="",
                 gold={"base": 100, "purchasable": True, "total": 2700, "sell": 100}, tags=["Health", "Armor"], image={"full":"item3.png"}, maps={"11":True}, stats=item3_stats)

    # Test case 1: Mage with an AP item
    mage_build_1 = [item1]
    score1 = evaluate_build_simple(mock_mage, mage_build_1)
    print(f"Score for {mock_mage.name} with [{item1.name}]: {score1:.2f}")
    # Expected: (80 AP * 2.0) + (500 Mana * 0.5) = 160 + 250 = 410

    # Test case 2: Mage with an AD item
    mage_build_2 = [item2]
    score2 = evaluate_build_simple(mock_mage, mage_build_2)
    print(f"Score for {mock_mage.name} with [{item2.name}]: {score2:.2f}")
    # Expected: 0.0 (Mage archetype has no preference for FlatPhysicalDamageMod or PercentAttackSpeedMod)

    # Test case 3: Fighter with AD/AS item
    fighter_build_1 = [item2] # Fighter is tagged ["Fighter", "Tank"]
    score3 = evaluate_build_simple(mock_fighter, fighter_build_1)
    print(f"Score for {mock_fighter.name} with [{item2.name}]: {score3:.2f}")
    # Fighter component: (50 AD * 1.5) + (0.35 AS * 1.0) = 75 + 0.35 = 75.35
    # Tank component: (AD and AS are not in Tank preferred stats) = 0
    # Total = 75.35

    # Test case 4: Fighter with AP and Tank item
    fighter_build_2 = [item1, item3] # Fighter is tagged ["Fighter", "Tank"]
    score4 = evaluate_build_simple(mock_fighter, fighter_build_2)
    print(f"Score for {mock_fighter.name} with [{item1.name}, {item3.name}]: {score4:.2f}")
    # From item1 (AP item):
    #   Fighter component: FlatMagicDamageMod not in Fighter list, FlatMPPoolMod not in Fighter list. Score = 0
    #   Tank component: FlatMagicDamageMod not in Tank list, FlatMPPoolMod not in Tank list. Score = 0
    # From item3 (Tank item):
    #   Fighter component: (400 HP * 1.0) + (60 Armor * 0.5) = 400 + 30 = 430
    #   Tank component: (400 HP * 2.0) + (60 Armor * 2.0) = 800 + 120 = 920
    # Total = 430 (from Fighter) + 920 (from Tank) = 1350.00
    # Note: The logic sums scores if a champion fits multiple archetypes and items have stats for them.

    print("--- Finished core_logic.py test ---")
