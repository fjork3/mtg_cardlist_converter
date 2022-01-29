import csv
import json
import os.path
from typing import List, Dict
import requests
import re


# Load local set data if available, falling back to Scryfall API
def load_sets() -> Dict:
    if os.path.exists("scryfall_sets.json"):
        with open("scryfall_sets.json", "r") as f:
            set_json = json.load(f)
            return {x["code"].upper(): x for x in set_json["data"]}

    # Scryfall API docs: https://scryfall.com/docs/api/sets
    sets_req = requests.get("https://api.scryfall.com/sets")
    sets_req.raise_for_status()
    return {x["code"].upper(): x for x in sets_req.json()["data"]}


def set_code_to_name(code: str) -> str:
    # TODO: deal with sets that providers don't call by name (e.g. Promotional)
    return sets[code]["name"]


class CardMetadata:
    def __init__(self, quantity: int, name: str, set_code: str, is_foil: bool = False):
        self.quantity = quantity
        self.name = name
        self.set_code = set_code
        self.is_foil = is_foil
        self.set_name = set_code_to_name(self.set_code)

    def cardkingdom_csv_data(self) -> List:
        return [self.name, self.set_name, int(self.is_foil), self.quantity]


# Matches these formats:
# 1 Llanowar Elves (DOM)
# 1 Llanowar Elves [DOM]
DECKLIST_REGEX = r"(\d+) (.*) [\[\(](.*)[\]\)]"
# TODO: function for decklist line matching, with more fallback regexes for other formats

def read_decklist(input_file: str) -> List[CardMetadata]:
    cards = []
    with open(input_file, "r") as f:
        while line := f.readline():
            if (fields := re.match(DECKLIST_REGEX, line.strip())) is not None:
                quantity, name, code = fields.groups()
                cards.append(CardMetadata(quantity=quantity, name=name, set_code=code))
    return cards


def write_cardkingdom_csv(output_file: str, cards: List[CardMetadata]):
    with open(output_file, "w", newline="") as f:
        w = csv.writer(f)
        for card in cards:
            w.writerow(card.cardkingdom_csv_data())


if __name__ == "__main__":
    sets = load_sets()
    cards = read_decklist(input_file="input.txt")
    write_cardkingdom_csv(output_file="output.csv", cards=cards)
