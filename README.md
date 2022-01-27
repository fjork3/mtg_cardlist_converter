# mtg_cardlist_converter

Move your decklists between different providers' formats.

## Usage

- Run `converter.py` with a file called `input.txt` in the same directory, in decklist format:
- `1 Llanowar Elves (DOM)` or `1 Llanowar Elves [DOM]`
- output CSV will be writen to `output.csv`, in CardKingdom import format:
- `Llanowar Elves,Dominaria,0,1`

## Known issues / future improvements

- Set names are currently pulled from Scryfall, based on provided set codes; these don't necessarily line up with CK's
  internal catalog.
- Currently supported formats just include TCGplayer collection export, which doesn't include a foil specifier.
