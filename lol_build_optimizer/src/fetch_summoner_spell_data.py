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
SUMMONER_SPELL_DATA_URL = f"{BASE_URL}/summoner.json"

DATA_DIR = "lol_build_optimizer/data"
SUMMONER_SPELL_FILE_PATH = os.path.join(DATA_DIR, "summoner.json")

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
    logging.info("Starting summoner spell data fetch process.")

    # Create base data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
        logging.info(f"Created directory: {DATA_DIR}")

    # Fetch and save summoner.json
    logging.info(f"Fetching summoner spell data from {SUMMONER_SPELL_DATA_URL}")
    summoner_spell_data = fetch_json(SUMMONER_SPELL_DATA_URL)

    if not summoner_spell_data:
        logging.error("Could not fetch summoner spell data. Exiting.")
        return

    save_json(summoner_spell_data, SUMMONER_SPELL_FILE_PATH)
    logging.info("Summoner spell data fetch process completed.")

if __name__ == "__main__":
    main()
