# chess-opening-prep
A tool to practice openings using an optimized player book and a high-variance opponent book.

## Installation
After cloning the repository, run `pip install -r requirements.txt` to download the necessary Python packages.

For full standalone functionality, it is recommended to use the [kitty](https://sw.kovidgoyal.net/kitty/) terminal emulator. This will enable full images of the board to be displayed in the console. In other emulators, a simple text-based board will be shown.

Next, you will need to obtain polyglot opening books for the player and opponent. For the player, I recommend a high-performance opening book such as [Cerebellum](https://www.zipproth.de/Brainfish/download/), which we cannot include here due to license incompatibility.

For the opponent, I recommend a high-variance book that still has a good depth of lines. For this purpose, you can use the `gm2600.bin` or `Elo2400.bin` book provided by [Scid vs PC](http://scidvspc.sourceforge.net/), included here for convenience.

Personally, I recommend instead generating an opponent book using games from the Lichess database. For this purpose, you can clone lichapibot's [book builder](https://github.com/lichapibot/lichess-bot) and follow the instructions there. For convenience, I have included a book `dec2015.bin` constructed from a subset of the Lichess database, though it is rather small due to Github's filesize limit.

Optionally, you may also download an engine such as [Stockfish](https://stockfishchess.org/) to provide analysis when you reach the end of the book.

## Confuguration
Simply edit the entries in `config.yml` according to your specifications. You can use the "lines" entry to practice particular openings -- this way, you will not be forced to replay the initial moves.

### Copyright Notice:
Book files (Elo2400.bin and gm2600.bin): Pascal Georges
