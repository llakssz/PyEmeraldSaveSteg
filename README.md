# PyEmeraldSaveSteg

A Python 3 application able to edit Pokemon Emerald saves.
It can also be used an a steganography tool, storing a maximum of 28,140 bytes in the Pokemon Storage System (boxes).

Only English language saves are recommended and have been tested.

As an editor, only the pokemon within the boxes are able to be edited.
Supports reading/editing:
* Species
* Level
* Exp
* Held Item
* Moves
* PP
* PID
* OTID
* Name
* Egg flag (make/hatch egg)
* IVs
* EVs
* Ability (although not all pokemon have a second ability)

As a steganography tool, a data file is hidden within eggs.
Upon viewing these eggs in the boxes, it is impossible to tell that any data is hidden within.
Notice: Japanese games display eggs differently, in the summary these name of these eggs will NOT be Egg/タマゴ, and thus it is possible to see that there is something strange in the save file.
The order of the eggs matter, so if you change the position of the eggs, make sure to put them back in the correct order when you want to extract them.
Maximum data stored possible is 28,140 bytes (420 box capacity * 67 bytes per egg)

It is also possible to store a secret text within the names of pokemon, meaning no special tools are needed to extract.
The secret text will be encoded to Base64, which is used to rename as many pokemon needed to hold the string.
Maximum secret text length is 4200 (420 box capactiy * 10 name length)