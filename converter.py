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
    return sets[code.upper()]["name"]


class CardMetadata:
    def __init__(
        self,
        quantity: int,
        name: str,
        set_code: str,
        is_foil: bool = False,
        collector_number: int = None,
    ):
        self.quantity = quantity
        self.name = name
        self.set_code = set_code
        self.is_foil = is_foil
        self.set_name = set_code_to_name(self.set_code)
        self.collector_number = collector_number

    def cardkingdom_csv_data(self) -> List:
        return [self.name, self.set_name, int(self.is_foil), self.quantity]

    def scryfall_decklist_line(self) -> str:
        line = f"{self.quantity} {self.name} | {self.set_code}"
        if self.collector_number is not None:
            return line + f" | {self.collector_number}"
        return line


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
                quantity, name, set_code = fields.groups()
                cards.append(
                    CardMetadata(quantity=quantity, name=name, set_code=set_code)
                )
    return cards


MOXFIELD_REGEX = r"(\d+) (.*) \((.*)\) (\d+)"


def read_moxfield(input_file: str) -> List[CardMetadata]:
    cards = []
    with open(input_file, "r") as f:
        while line := f.readline():
            if (fields := re.match(MOXFIELD_REGEX, line.strip())) is not None:
                quantity, name, set_code, collector_number = fields.groups()
                cards.append(
                    CardMetadata(
                        quantity=quantity,
                        name=name,
                        set_code=set_code,
                        collector_number=collector_number,
                    )
                )
    return cards


def write_cardkingdom_csv(output_file: str, cards: List[CardMetadata]):
    with open(output_file, "w", newline="") as f:
        w = csv.writer(f)
        for card in cards:
            w.writerow(card.cardkingdom_csv_data())


def write_scryfall(output_file: str, cards: List[CardMetadata]):
    with open(output_file, "w", newline="") as f:
        lines = [card.scryfall_decklist_line() for card in cards]
        f.write("\n".join(lines))


if __name__ == "__main__":
    sets = load_sets()
    cards = read_decklist(input_file="input.txt")
    # cards = read_moxfield(input_file="input.txt")
    write_cardkingdom_csv(output_file="output.csv", cards=cards)
    # write_scryfall(output_file="output.txt", cards=cards)
