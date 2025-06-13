import json
import os
from typing import Dict, List, Any
from pathlib import Path

# Adjust the import path based on your project structure if necessary
# Assuming models.py is in the same directory (src)
from models import Champion, Item, Rune, SummonerSpell

# Helper function to load a single JSON file
def _load_json_file(file_path: Path) -> Any:
    """Loads a JSON file and returns its content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
        return None

def load_champion_data(data_path: Path) -> Dict[str, Champion]:
    """Loads champion data from individual champion JSON files."""
    champions: Dict[str, Champion] = {}
    main_champion_file = data_path / 'champion.json'
    main_champion_data = _load_json_file(main_champion_file)

    if not main_champion_data or 'data' not in main_champion_data:
        print("Error: Could not load main champion.json or it has an unexpected format.")
        return champions

    for champ_key_from_summary, champ_summary_data in main_champion_data['data'].items():
        champion_id = champ_summary_data['id']

        individual_file_path = data_path / 'champions' / f"{champion_id}.json"

        champ_detail_outer = _load_json_file(individual_file_path)

        if champ_detail_outer and 'data' in champ_detail_outer and champion_id in champ_detail_outer['data']:
            champ_data = champ_detail_outer['data'][champion_id]

            required_fields = ['id', 'key', 'name', 'title', 'blurb', 'info', 'image', 'tags', 'partype', 'stats']
            if not all(field in champ_data for field in required_fields):
                print(f"Warning: Missing one or more required fields for champion {champion_id} in {individual_file_path}")
                continue

            spells_data = champ_data.get('spells', [])
            passive_data = champ_data.get('passive', {})

            try:
                champions[champion_id] = Champion(
                    id=champ_data['id'],
                    key=champ_data['key'],
                    name=champ_data['name'],
                    title=champ_data['title'],
                    blurb=champ_data['blurb'],
                    info=champ_data['info'],
                    image=champ_data['image'],
                    tags=champ_data['tags'],
                    partype=champ_data['partype'],
                    stats=champ_data['stats'],
                    spells=spells_data,
                    passive=passive_data
                )
            except KeyError as e:
                print(f"KeyError when creating Champion object for {champion_id}: {e} in file {individual_file_path}")
            except TypeError as e:
                 print(f"TypeError when creating Champion object for {champion_id}: {e} in file {individual_file_path}. Check model constructor.")
        else:
            print(f"Warning: Could not load or find detailed data for champion {champion_id} in {individual_file_path}")

    return champions

def load_item_data(data_path: Path) -> Dict[str, Item]:
    """Loads item data from item.json."""
    items: Dict[str, Item] = {}
    item_file = data_path / 'item.json'
    item_data_json = _load_json_file(item_file)

    if not item_data_json or 'data' not in item_data_json:
        print("Error: Could not load item.json or it has an unexpected format.")
        return items

    for item_id, data in item_data_json['data'].items():
        required_fields = ['name', 'description', 'plaintext', 'gold', 'tags', 'maps', 'stats']
        # 'image' is also essential, let's add it to required or handle its absence
        if not all(field in data for field in required_fields):
            print(f"Warning: Missing one or more required fields for item {item_id}")
            continue

        into_items = data.get('into', [])
        from_items_list = data.get('from', [])
        depth = data.get('depth') # Can be None if not present
        effect = data.get('effect', {})
        in_store = data.get('inStore', True)
        colloq = data.get('colloq', "")
        image_data = data.get('image', {}) # Default to empty dict if not present

        try:
            items[item_id] = Item(
                id=item_id,
                name=data['name'],
                description=data['description'],
                colloq=colloq,
                plaintext=data['plaintext'],
                into=into_items,
                image=image_data,
                gold=data['gold'],
                tags=data['tags'],
                maps=data['maps'],
                stats=data['stats'],
                depth=depth,
                from_items=from_items_list,
                effect=effect,
                in_store=in_store
            )
        except KeyError as e:
            print(f"KeyError when creating Item object for {item_id}: {e}")
        except TypeError as e:
            print(f"TypeError when creating Item object for {item_id}: {e}. Check model constructor.")

    return items

def load_rune_data(data_path: Path) -> List[Rune]:
    """Loads rune data from runesReforged.json."""
    runes: List[Rune] = []
    rune_file = data_path / 'runesReforged.json'
    rune_data_json = _load_json_file(rune_file)

    if not rune_data_json:
        print("Error: Could not load runesReforged.json.")
        return runes

    for tree in rune_data_json:
        if 'slots' not in tree:
            continue
        for slot in tree['slots']:
            if 'runes' not in slot:
                continue
            for data in slot['runes']:
                required_fields = ['id', 'key', 'icon', 'name', 'shortDesc', 'longDesc']
                if not all(field in data for field in required_fields):
                    print(f"Warning: Missing one or more required fields for rune with id {data.get('id', 'Unknown')}")
                    continue
                try:
                    runes.append(Rune(
                        id=data['id'],
                        key=data['key'],
                        icon=data['icon'],
                        name=data['name'],
                        shortDesc=data['shortDesc'],
                        longDesc=data['longDesc']
                    ))
                except KeyError as e:
                    print(f"KeyError when creating Rune object for id {data.get('id', 'Unknown')}: {e}")
                except TypeError as e:
                    print(f"TypeError when creating Rune object for id {data.get('id', 'Unknown')}: {e}. Check model constructor.")
    return runes

def load_summoner_spell_data(data_path: Path) -> Dict[str, SummonerSpell]:
    """Loads summoner spell data from summoner.json."""
    spells: Dict[str, SummonerSpell] = {}
    spell_file = data_path / 'summoner.json'
    spell_data_json = _load_json_file(spell_file)

    if not spell_data_json or 'data' not in spell_data_json:
        print("Error: Could not load summoner.json or it has an unexpected format.")
        return spells

    for spell_key, data in spell_data_json['data'].items(): # spell_key is e.g. "SummonerFlash"
        required_fields = ['id', 'name', 'description', 'tooltip', 'maxrank', 'cooldown', 'cooldownBurn', 'cost', 'costBurn', 'image', 'key']
        # 'effect' and 'effectBurn' can be complex or sometimes missing for certain spells, handle gracefully
        if not all(field in data for field in required_fields):
            print(f"Warning: Missing one or more required fields for summoner spell {spell_key}")
            continue

        modes = data.get('modes', [])
        # Default effect/effectBurn to empty lists if not present or if their structure is variable
        effect_data = data.get('effect', [])
        effect_burn_data = data.get('effectBurn', [])

        try:
            spells[spell_key] = SummonerSpell(
                id=data['id'],
                name=data['name'],
                description=data['description'],
                tooltip=data['tooltip'],
                maxrank=data['maxrank'],
                cooldown=data['cooldown'],
                cooldownBurn=data['cooldownBurn'],
                cost=data['cost'],
                costBurn=data['costBurn'],
                effect=effect_data,
                effectBurn=effect_burn_data,
                image=data['image'],
                key=data['key'],
                modes=modes
            )
        except KeyError as e:
            print(f"KeyError when creating SummonerSpell object for {spell_key}: {e}")
        except TypeError as e:
            print(f"TypeError when creating SummonerSpell object for {spell_key}: {e}. Check model constructor.")

    return spells

if __name__ == '__main__':
    current_script_path = Path(__file__).resolve()
    # Assuming this script is in lol_build_optimizer/src, then project_root is lol_build_optimizer
    project_root = current_script_path.parent.parent
    test_data_path = project_root / 'data'

    print(f"Attempting to load data from: {test_data_path}")

    # Ensure the 'champions' subdirectory exists for sample data creation
    (test_data_path / 'champions').mkdir(parents=True, exist_ok=True)

    # Minimal sample data for testing structure
    sample_champion_list_data = {
        "type": "champion", "format": "full", "version": "15.12.1",
        "data": { "TestChamp": {"id": "TestChamp", "key": "999", "name": "Test Champion"}}}
    sample_testchamp_data = {
        "type": "champion", "format": "full", "version": "15.12.1",
        "data": {
            "TestChamp": {
                "id": "TestChamp", "key": "999", "name": "Test Champion", "title": "the Tester",
                "blurb": "A champion for testing.", "info": {"attack":1,"defense":1,"magic":1,"difficulty":1}, "image": {"full":"TestChamp.png"}, "tags": ["Tester"], "partype": "Mana",
                "stats": {"hp": 600, "hpperlevel":100, "mp":300, "mpperlevel":50, "movespeed":350, "armor":30}, "spells": [], "passive": {"name":"TestPassive"}
            }}}
    sample_item_data = { "type": "item", "version": "15.12.1", "data": {
            "9001": {"name": "Test Item", "description": "An item for testing.", "colloq": ";test", "plaintext": "Test item.", "image": {"full":"9001.png"}, "gold": {"base": 100, "purchasable": True, "total": 100, "sell": 70}, "tags": ["Test"], "maps": {"11": True}, "stats": {"FlatHPRegenMod": 5.0}}}}
    sample_rune_data = [
        {"id": 9999, "key": "TestRuneTree", "icon": "test_tree.png", "name": "Test Tree", "slots": [
             {"runes": [{"id": 9998, "key": "TestRuneKey", "icon": "test_rune.png", "name": "Test Rune", "shortDesc": "A test rune.", "longDesc": "Longer desc."}]} ]}]
    sample_summoner_spell_data = { "type": "summoner", "version": "15.12.1", "data": {
            "SummonerTest": {"id": "SummonerTest", "name": "TestSpell", "description": "A test summoner spell.", "tooltip": "Test tooltip", "maxrank": 1, "cooldown": [60.0], "cooldownBurn": "60", "cost": [0], "costBurn": "0", "effect": [None], "effectBurn": [None], "image": {"full":"SummonerTest.png"}, "key": "99", "modes": ["CLASSIC"]}}}

    # Create sample files if they don't exist (for local testing)
    # These are created in the expected 'data' directory relative to project root
    if not (test_data_path / 'champion.json').exists():
        with open(test_data_path / 'champion.json', 'w', encoding='utf-8') as f: json.dump(sample_champion_list_data, f)
        print(f"Created sample: {test_data_path / 'champion.json'}")
    if not (test_data_path / 'champions' / 'TestChamp.json').exists():
        with open(test_data_path / 'champions' / 'TestChamp.json', 'w', encoding='utf-8') as f: json.dump(sample_testchamp_data, f)
        print(f"Created sample: {test_data_path / 'champions' / 'TestChamp.json'}")
    if not (test_data_path / 'item.json').exists():
        with open(test_data_path / 'item.json', 'w', encoding='utf-8') as f: json.dump(sample_item_data, f)
        print(f"Created sample: {test_data_path / 'item.json'}")
    if not (test_data_path / 'runesReforged.json').exists():
        with open(test_data_path / 'runesReforged.json', 'w', encoding='utf-8') as f: json.dump(sample_rune_data, f)
        print(f"Created sample: {test_data_path / 'runesReforged.json'}")
    if not (test_data_path / 'summoner.json').exists():
        with open(test_data_path / 'summoner.json', 'w', encoding='utf-8') as f: json.dump(sample_summoner_spell_data, f)
        print(f"Created sample: {test_data_path / 'summoner.json'}")

    print("--- Loading Champions ---")
    champions_loaded = load_champion_data(test_data_path)
    if champions_loaded:
        for champ_id, champ in list(champions_loaded.items())[:2]: # Print first 2
            print(f"  Loaded: {champ.name} (ID: {champ_id}), HP: {champ.stats.get('hp', 'N/A')}")
    else:
        print("  No champions loaded or an error occurred.")

    print("\n--- Loading Items ---")
    items_loaded = load_item_data(test_data_path)
    if items_loaded:
        for item_id, item in list(items_loaded.items())[:2]:
            print(f"  Loaded: {item.name} (ID: {item_id}), Cost: {item.gold.get('total', 'N/A')}")
    else:
        print("  No items loaded or an error occurred.")

    print("\n--- Loading Runes ---")
    runes_loaded = load_rune_data(test_data_path)
    if runes_loaded:
        for rune in runes_loaded[:2]:
            print(f"  Loaded: {rune.name} (ID: {rune.id})")
    else:
        print("  No runes loaded or an error occurred.")

    print("\n--- Loading Summoner Spells ---")
    summoner_spells_loaded = load_summoner_spell_data(test_data_path)
    if summoner_spells_loaded:
        for spell_id, spell in list(summoner_spells_loaded.items())[:2]:
            print(f"  Loaded: {spell.name} (ID: {spell_id})")
    else:
        print("  No summoner spells loaded or an error occurred.")

    print("\n--- Data Loader Script End ---")
