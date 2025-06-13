import requests
import json
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
DDRAGON_VERSION = "15.12.1"
LANGUAGE = "en_US"
BASE_URL = f"https://ddragon.leagueoflegends.com/cdn/{DDRAGON_VERSION}/data/{LANGUAGE}"
CHAMPION_DATA_URL = f"{BASE_URL}/champion.json"

DATA_DIR = "lol_build_optimizer/data"
CHAMPIONS_SUBDIR = os.path.join(DATA_DIR, "champions")

def fetch_json(url):
    """Fetches JSON data from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None

def save_json(data, filepath):
    """Saves JSON data to a file."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Successfully saved data to {filepath}")
    except IOError as e:
        logging.error(f"Error saving data to {filepath}: {e}")

def main():
    logging.info("Starting champion data fetch process.")

    # Create base data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
        logging.info(f"Created directory: {DATA_DIR}")

    # Fetch and save champion.json
    logging.info(f"Fetching general champion data from {CHAMPION_DATA_URL}")
    all_champions_data = fetch_json(CHAMPION_DATA_URL)

    if not all_champions_data:
        logging.error("Could not fetch general champion data. Exiting.")
        return

    main_champion_file_path = os.path.join(DATA_DIR, "champion.json")
    save_json(all_champions_data, main_champion_file_path)

    if not 'data' in all_champions_data:
        logging.error("'data' key not found in champion.json. Cannot process individual champions.")
        return

    # Create subdirectory for individual champion data
    if not os.path.exists(CHAMPIONS_SUBDIR):
        os.makedirs(CHAMPIONS_SUBDIR, exist_ok=True)
        logging.info(f"Created directory: {CHAMPIONS_SUBDIR}")

    # Fetch and save individual champion data
    champions = all_champions_data['data']
    logging.info(f"Found {len(champions)} champions. Fetching individual data...")

    # Limit to first 5 champions for testing to avoid timeout
    champion_ids_to_fetch = list(champions.keys())[:5]
    logging.info(f"Processing the first {len(champion_ids_to_fetch)} champions: {champion_ids_to_fetch}")

    for champion_id in champion_ids_to_fetch:
        individual_champion_url = f"{BASE_URL}/champion/{champion_id}.json"
        logging.info(f"Fetching data for {champion_id} from {individual_champion_url}")

        champion_detail_data = fetch_json(individual_champion_url)

        if champion_detail_data:
            # The individual champion JSON is nested under a 'data' key itself,
            # and then keyed by the champion's ID.
            # We want to save the content of champion_detail_data['data'][champion_id]
            if 'data' in champion_detail_data and champion_id in champion_detail_data['data']:
                champion_specific_data_to_save = champion_detail_data['data'][champion_id]
                champion_file_path = os.path.join(CHAMPIONS_SUBDIR, f"{champion_id}.json")
                save_json(champion_specific_data_to_save, champion_file_path)
            else:
                logging.warning(f"Data format unexpected for {champion_id}. Skipping save for this champion.")
        else:
            logging.warning(f"Could not fetch data for {champion_id}. Skipping.")

    logging.info(f"Champion data fetch process completed for the first {len(champion_ids_to_fetch)} champions.")

if __name__ == "__main__":
    main()
