import csv
from typing import List
import requests
import re

sets_req = requests.get("https://api.scryfall.com/sets")
sets_req.raise_for_status()

# Lookup from set code to Scryfall set objects:
# https://scryfall.com/docs/api/sets
sets = {x["code"].upper(): x for x in sets_req.json()["data"]}


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


DECKLIST_REGEX = r"(\d+) (.*) [\[\(](.*)[\]\)]"

if __name__ == "__main__":
    cards = []

    # For now, expect TCGplayer collection output format:
    # 4 Polluted Delta [ONS]
    with open("input.txt", "r") as f:
        while line := f.readline():
            if (fields := re.match(DECKLIST_REGEX, line.strip())) is not None:
                quantity, name, code = fields.groups()
                cards.append(CardMetadata(quantity=quantity, name=name, set_code=code))

    with open("output.csv", "w", newline="") as f:
        w = csv.writer(f)
        for card in cards:
            w.writerow(card.cardkingdom_csv_data())
