import os
from pathlib import Path
import json # Added for ensure_sample_data

# Attempt to import from src, adjust if necessary based on how the script is run
# or if PYTHONPATH needs to be set.
try:
    from src import data_loader
    from src import models
    from src import core_logic
except ImportError:
    # This fallback might be needed if running directly from the root
    # and 'src' is not automatically in the Python path.
    print("Attempting fallback import for src modules...")
    import sys
    # Get the parent directory of the current script's directory (src)
    # Assuming main.py is in project_root and src is project_root/src
    project_root_path = Path(__file__).parent.resolve()
    src_path = project_root_path / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path)) # Add src to path for `from models import ...`
        print(f"Added {src_path} to sys.path for direct src imports")

    # If src files use `from .models`, and we run main.py from root,
    # then src needs to be treated as a package.
    # The above sys.path.insert for src_path helps data_loader find models.
    # If core_logic/data_loader themselves try `from .models`, they need `src` to be a package context
    # This is usually handled by running `python -m src.main_module_in_src` or proper project installation.
    # For this direct execution of main.py from root, ensuring src/ is in path for `from models` is key.
    # And ensuring main.py can do `from src import ...` is also key.
    # Let's add project_root_path to allow `from src import ...` if not already covered.
    # This means Python looks in project_root_path for a directory named 'src'.
    if str(project_root_path) not in sys.path and (project_root_path / "src").exists():
         sys.path.insert(0, str(project_root_path))
         print(f"Added {project_root_path} to sys.path for 'from src import ...' to work")


    # Re-try imports
    from src import data_loader
    from src import models
    from src import core_logic


def run_cli():
    """Runs the command-line interface for the LoL Build Optimizer."""

    # Determine the base path for data files
    # Assumes 'data' directory is at the same level as 'main.py' (project root)
    base_data_path = Path(__file__).parent / 'data'
    print(f"LoL Build Optimizer - CLI")
    print(f"==========================")
    print(f"Loading data from: {base_data_path}...")

    # Ensure data subdirectories exist if using sample data generation from data_loader
    (base_data_path / 'champions').mkdir(parents=True, exist_ok=True)

    # --- Helper to ensure sample data exists if real data is missing ---
    ensure_sample_data(base_data_path)
    # --- End Helper ---

    # 1. Load data
    champions = data_loader.load_champion_data(base_data_path)
    items = data_loader.load_item_data(base_data_path)
    # runes_data = data_loader.load_rune_data(base_data_path) # Not used
    # summoner_spells_data = data_loader.load_summoner_spell_data(base_data_path) # Not used

    if not champions or not items:
        print("\nError: Could not load essential champion or item data. Exiting.")
        if not (base_data_path / 'champion.json').exists():
            print(f"Hint: Expected champion data file not found: {base_data_path / 'champion.json'}")
        if not (base_data_path / 'item.json').exists():
            print(f"Hint: Expected item data file not found: {base_data_path / 'item.json'}")
        return

    print(f"\nSuccessfully loaded {len(champions)} champions and {len(items)} items.")
    print(f"Note: If these numbers are very small (e.g. 1 champ, 1 item), data_loader might be using its internal sample data because actual data files were not found at '{base_data_path}'.")


    # 2. Champion Selection
    print("\n--- Champion Selection ---")
    sorted_champion_list = sorted([(champ.name, champ_id) for champ_id, champ in champions.items()])

    for i, (name, champ_id) in enumerate(sorted_champion_list):
        print(f"{i + 1}. {name} (ID: {champ_id})")

    selected_champion_obj = None
    while not selected_champion_obj:
        try:
            choice = input("Select a champion by number: ")
            selected_idx = int(choice) - 1
            if 0 <= selected_idx < len(sorted_champion_list):
                _name, champ_id_chosen = sorted_champion_list[selected_idx]
                selected_champion_obj = champions[champ_id_chosen]
                print(f"You selected: {selected_champion_obj.name} - {selected_champion_obj.title}")
                print(f"Tags: {', '.join(selected_champion_obj.tags)}")
                print(f"Archetype(s) identified: {', '.join(core_logic.get_champion_archetype(selected_champion_obj))}")
                print("Base Stats (first 5):")
                for stat, value in list(selected_champion_obj.stats.items())[:5]:
                     print(f"  {stat}: {value}")
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"An unexpected error during champion selection: {e}")
            return


    # 3. Item Selection for Build
    print("\n--- Build Creation ---")
    # Filter for purchasable items and then sort by name
    purchasable_items = {item_id: item for item_id, item in items.items() if item.in_store and item.gold.get('purchasable', True)}
    sorted_item_list = sorted([(item.name, item_id) for item_id, item in purchasable_items.items()])

    print("Available Items (showing first 20 purchasable):")
    items_to_show = min(20, len(sorted_item_list))
    for i, (name, item_id) in enumerate(sorted_item_list[:items_to_show]):
        cost = purchasable_items[item_id].gold.get('total', 'N/A')
        print(f"{i + 1}. {name} (ID: {item_id}, Cost: {cost})")
    if len(sorted_item_list) > items_to_show:
        print(f"...and {len(sorted_item_list) - items_to_show} more items available (select by ID).")

    selected_items_for_build: List[models.Item] = []
    max_items = 6

    while len(selected_items_for_build) < max_items:
        print(f"\nCurrent Build ({len(selected_items_for_build)}/{max_items} items): {[item.name for item in selected_items_for_build]}")
        choice = input(f"Enter item number (1-{items_to_show}), item ID, or 'done'/'exit': ").strip().lower()

        if choice == 'done':
            if not selected_items_for_build:
                print("No items selected. Add at least one item or type 'exit'.")
                continue
            break
        if choice == 'exit':
            print("Exiting build creation.")
            return

        item_obj_to_add = None
        try:
            if choice.isdigit() and 1 <= int(choice) <= items_to_show: # Selection from displayed list
                selected_item_idx = int(choice) - 1
                if 0 <= selected_item_idx < items_to_show: # Ensure index is within the displayed portion
                    _name, item_id_chosen = sorted_item_list[selected_item_idx]
                    item_obj_to_add = purchasable_items[item_id_chosen]
                else:
                    print("Selection out of displayed list range.")
            elif choice in purchasable_items: # Direct ID input
                item_obj_to_add = purchasable_items[choice]
            else:
                print(f"Invalid selection or item ID '{choice}' not found among purchasable items.")

            if item_obj_to_add:
                if item_obj_to_add in selected_items_for_build:
                     print(f"Item '{item_obj_to_add.name}' is already in the build.")
                else:
                    selected_items_for_build.append(item_obj_to_add)
                    print(f"Added {item_obj_to_add.name} to build.")
        except ValueError: # Handles non-integer input if choice.isdigit() was false but it was still not a valid ID
            print("Invalid input. Please enter a number, an item ID, or 'done'/'exit'.")
        except Exception as e:
            print(f"An unexpected error during item selection: {e}")
            continue

    if not selected_items_for_build:
        print("No items were selected for the build. Cannot evaluate.")
    else:
        # 4. Evaluate Build
        print("\n--- Build Evaluation ---")
        build_score = core_logic.evaluate_build_simple(selected_champion_obj, selected_items_for_build)
        print(f"Champion: {selected_champion_obj.name}")
        print(f"Build: {[item.name for item in selected_items_for_build]}")
        print(f"Simple Evaluation Score: {build_score:.2f}")
        print("(Higher score is generally better according to the simple evaluation logic.)")

    print("\nExiting LoL Build Optimizer CLI.")


def ensure_sample_data(test_data_path: Path):
    """
    Creates minimal sample JSON files if actual data files are not found.
    This helps in testing main.py independently of prior data fetching steps.
    """
    print(f"Checking for data files in {test_data_path}. Will create samples if missing.")
    sample_files_created = False

    # Ensure 'champions' subdirectory exists for sample champion details
    (test_data_path / 'champions').mkdir(parents=True, exist_ok=True)

    sample_champion_list_data = {
        "type": "champion", "format": "full", "version": "15.12.1",
        "data": { "TestChamp": {"id": "TestChamp", "key": "999", "name": "Test Champion", "title": "the Tester"}}}
    sample_testchamp_data = {
        "type": "champion", "format": "full", "version": "15.12.1",
        "data": {
            "TestChamp": {
                "id": "TestChamp", "key": "999", "name": "Test Champion", "title": "the Tester",
                "blurb": "A champion for testing.", "info": {"attack":1.0,"defense":1.0,"magic":1.0,"difficulty":1.0},
                "image": {"full":"TestChamp.png"}, "tags": ["Mage", "Fighter"], "partype": "Mana",
                "stats": {"hp": 600.0, "mp":300.0}, "spells": [], "passive": {"name":"TestPassive"}
            }}}
    sample_item_data = { "type": "item", "version": "15.12.1", "data": {
            "9001": {"name": "Test Item Alpha", "description": "An item for testing.", "colloq": ";test", "plaintext": "Test item.",
                     "image": {"full":"9001.png"}, "gold": {"base": 100, "purchasable": True, "total": 100, "sell": 70},
                     "tags": ["Test", "Active"], "maps": {"11": True}, "stats": {"FlatMagicDamageMod": 10.0, "FlatHPPoolMod": 100.0}},
            "9002": {"name": "Test Item Beta", "description": "Another item.", "colloq": ";test2", "plaintext": "Test item 2.",
                     "image": {"full":"9002.png"}, "gold": {"base": 200, "purchasable": True, "total": 200, "sell": 140},
                     "tags": ["Test", "Health"], "maps": {"11": True}, "stats": {"FlatHPPoolMod": 200.0, "FlatPhysicalDamageMod": 15.0 }}
            }}

    files_to_check_and_create = {
        'champion.json': sample_champion_list_data,
        'champions/TestChamp.json': sample_testchamp_data,
        'item.json': sample_item_data,
    }

    for filename, sample_data_content in files_to_check_and_create.items():
        file_path = test_data_path / filename
        if not file_path.exists():
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(sample_data_content, f, indent=4)
                print(f"Created sample data: {file_path}")
                sample_files_created = True
            except Exception as e:
                print(f"Error creating sample file {file_path}: {e}")
        else:
            print(f"Found existing data file: {file_path} (sample creation skipped).")

    if sample_files_created:
         print("Sample data files were created. The application will use these.")
    else:
         print("All necessary data files were found or no samples needed to be created.")


if __name__ == '__main__':
    run_cli()
