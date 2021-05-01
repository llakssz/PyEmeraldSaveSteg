#!/usr/bin/env python3

# 2021 - jtm.gg
# Version 0.9

import argparse
import base64
import binascii
import itertools
import math
import os
import random
import sys
from enum import Enum

parser = argparse.ArgumentParser()
parser.add_argument('save_path', help='Filepath to save, used for reading and writing (good idea to make a backup first)')
parser.add_argument('--use-backup-save', '-b', help='Use the backup save (not the current save)', action='store_true')
parser.add_argument('--num-bytes-extract', '-n', help='Exact number of bytes to extract. End of data is (usually) padded with empty/null/0x0 bytes, use this to trim the secret data when saving secret data to a file')
group = parser.add_mutually_exclusive_group()
group.add_argument('--store', '-s', help='Filepath, to store in save as eggs. Writes backwards from last cell in Box 14')
group.add_argument('--extract', '-e', help='Filepath, to extract stored data to. Reads from last cell in Box 14, must have a non egg cell next to final egg')
group.add_argument('--verify', '-v', help='Filepath, to check if file exists in save. Reads backwards from last cell in Box 14, must have a blank cell nex to final egg')
group.add_argument('--text-to-b64-names', '-t', help='Text that will be converted to base64, then split across pokemon names. Starts with the first cell in Box 1. If empty cells in box are encountered, a Lv 0 Bulbasaur will be created. Better to make sure enough pokemon are in your box.')
args = parser.parse_args()

if args.num_bytes_extract and (not args.extract):
    print('Number of bytes to extract were given, but we\'re not extracting...')
    print('Exiting, make sure you use the correct options!')
    sys.exit()

# only confirmed to apply to English language game
text_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
text_bytes = [0xBB,0xBC,0xBD,0xBE,0xBF,0xC0,0xC1,0xC2,0xC3,0xC4,0xC5,0xC6,0xC7,0xC8,0xC9,0xCA,0xCB,0xCC,0xCD,0xCE,0xCF,0xD0,0xD1,0xD2,0xD3,0xD4,0xD5,0xD6,0xD7,0xD8,0xD9,0xDA,0xDB,0xDC,0xDD,0xDE,0xDF,0xE0,0xE1,0xE2,0xE3,0xE4,0xE5,0xE6,0xE7,0xE8,0xE9,0xEA,0xEB,0xEC,0xED,0xEE,0xA1,0xA2,0xA3,0xA4,0xA5,0xA6,0xA7,0xA8,0xA9,0xAA,0x2E,0xBA,0x35]
char2byte_dict = {}
byte2char_dict = {}
for i, char in enumerate(text_chars):
    curr_byte = text_bytes[i]
    char2byte_dict[char] = curr_byte
    byte2char_dict[curr_byte] = char

# items
item_list = ["","Master Ball","Ultra Ball","Great Ball","Poké Ball","Safari Ball","Net Ball","Dive Ball","Nest Ball","Repeat Ball","Timer Ball","Luxury Ball","Premier Ball","Potion","Antidote","Burn Heal","Ice Heal","Awakening","Parlyz Heal","Full Restore","Max Potion","Hyper Potion","Super Potion","Full Heal","Revive","Max Revive","Fresh Water","Soda Pop","Lemonade","Moomoo Milk","EnergyPowder","Energy Root","Heal Powder","Revival Herb","Ether","Max Ether","Elixir","Max Elixir","Lava Cookie","Blue Flute","Yellow Flute","Red Flute","Black Flute","White Flute","Berry Juice","Sacred Ash","Shoal Salt","Shoal Shell","Red Shard","Blue Shard","Yellow Shard","Green Shard","?","?","?","?","?","?","?","?","?","?","?","HP Up","Protein","Iron","Carbos","Calcium","Rare Candy","PP Up","Zinc","PP Max","?","Guard Spec.","Dire Hit","X Attack","X Defend","X Speed","X Accuracy","X Special","Poké Doll","Fluffy Tail","?","Super Repel","Max Repel","Escape Rope","Repel","?","?","?","?","?","?","Sun Stone","Moon Stone","Fire Stone","Thunderstone","Water Stone","Leaf Stone","?","?","?","?","TinyMushroom","Big Mushroom","?","Pearl","Big Pearl","Stardust","Star Piece","Nugget","Heart Scale","?","?","?","?","?","?","?","?","?","Orange Mail","Harbor Mail","Glitter Mail","Mech Mail","Wood Mail","Wave Mail","Bead Mail","Shadow Mail","Tropic Mail","Dream Mail","Fab Mail","Retro Mail","Cheri Berry","Chesto Berry","Pecha Berry","Rawst Berry","Aspear Berry","Leppa Berry","Oran Berry","Persim Berry","Lum Berry","Sitrus Berry","Figy Berry","Wiki Berry","Mago Berry","Aguav Berry","Iapapa Berry","Razz Berry","Bluk Berry","Nanab Berry","Wepear Berry","Pinap Berry","Pomeg Berry","Kelpsy Berry","Qualot Berry","Hondew Berry","Grepa Berry","Tamato Berry","Cornn Berry","Magost Berry","Rabuta Berry","Nomel Berry","Spelon Berry","Pamtre Berry","Watmel Berry","Durin Berry","Belue Berry","Liechi Berry","Ganlon Berry","Salac Berry","Petaya Berry","Apicot Berry","Lansat Berry","Starf Berry","Enigma Berry","?","?","?","BrightPowder","White Herb","Macho Brace","Exp. Share","Quick Claw","Soothe Bell","Mental Herb","Choice Band","King's Rock","SilverPowder","Amulet Coin","Cleanse Tag","Soul Dew","DeepSeaTooth","DeepSeaScale","Smoke Ball","Everstone","Focus Band","Lucky Egg","Scope Lens","Metal Coat","Leftovers","Dragon Scale","Light Ball","Soft Sand","Hard Stone","Miracle Seed","BlackGlasses","Black Belt","Magnet","Mystic Water","Sharp Beak","Poison Barb","NeverMeltIce","Spell Tag","TwistedSpoon","Charcoal","Dragon Fang","Silk Scarf","Up-Grade","Shell Bell","Sea Incense","Lax Incense","Lucky Punch","Metal Powder","Thick Club","Stick","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","?","Red Scarf","Blue Scarf","Pink Scarf","Green Scarf","Yellow Scarf","Mach Bike","Coin Case","Itemfinder","Old Rod","Good Rod","Super Rod","S.S. Ticket","Contest Pass","?","Wailmer Pail","Devon Goods","Soot Sack","Basement Key","Acro Bike","Pokéblock Case","Letter","Eon Ticket","Red Orb","Blue Orb","Scanner","Go-Goggles","Meteorite","Rm. 1 Key","Rm. 2 Key","Rm. 4 Key","Rm. 6 Key","Storage Key","Root Fossil","Claw Fossil","Devon Scope","TM01","TM02","TM03","TM04","TM05","TM06","TM07","TM08","TM09","TM10","TM11","TM12","TM13","TM14","TM15","TM16","TM17","TM18","TM19","TM20","TM21","TM22","TM23","TM24","TM25","TM26","TM27","TM28","TM29","TM30","TM31","TM32","TM33","TM34","TM35","TM36","TM37","TM38","TM39","TM40","TM41","TM42","TM43","TM44","TM45","TM46","TM47","TM48","TM49","TM50","HM01","HM02","HM03","HM04","HM05","HM06","HM07","HM08","?","?","Oak's Parcel","Poké Flute","Secret Key","Bike Voucher","Gold Teeth","Old Amber","Card Key","Lift Key","Helix Fossil","Dome Fossil","Silph Scope","Bicycle","Town Map","VS Seeker","Fame Checker","TM Case","Berry Pouch","Teachy TV","Tri-Pass","Rainbow Pass","Tea","MysticTicket","AuroraTicket","Powder Jar","Ruby","Sapphire","Magma Emblem","Old Sea Map"]

class PokemonName(Enum):
    Bulbasaur = 1
    Ivysaur = 2
    Venusaur = 3
    Charmander = 4
    Charmeleon = 5
    Charizard = 6
    Squirtle = 7
    Wartortle = 8
    Blastoise = 9
    Caterpie = 10
    Metapod = 11
    Butterfree = 12
    Weedle = 13
    Kakuna = 14
    Beedrill = 15
    Pidgey = 16
    Pidgeotto = 17
    Pidgeot = 18
    Rattata = 19
    Raticate = 20
    Spearow = 21
    Fearow = 22
    Ekans = 23
    Arbok = 24
    Pikachu = 25
    Raichu = 26
    Sandshrew = 27
    Sandslash = 28
    Nidoran_F = 29
    Nidorina = 30
    Nidoqueen = 31
    Nidoran_M = 32
    Nidorino = 33
    Nidoking = 34
    Clefairy = 35
    Clefable = 36
    Vulpix = 37
    Ninetales = 38
    Jigglypuff = 39
    Wigglytuff = 40
    Zubat = 41
    Golbat = 42
    Oddish = 43
    Gloom = 44
    Vileplume = 45
    Paras = 46
    Parasect = 47
    Venonat = 48
    Venomoth = 49
    Diglett = 50
    Dugtrio = 51
    Meowth = 52
    Persian = 53
    Psyduck = 54
    Golduck = 55
    Mankey = 56
    Primeape = 57
    Growlithe = 58
    Arcanine = 59
    Poliwag = 60
    Poliwhirl = 61
    Poliwrath = 62
    Abra = 63
    Kadabra = 64
    Alakazam = 65
    Machop = 66
    Machoke = 67
    Machamp = 68
    Bellsprout = 69
    Weepinbell = 70
    Victreebel = 71
    Tentacool = 72
    Tentacruel = 73
    Geodude = 74
    Graveler = 75
    Golem = 76
    Ponyta = 77
    Rapidash = 78
    Slowpoke = 79
    Slowbro = 80
    Magnemite = 81
    Magneton = 82
    Farfetch_d = 83
    Doduo = 84
    Dodrio = 85
    Seel = 86
    Dewgong = 87
    Grimer = 88
    Muk = 89
    Shellder = 90
    Cloyster = 91
    Gastly = 92
    Haunter = 93
    Gengar = 94
    Onix = 95
    Drowzee = 96
    Hypno = 97
    Krabby = 98
    Kingler = 99
    Voltorb = 100
    Electrode = 101
    Exeggcute = 102
    Exeggutor = 103
    Cubone = 104
    Marowak = 105
    Hitmonlee = 106
    Hitmonchan = 107
    Lickitung = 108
    Koffing = 109
    Weezing = 110
    Rhyhorn = 111
    Rhydon = 112
    Chansey = 113
    Tangela = 114
    Kangaskhan = 115
    Horsea = 116
    Seadra = 117
    Goldeen = 118
    Seaking = 119
    Staryu = 120
    Starmie = 121
    Mr_Mime = 122
    Scyther = 123
    Jynx = 124
    Electabuzz = 125
    Magmar = 126
    Pinsir = 127
    Tauros = 128
    Magikarp = 129
    Gyarados = 130
    Lapras = 131
    Ditto = 132
    Eevee = 133
    Vaporeon = 134
    Jolteon = 135
    Flareon = 136
    Porygon = 137
    Omanyte = 138
    Omastar = 139
    Kabuto = 140
    Kabutops = 141
    Aerodactyl = 142
    Snorlax = 143
    Articuno = 144
    Zapdos = 145
    Moltres = 146
    Dratini = 147
    Dragonair = 148
    Dragonite = 149
    Mewtwo = 150
    Mew = 151
    Chikorita = 152
    Bayleef = 153
    Meganium = 154
    Cyndaquil = 155
    Quilava = 156
    Typhlosion = 157
    Totodile = 158
    Croconaw = 159
    Feraligatr = 160
    Sentret = 161
    Furret = 162
    Hoothoot = 163
    Noctowl = 164
    Ledyba = 165
    Ledian = 166
    Spinarak = 167
    Ariados = 168
    Crobat = 169
    Chinchou = 170
    Lanturn = 171
    Pichu = 172
    Cleffa = 173
    Igglybuff = 174
    Togepi = 175
    Togetic = 176
    Natu = 177
    Xatu = 178
    Mareep = 179
    Flaaffy = 180
    Ampharos = 181
    Bellossom = 182
    Marill = 183
    Azumarill = 184
    Sudowoodo = 185
    Politoed = 186
    Hoppip = 187
    Skiploom = 188
    Jumpluff = 189
    Aipom = 190
    Sunkern = 191
    Sunflora = 192
    Yanma = 193
    Wooper = 194
    Quagsire = 195
    Espeon = 196
    Umbreon = 197
    Murkrow = 198
    Slowking = 199
    Misdreavus = 200
    Unown = 201
    Wobbuffet = 202
    Girafarig = 203
    Pineco = 204
    Forretress = 205
    Dunsparce = 206
    Gligar = 207
    Steelix = 208
    Snubbull = 209
    Granbull = 210
    Qwilfish = 211
    Scizor = 212
    Shuckle = 213
    Heracross = 214
    Sneasel = 215
    Teddiursa = 216
    Ursaring = 217
    Slugma = 218
    Magcargo = 219
    Swinub = 220
    Piloswine = 221
    Corsola = 222
    Remoraid = 223
    Octillery = 224
    Delibird = 225
    Mantine = 226
    Skarmory = 227
    Houndour = 228
    Houndoom = 229
    Kingdra = 230
    Phanpy = 231
    Donphan = 232
    Porygon2 = 233
    Stantler = 234
    Smeargle = 235
    Tyrogue = 236
    Hitmontop = 237
    Smoochum = 238
    Elekid = 239
    Magby = 240
    Miltank = 241
    Blissey = 242
    Raikou = 243
    Entei = 244
    Suicune = 245
    Larvitar = 246
    Pupitar = 247
    Tyranitar = 248
    Lugia = 249
    Ho_Oh = 250
    Celebi = 251
    Treecko = 252
    Grovyle = 253
    Sceptile = 254
    Torchic = 255
    Combusken = 256
    Blaziken = 257
    Mudkip = 258
    Marshtomp = 259
    Swampert = 260
    Poochyena = 261
    Mightyena = 262
    Zigzagoon = 263
    Linoone = 264
    Wurmple = 265
    Silcoon = 266
    Beautifly = 267
    Cascoon = 268
    Dustox = 269
    Lotad = 270
    Lombre = 271
    Ludicolo = 272
    Seedot = 273
    Nuzleaf = 274
    Shiftry = 275
    Taillow = 276
    Swellow = 277
    Wingull = 278
    Pelipper = 279
    Ralts = 280
    Kirlia = 281
    Gardevoir = 282
    Surskit = 283
    Masquerain = 284
    Shroomish = 285
    Breloom = 286
    Slakoth = 287
    Vigoroth = 288
    Slaking = 289
    Nincada = 290
    Ninjask = 291
    Shedinja = 292
    Whismur = 293
    Loudred = 294
    Exploud = 295
    Makuhita = 296
    Hariyama = 297
    Azurill = 298
    Nosepass = 299
    Skitty = 300
    Delcatty = 301
    Sableye = 302
    Mawile = 303
    Aron = 304
    Lairon = 305
    Aggron = 306
    Meditite = 307
    Medicham = 308
    Electrike = 309
    Manectric = 310
    Plusle = 311
    Minun = 312
    Volbeat = 313
    Illumise = 314
    Roselia = 315
    Gulpin = 316
    Swalot = 317
    Carvanha = 318
    Sharpedo = 319
    Wailmer = 320
    Wailord = 321
    Numel = 322
    Camerupt = 323
    Torkoal = 324
    Spoink = 325
    Grumpig = 326
    Spinda = 327
    Trapinch = 328
    Vibrava = 329
    Flygon = 330
    Cacnea = 331
    Cacturne = 332
    Swablu = 333
    Altaria = 334
    Zangoose = 335
    Seviper = 336
    Lunatone = 337
    Solrock = 338
    Barboach = 339
    Whiscash = 340
    Corphish = 341
    Crawdaunt = 342
    Baltoy = 343
    Claydol = 344
    Lileep = 345
    Cradily = 346
    Anorith = 347
    Armaldo = 348
    Feebas = 349
    Milotic = 350
    Castform = 351
    Kecleon = 352
    Shuppet = 353
    Banette = 354
    Duskull = 355
    Dusclops = 356
    Tropius = 357
    Chimecho = 358
    Absol = 359
    Wynaut = 360
    Snorunt = 361
    Glalie = 362
    Spheal = 363
    Sealeo = 364
    Walrein = 365
    Clamperl = 366
    Huntail = 367
    Gorebyss = 368
    Relicanth = 369
    Luvdisc = 370
    Bagon = 371
    Shelgon = 372
    Salamence = 373
    Beldum = 374
    Metang = 375
    Metagross = 376
    Regirock = 377
    Regice = 378
    Registeel = 379
    Latias = 380
    Latios = 381
    Kyogre = 382
    Groudon = 383
    Rayquaza = 384
    Jirachi = 385
    Deoxys = 386

class ExpType(Enum):
    MEDIUM_SLOW = 1
    MEDIUM_FAST = 2
    FAST = 3
    SLOW = 4
    ERRATIC = 5
    FLUCTUATING = 6

# some data that makes up a pokemon is stored in a block of 4 parts
# these parts are stored in 24 permutations
# we want to be able to reorganize these parts so that we can work with them
# [0,3,1,2] means that parts ABCD are stored in the order of ACDB
pokemon_substructure_order_lookup = [[0,1,2,3],[0,1,3,2],[0,2,1,3],[0,3,1,2],[0,2,3,1],[0,3,2,1],[1,0,2,3],[1,0,3,2],[2,0,1,3],[3,0,1,2],[2,0,3,1],[3,0,2,1],[1,2,0,3],[1,3,0,2],[2,1,0,3],[3,1,0,2],[2,3,0,1],[3,2,0,1],[1,2,3,0],[1,3,2,0],[2,1,3,0],[3,1,2,0],[2,3,1,0],[3,2,1,0]]

class pokemon:

    def __init__(self, pokemon_bytes):
        self.bytes_ = pokemon_bytes

    def clear(self):
        self.bytes_ = [0x0] * 80
    
    def is_clear(self):
        if all([x is 0 for x in self.bytes_]):
            return True
        return False

    def __gen_subdata_checksum(self, subdata):
        checksum = 0
        it = iter(subdata)
        for a in it:
            b = next(it)
            value = (b << 8) | a
            checksum = (checksum + value) & 0xFFFF
        return checksum.to_bytes(2, byteorder='little')

    def __xor_subdata(self, key, subdata):
        dest = [0x0] * 48
        for i in range(len(subdata)):
            # saw in pkhex, clever idea
            dest[i] = subdata[i] ^ key[i & 3]
        return dest

    def __make_subdata_messy_again(self, substructure_order, subdata):
        dest = [0x0] * 48
        for i, part in enumerate(substructure_order):
            dest[(part*12) : (part*12)+12] = subdata[(i*12) : (i*12)+12]
        return dest

    def __make_subdata_organized(self, substructure_order, subdata):
        dest = []
        for i in substructure_order:
            temp = subdata[(i*12) : (i*12) + 12]
            dest.extend(temp)
        return dest
    
    def __internal_species_id_to_national_id(self, species_id):
        # index is the internal id, value is the national id
        internal_to_national = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,290,291,292,276,277,285,286,327,278,279,283,284,320,321,300,301,352,343,344,299,324,302,339,340,370,341,342,349,350,318,319,328,329,330,296,297,309,310,322,323,363,364,365,331,332,361,362,337,338,298,325,326,311,312,303,307,308,333,334,360,355,356,315,287,288,289,316,317,357,293,294,295,366,367,368,359,353,354,336,335,369,304,305,306,351,313,314,345,346,347,348,280,281,282,371,372,373,374,375,376,377,378,379,382,383,384,380,381,385,386,358]
        return internal_to_national[species_id]

    def __national_id_to_internal_species_id(self, national_id):
        # index is the national id, value is the internal id
        national_to_internal = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,304,305,309,310,392,393,394,311,312,306,307,364,365,366,301,302,303,370,371,372,335,336,350,320,315,316,322,355,382,383,384,356,357,337,338,353,354,386,387,363,367,368,330,331,313,314,339,340,321,351,352,308,332,333,334,344,345,358,359,380,379,348,349,323,324,326,327,318,319,388,389,390,391,328,329,385,317,377,378,361,362,369,411,376,360,346,347,341,342,343,373,374,375,381,325,395,396,397,398,399,400,401,402,403,407,408,404,405,406,409,410]
        return national_to_internal[national_id]

    def __write_value_to_subdata(self, value, position, size):
        # this function exists because we cannot set a part/slice of a property
        # meaning this won't work: self.__subdata[6] = 0xFF
        # putting subdata in a separate class and using __setitem__ would let us set data like that
        # but then we'd have to keep the bytes of that subdata class up to date with this main pokemon class each time
        # an easy solution is to get all the subdata, edit what we need, and then set it all back
        temp = self.__subdata
        temp[position: position+size] = value.to_bytes(size, byteorder='little')
        self.__subdata = temp

    def hide_secret_data(self, hide_data):
        if len(hide_data) is not 67:
            raise ValueError('Data is not the right size')

        # clear the pokemon so that we start with 0s
        self.clear()

        # places where we store hidden data in the subdata
        # subdata (size is 48 bytes):
        #   2 byte @ subdata[0:2] species id, illegal values are fine if egg
        #   NONE x 2 @ subdata[2:4] held item, illegal for eggs to have an item, shows in pc item mover and in party
        #   16 bytes @ subdata[4:20], subdata section 
        #   NONE x 4 @ subdata[20:24], skipping PP bytes since these get reset on move in box
        #   12 bytes @ subdata[24:36] subdata section
        #   NONE x 1 @ subdata[36:37], pkrs, illegal for eggs to have, it shows up in summary
        #   1 bytes @ subdata[37:38], met location, hidden if egg
        #   1 byte @ subdata[38:40], origins, 2 byte value, use lower byte, upper half contains pokeball used, shows on egg summary. illegal if not a pokeball 
        #   3 bytes @ subdata[40:44], we have 4 bytes but last bit is used for egg flag
        #   4 bytes @ subdata[44:48], ribbons and obedience, hidden if egg
        #   1 byte @ using bits from other values
        # total bytes stored in subdata = 40

        # making the most of data in subdata
        # origins 2 bytes
        # Gender(1) Ball(4) Game(4) Level(7)
        # 0         0000    0000    0000000
        # Rotate the bits, so that the gender bit moves from the highest bit to the lowest
        # (No need to rotate bits to begin with, since we're starting with a 0 value)
        # This gives us 8 bits at the start to work with, then 4 bits, then 4 bits we leave alone
        # Rotate the bits back for storing in the pokemon
        ###
        # egg_iv_abaility 4 bytes
        # 1111 1111 1111 1111 1111 1111 1111 1111
        # ability egg  | ivs                                 |        
        #                        | three bytes using already |
        # 1       1    11 1111   1111 1111 1111 1111 1111 1111
        # only egg is important, another 7 bits we can use

        part_1 = hide_data[0:2]   # species id                      2
        part_2a = hide_data[2:18]  # big section                    16
        part_2b = hide_data[18:30]  # big section                   12
        part_3 = hide_data[30:31] # met location                    1
        part_4 = hide_data[31:32] # origins lower byte              1
        part_5 = hide_data[32:35] # egg_iv_ability lower 3 bytes    3
        part_6 = hide_data[35:39] # ribbons and obedience           4
        part_7 = hide_data[39]    # extra byte we fit in            1
        part_7_upper = (part_7 >> 4) & 0xF
        part_7_lower = part_7 & 0xF
        #
        part_8 = hide_data[40:50]
        part_9 = hide_data[50:57]
        part_10 = hide_data[57:61]
        part_11 = hide_data[61:65]
        part_12 = hide_data[65:67]

        temp = self.__subdata
        temp[0:2] = part_1 # species id
        temp[4:20] = part_2a # big section
        temp[24:36] = part_2b # big section
        temp[37:38] = part_3 # met location
        # for origins, we set part_4 to the lower bytes
        # then part_7_upper to the next 4 bits
        origins_value = int.from_bytes(part_4, byteorder='little')
        origins_value = origins_value | (part_7_upper << 8)
        # Now, rotate bits by 1 so that the lowest is now the highest
        origins_value = (origins_value >> 1) | (origins_value << (16 - 1)) & 0xFFFF
        # set the value
        temp[38:40] = origins_value.to_bytes(2, byteorder='little')

        # part 5
        temp[40:43] = part_5
        # byte's value is 0, so we can just set to value. we set egg flag later on
        temp[43] = part_7_lower
        # part 6
        temp[44:48] = part_6

        self.__subdata = temp
        self.egg = True

        self.bytes_[8:18] = part_8
        self.bytes_[20:27] = part_9
        self.pid = int.from_bytes(part_10, byteorder='little')
        self.otid = int.from_bytes(part_11, byteorder='little')
        self.bytes_[30:32] = part_12
    
    def extract_secret_data(self):
        all_hidden_data = bytearray()

        part_1 = self.__subdata[0:2]   # species id
        part_2a = self.__subdata[4:20]  # big section
        part_2b = self.__subdata[24:36]  # big section
        part_3 = self.__subdata[37:38] # met location
        
        origins_value = int.from_bytes(self.__subdata[38:40], byteorder='little')
        # Rotate the bits, so that the gender bit moves from the highest bit to the lowest
        origins_value = ((origins_value << 1) | (origins_value >> (16-1))) & 0xFFFF
        # set part_4 to the lower byte
        part_4 = origins_value & 0xFF
        part_4 = part_4.to_bytes(1, byteorder='little')
        # set part_7_upper to the next 4 bits after the first byte
        part_7_upper = (origins_value >> 8) & 0xF
        # and the lower part to the lower half of this byte
        part_7_lower = self.__subdata[43] & 0xF
        part_7 = ((part_7_upper << 4) | part_7_lower) & 0xFF
        part_7 = part_7.to_bytes(1, byteorder='little')

        part_5 = self.__subdata[40:43] 
        part_6 = self.__subdata[44:48] 

        # regular pokemon data, not subdata
        part_8 = self.bytes_[8:18]
        part_9 = self.bytes_[20:27]
        part_10 = self.pid.to_bytes(4, byteorder='little')
        part_11 = self.otid.to_bytes(4, byteorder='little')
        part_12 = self.bytes_[30:32]
        
        
        all_hidden_data.extend(part_1)
        all_hidden_data.extend(part_2a)
        all_hidden_data.extend(part_2b)
        all_hidden_data.extend(part_3)
        all_hidden_data.extend(part_4)
        all_hidden_data.extend(part_5)
        all_hidden_data.extend(part_6)
        all_hidden_data.extend(part_7)
        #
        all_hidden_data.extend(part_8)
        all_hidden_data.extend(part_9)
        all_hidden_data.extend(part_10)
        all_hidden_data.extend(part_11)
        all_hidden_data.extend(part_12)

        return all_hidden_data

    @property
    def pid(self):
        return int.from_bytes(self.bytes_[0:4], byteorder='little')
    @pid.setter
    def pid(self, value):
        # subdata encryption and the order of the 4 parts within
        # depends on pid (and otid), so first get the decrypted subdata
        subdata = self.__subdata
        # then change the pid
        self.bytes_[0:4] = value.to_bytes(4, byteorder='little')
        # and then set the same subdata back, now encrypting it with the new key and in the new order
        self.__subdata = subdata

    @property
    def otid(self):
        return int.from_bytes(self.bytes_[4:8], byteorder='little')
    @otid.setter
    def otid(self, value):
        # same idea as when we as change the pid
        subdata = self.__subdata
        self.bytes_[4:8] = value.to_bytes(4, byteorder='little')
        self.__subdata = subdata

    @property
    def __subdata_xor_key_bytes(self):
        return (self.pid ^ self.otid).to_bytes(4, byteorder='little')
    @property
    def __subdata_part_order(self):
        return pokemon_substructure_order_lookup[self.pid % 24]

    @property
    def __subdata(self):
        # take encrypted data which has four parts arranged in a top secret order
        temp = self.bytes_[32:80]
        # decrypt
        temp = self.__xor_subdata(self.__subdata_xor_key_bytes, temp)
        # put subdata parts into standardized order
        return self.__make_subdata_organized(self.__subdata_part_order, temp)

    @__subdata.setter
    def __subdata(self, subdata):
        # encrypt
        temp = self.__xor_subdata(self.__subdata_xor_key_bytes, subdata)
        # arrange subdata parts back in the top secret order
        temp = self.__make_subdata_messy_again(self.__subdata_part_order, temp)
        # set back to pokemon data
        self.bytes_[32:80] = temp
        # recalculate checksum
        self.bytes_[28:30] = self.__gen_subdata_checksum(self.__subdata)

    @property
    def national_dex_id(self):
        internal_species_id = int.from_bytes(self.__subdata[0:2], byteorder='little')
        return self.__internal_species_id_to_national_id(internal_species_id)

    @national_dex_id.setter
    def national_dex_id(self, value):
        # different pokemon level up at different rates
        # most extreme example (I could find) if we don't adjust exp when changing the species:
        # lv 100 Altaria would become a lv 75 Breloom

        # get the current level, and exp needed to get to the next level
        original_level = self.level
        original_exp_to_next_level = self.__exp_to_next_level

        # change pokemon species
        internal_species_id = self.__national_id_to_internal_species_id(value)
        self.__write_value_to_subdata(internal_species_id, 0, 2)

        if original_level == 100:
            self.level = original_level
        else:
            # if we used to be on level 50 with 30 exp until 51
            # set to level 51, then subtract 30 exp so we are level 50
            self.level = original_level + 1
            adjusted_exp = self.exp - original_exp_to_next_level
            # this has issues at lower levels, when the old distance to the
            # next level is higher than the base exp for the level of the new species
            # in that case, we set to the new level only
            if adjusted_exp < 0:
                self.level = original_level
            else:
                self.exp = adjusted_exp
            
            # similar to above, handling some rare cases where 
            # we subtracted enough exp to take us down a level
            if self.level < original_level:
                self.level = original_level

    @property
    def egg(self):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        return (iv_egg_ability >> 30)
    @egg.setter
    def egg(self, set_egg):
        iv_egg_ability = int.from_bytes(self.__subdata[40:44], byteorder='little')
        if set_egg:
            iv_egg_ability = iv_egg_ability | (1 << 30)
            self.bytes_[18:20] = (0x0601).to_bytes(2, byteorder='little')
        else:
            iv_egg_ability = iv_egg_ability & ~(1 << 30)
            self.bytes_[18:20] = (0x0202).to_bytes(2, byteorder='little')
        self.__write_value_to_subdata(iv_egg_ability, 0x28, 4)
    
    @property
    def iv_hp(self):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        # to get the first 5 bits from this 32 bit value, we can & with 0b11111
        # this ensures the maximum value we can is 0b11111
        return iv_egg_ability & 0b11111
    @iv_hp.setter
    def iv_hp(self, value):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        # 1. For the HP IV, our attention is on the last 5 bits (separated for visibility)
        #    111111111111111111111111111_11111
        # 2. First we set these bits to 0:      num = num & ~(0b11111)
        #    0b11111 is 31, all 5 bits set, the maximum value of an IV
        #    We take the inverse of 31 so that we have a value that has all bits set to 1 apart from the last 5
        #    ~(0b11111) = 111111111111111111111111111_00000
        #    Take this and Bitwise AND with our initial value makes it so our value is never bigger than 111111111111111111111111111_00000
        #    Now our value is the same as before, but with the HP IV set to 0
        # 3. Now we can use Bitwise OR to set our desired HP IV:      num = num | hp_iv
        iv_egg_ability &= ~31
        iv_egg_ability |= value
        self.__write_value_to_subdata(iv_egg_ability, 0x28, 4)

    @property
    def iv_atk(self):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        return (iv_egg_ability >> 5) & 0b11111
    @iv_atk.setter
    def iv_atk(self, value):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        iv_egg_ability & ~(31 << 5)
        iv_egg_ability |= (value << 5)
        self.__write_value_to_subdata(iv_egg_ability, 0x28, 4)

    @property
    def iv_def(self):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        return (iv_egg_ability >> 10) & 0b11111
    @iv_def.setter
    def iv_def(self, value):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        iv_egg_ability & ~(31 << 10)
        iv_egg_ability |= (value << 10)
        self.__write_value_to_subdata(iv_egg_ability, 0x28, 4)

    @property
    def iv_spd(self):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        return (iv_egg_ability >> 15) & 0b11111
    @iv_spd.setter
    def iv_spd(self, value):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        iv_egg_ability & ~(31 << 15)
        iv_egg_ability |= (value << 15)
        self.__write_value_to_subdata(iv_egg_ability, 0x28, 4)

    @property
    def iv_spatk(self):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        return (iv_egg_ability >> 20) & 0b11111
    @iv_spatk.setter
    def iv_spatk(self, value):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        iv_egg_ability & ~(31 << 20)
        iv_egg_ability |= (value << 20)
        self.__write_value_to_subdata(iv_egg_ability, 0x28, 4)

    @property
    def iv_spdef(self):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        return (iv_egg_ability >> 25) & 0b11111
    @iv_spdef.setter
    def iv_spdef(self, value):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        iv_egg_ability & ~(31 << 25)
        iv_egg_ability |= (value << 25)
        self.__write_value_to_subdata(iv_egg_ability, 0x28, 4)

    @property
    def iv_list(self):
        return [self.iv_hp, self.iv_atk, self.iv_def, self.iv_spd, self.iv_spatk, self.iv_spdef]
    @iv_list.setter
    def iv_list(self, iv_list):
        if len(iv_list) is not 6:
            raise ValueError('Needs 6 IVs')
        if any([0 < x > 31 for x in iv_list]):
            raise ValueError('IVs must be from 0 to 31')
        [self.iv_hp, self.iv_atk, self.iv_def, self.iv_spd, self.iv_spatk, self.iv_spdef] = iv_list

    @property
    def ev_hp(self):
        return self.__subdata[24]
    @ev_hp.setter
    def ev_hp(self, value):
        self.__write_value_to_subdata(value, 24, 1)
    
    @property
    def ev_atk(self):
        return self.__subdata[25]
    @ev_atk.setter
    def ev_atk(self, value):
        self.__write_value_to_subdata(value, 25, 1)

    @property
    def ev_def(self):
        return self.__subdata[26]
    @ev_def.setter
    def ev_def(self, value):
        self.__write_value_to_subdata(value, 26, 1)
    
    @property
    def ev_spd(self):
        return self.__subdata[27]
    @ev_spd.setter
    def ev_spd(self, value):
        self.__write_value_to_subdata(value, 27, 1)

    @property
    def ev_spatk(self):
        return self.__subdata[28]
    @ev_spatk.setter
    def ev_spatk(self, value):
        self.__write_value_to_subdata(value, 28, 1)
    
    @property
    def ev_spdef(self):
        return self.__subdata[29]
    @ev_spdef.setter
    def ev_spdef(self, value):
        self.__write_value_to_subdata(value, 29, 1)
    
    @property
    def ev_list(self):
        return [self.ev_hp, self.ev_atk, self.ev_def, self.ev_spd, self.ev_spatk, self.ev_spdef]
    @ev_list.setter
    def ev_list(self, ev_list):
        if len(ev_list) is not 6:
            raise ValueError('Needs 6 EVs')
        if any([0 < x > 255 for x in ev_list]):
            raise ValueError('EVs must be from 0 to 255')
        [self.ev_hp, self.ev_atk, self.ev_def, self.ev_spd, self.ev_spatk, self.ev_spdef] = ev_list

    @property
    def ability(self):
        iv_egg_ability = int.from_bytes(self.__subdata[0x28:0x2C], byteorder='little')
        return (iv_egg_ability >> 31) + 1
    @ability.setter
    def ability(self, value):
        if (1 < value > 2):
            raise ValueError('Ability can only be 1 or 2')
        iv_egg_ability = int.from_bytes(self.__subdata[40:44], byteorder='little')
        if value == 2:
            iv_egg_ability = iv_egg_ability | (1 << 31)
        else:
            iv_egg_ability = iv_egg_ability & ~(1 << 31)
        self.__write_value_to_subdata(iv_egg_ability, 40, 4)
    
    @property
    def pokerus_days_left(self):
        pokerus = self.__subdata[36]
        return pokerus & 0xF
    @pokerus_days_left.setter
    def pokerus_days_left(self, value):
        # when setting days left, max days is 4, and only for some strains
        pokerus = self.__subdata[36]
        pokerus = pokerus & ~(0xF)
        pokerus |= value
        self.__write_value_to_subdata(pokerus, 36, 1)

    @property
    def pokerus_strain(self):
        pokerus = self.__subdata[36]
        return pokerus >> 4
    @pokerus_strain.setter
    def pokerus_strain(self, value):
        pokerus = self.__subdata[36]
        pokerus = pokerus & ~(0xF << 4)
        pokerus |= (value << 4)
        self.__write_value_to_subdata(pokerus, 36, 1)
    
    @property
    def pokerus(self):
        if self.pokerus_strain and self.pokerus_days_left:
            return 'Infected'
        elif self.pokerus_strain:
            return 'Cured'
        else:
            return False
    # Might have noticed some issues, will verifiy again later
    # @pokerus_strain.setter
    # def pokerus_strain(self, value):
    #     pokerus = self.__subdata[32]
    #     pokerus = pokerus & ~(0xF << 4)
    #     pokerus |= (value << 4)
    #     temp = self.__subdata
    #     temp[32] = pokerus
    #     self.__subdata = temp

    @property
    def name(self):
        name_bytes = self.bytes_[0x8 : 0x8+10]
        text = ""
        for byte in name_bytes:
            if byte == 0xFF:
                break
            try:
                char = byte2char_dict[byte]
            except:
                char = '?'
            text = text + char
        return text
    
    @name.setter
    def name(self, text):
        if len(text) > 10:
            raise ValueError('Max name length is 10')
        name_bytes = [0xFF] * 10
        for i, char in enumerate(text):
            try:
                this_byte = char2byte_dict[char]
            except:
                this_byte = 0x0
            name_bytes[i] = this_byte
        self.bytes_[0x8 : 0x8+10] = name_bytes

    @property
    def held_item(self):
        return int.from_bytes(self.__subdata[2:4], byteorder='little')
    @held_item.setter
    def held_item(self, value):
        self.__write_value_to_subdata(value, 2, 2)

    @property
    def move_1(self):
        return int.from_bytes(self.__subdata[12:14], byteorder='little')
    @move_1.setter
    def move_1(self, value):
        self.__write_value_to_subdata(value, 12, 2)
    
    @property
    def move_2(self):
        return int.from_bytes(self.__subdata[14:16], byteorder='little')
    @move_2.setter
    def move_2(self, value):
        self.__write_value_to_subdata(value, 14, 2)
    
    @property
    def move_3(self):
        return int.from_bytes(self.__subdata[16:18], byteorder='little')
    @move_3.setter
    def move_3(self, value):
        self.__write_value_to_subdata(value, 16, 2)
    
    @property
    def move_4(self):
        return int.from_bytes(self.__subdata[18:20], byteorder='little')
    @move_4.setter
    def move_4(self, value):
        self.__write_value_to_subdata(value, 18, 2)

    @property
    def move_list(self):
        return [self.move_1, self.move_2, self.move_3, self.move_4]
    @move_list.setter
    def move_list(self, move_list):
        [self.move_1, self.move_2, self.move_3, self.move_4] = move_list

    @property
    def exp(self):
        return int.from_bytes(self.__subdata[4:8], byteorder='little')
    @exp.setter
    def exp(self, value):
        self.__write_value_to_subdata(value, 4, 4)
    
    @property
    def exp_type(self):
        poke_exp_types = [ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.FAST,ExpType.FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.FAST,ExpType.FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.SLOW,ExpType.SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.SLOW,ExpType.SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.SLOW,ExpType.SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.SLOW,ExpType.SLOW,ExpType.FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.SLOW,ExpType.SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.FAST,ExpType.FAST,ExpType.FAST,ExpType.FAST,ExpType.MEDIUM_FAST,ExpType.SLOW,ExpType.SLOW,ExpType.MEDIUM_FAST,ExpType.FAST,ExpType.FAST,ExpType.FAST,ExpType.FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.FAST,ExpType.FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.FAST,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_FAST,ExpType.FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_FAST,ExpType.FAST,ExpType.FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_SLOW,ExpType.SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.SLOW,ExpType.SLOW,ExpType.FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.FAST,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.SLOW,ExpType.FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.SLOW,ExpType.FAST,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.FLUCTUATING,ExpType.FLUCTUATING,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.ERRATIC,ExpType.ERRATIC,ExpType.ERRATIC,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.FLUCTUATING,ExpType.FLUCTUATING,ExpType.FAST,ExpType.MEDIUM_FAST,ExpType.FAST,ExpType.FAST,ExpType.MEDIUM_SLOW,ExpType.FAST,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.SLOW,ExpType.SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.ERRATIC,ExpType.FLUCTUATING,ExpType.MEDIUM_SLOW,ExpType.FLUCTUATING,ExpType.FLUCTUATING,ExpType.SLOW,ExpType.SLOW,ExpType.FLUCTUATING,ExpType.FLUCTUATING,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.FAST,ExpType.FAST,ExpType.FAST,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.ERRATIC,ExpType.ERRATIC,ExpType.ERRATIC,ExpType.FLUCTUATING,ExpType.FAST,ExpType.FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.FLUCTUATING,ExpType.FLUCTUATING,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.ERRATIC,ExpType.ERRATIC,ExpType.ERRATIC,ExpType.ERRATIC,ExpType.ERRATIC,ExpType.ERRATIC,ExpType.MEDIUM_FAST,ExpType.MEDIUM_SLOW,ExpType.FAST,ExpType.FAST,ExpType.FAST,ExpType.FAST,ExpType.SLOW,ExpType.FAST,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_FAST,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.MEDIUM_SLOW,ExpType.ERRATIC,ExpType.ERRATIC,ExpType.ERRATIC,ExpType.SLOW,ExpType.FAST,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW,ExpType.SLOW]
        return poke_exp_types[self.national_dex_id-1]
        
    @property
    def __exp_lookup_table(self):
        erratic_exp_lookup = [0,15,52,122,237,406,637,942,1326,1800,2369,3041,3822,4719,5737,6881,8155,9564,11111,12800,14632,16610,18737,21012,23437,26012,28737,31610,34632,37800,41111,44564,48155,51881,55737,59719,63822,68041,72369,76800,81326,85942,90637,95406,100237,105122,110052,115015,120001,125000,131324,137795,144410,151165,158056,165079,172229,179503,186894,194400,202013,209728,217540,225443,233431,241496,249633,257834,267406,276458,286328,296358,305767,316074,326531,336255,346965,357812,367807,378880,390077,400293,411686,423190,433572,445239,457001,467489,479378,491346,501878,513934,526049,536557,548720,560922,571333,583539,591882,600000]
        fluctuating_exp_lookup = [0,4,13,32,65,112,178,276,393,540,745,967,1230,1591,1957,2457,3046,3732,4526,5440,6482,7666,9003,10506,12187,14060,16140,18439,20974,23760,26811,30146,33780,37731,42017,46656,50653,55969,60505,66560,71677,78533,84277,91998,98415,107069,114205,123863,131766,142500,151222,163105,172697,185807,196322,210739,222231,238036,250562,267840,281456,300293,315059,335544,351520,373744,390991,415050,433631,459620,479600,507617,529063,559209,582187,614566,639146,673863,700115,737280,765275,804997,834809,877201,908905,954084,987754,1035837,1071552,1122660,1160499,1214753,1254796,1312322,1354652,1415577,1460276,1524731,1571884,1640000]
        fast_exp_lookup = [0,6,21,51,100,172,274,409,583,800,1064,1382,1757,2195,2700,3276,3930,4665,5487,6400,7408,8518,9733,11059,12500,14060,15746,17561,19511,21600,23832,26214,28749,31443,34300,37324,40522,43897,47455,51200,55136,59270,63605,68147,72900,77868,83058,88473,94119,100000,106120,112486,119101,125971,133100,140492,148154,156089,164303,172800,181584,190662,200037,209715,219700,229996,240610,251545,262807,274400,286328,298598,311213,324179,337500,351180,365226,379641,394431,409600,425152,441094,457429,474163,491300,508844,526802,545177,563975,583200,602856,622950,643485,664467,685900,707788,730138,752953,776239,800000]
        slow_exp_lookup = [0,10,33,80,156,270,428,640,911,1250,1663,2160,2746,3430,4218,5120,6141,7290,8573,10000,11576,13310,15208,17280,19531,21970,24603,27440,30486,33750,37238,40960,44921,49130,53593,58320,63316,68590,74148,80000,86151,92610,99383,106480,113906,121670,129778,138240,147061,156250,165813,175760,186096,196830,207968,219520,231491,243890,256723,270000,283726,297910,312558,327680,343281,359370,375953,393040,410636,428750,447388,466560,486271,506530,527343,548720,570666,593190,616298,640000,664301,689210,714733,740880,767656,795070,823128,851840,881211,911250,941963,973360,1005446,1038230,1071718,1105920,1140841,1176490,1212873,1250000]
        mediumfast_exp_lookup = [0,8,27,64,125,216,343,512,729,1000,1331,1728,2197,2744,3375,4096,4913,5832,6859,8000,9261,10648,12167,13824,15625,17576,19683,21952,24389,27000,29791,32768,35937,39304,42875,46656,50653,54872,59319,64000,68921,74088,79507,85184,91125,97336,103823,110592,117649,125000,132651,140608,148877,157464,166375,175616,185193,195112,205379,216000,226981,238328,250047,262144,274625,287496,300763,314432,328509,343000,357911,373248,389017,405224,421875,438976,456533,474552,493039,512000,531441,551368,571787,592704,614125,636056,658503,681472,704969,729000,753571,778688,804357,830584,857375,884736,912673,941192,970299,1000000]
        mediumslow_exp_lookup = [0,9,57,96,135,179,236,314,419,560,742,973,1261,1612,2035,2535,3120,3798,4575,5460,6458,7577,8825,10208,11735,13411,15244,17242,19411,21760,24294,27021,29949,33084,36435,40007,43808,47846,52127,56660,61450,66505,71833,77440,83335,89523,96012,102810,109923,117360,125126,133229,141677,150476,159635,169159,179056,189334,199999,211060,222522,234393,246681,259392,272535,286115,300140,314618,329555,344960,360838,377197,394045,411388,429235,447591,466464,485862,505791,526260,547274,568841,590969,613664,636935,660787,685228,710266,735907,762160,789030,816525,844653,873420,902835,932903,963632,995030,1027103,1059860]

        if self.exp_type is ExpType.MEDIUM_SLOW:
            return mediumslow_exp_lookup
        elif self.exp_type is ExpType.MEDIUM_FAST:
            return mediumfast_exp_lookup
        elif self.exp_type is ExpType.FAST:
            return fast_exp_lookup
        elif self.exp_type is ExpType.SLOW:
            return slow_exp_lookup
        elif self.exp_type is ExpType.ERRATIC:
            return erratic_exp_lookup
        elif self.exp_type is ExpType.FLUCTUATING:
            return fluctuating_exp_lookup
    
    @property
    def __exp_to_next_level(self):
        if self.level == 100:
            return 0
        # Level starts at 1 but arrays start at 0, so using level 1 to get the index
        # will return the 2nd element (level 2), the total exp to be at level 2
        next_level_exp =  self.__exp_lookup_table[self.level]
        return next_level_exp - self.exp

    @property
    def level(self):
        # if we have the max exp (or more), we're at level 100
        if self.exp >= self.__exp_lookup_table[-1]:
            # in case exp was above max for exp type, set to max
            if self.exp > self.__exp_lookup_table[-1]:
                self.exp = self.__exp_lookup_table[-1]
            return 100
        
        # Iterate through lookup_table to find the level
        # Ex: lookup table = [0,15,52,...], pokemon's exp = 50
        # We pass over index 0, 1, and stop at 2 since 52 is bigger than 50
        # We return 2 as the level. (level is index+1, can't have level 0!)
        for i, level_exp in enumerate(self.__exp_lookup_table):
            if level_exp > self.exp:
                return i

    @level.setter
    def level(self, level):
        if (1 < level > 100):
            raise ValueError('Level must be from 1 to 100')
        self.exp = self.__exp_lookup_table[level-1]

    def __str__(self):
        indent_size = 4
        print_string = ""
        if self.is_clear():
            print_string += f'{" " * indent_size}-'
        else:
            print_string += f'{" " * indent_size}Name:   {self.name}\n'
            print_string += f'{" " * indent_size}Egg:    {"True" if self.egg else "False"}\n'
            print_string += f'{" " * indent_size}Nat ID: {self.national_dex_id}\n'
            print_string += f'{" " * indent_size}OTID:   {self.otid}\n'
            print_string += f'{" " * indent_size}PID:    {self.pid}\n'
            print_string += f'{" " * indent_size}Abil:   {self.ability}\n'
            print_string += f'{" " * indent_size}IVs:    {self.iv_list}\n'
            print_string += f'{" " * indent_size}EVs:    {self.ev_list}\n'
            print_string += f'{" " * indent_size}Item:   {item_list[self.held_item] if self.held_item > 0 else "None"}\n'
            print_string += f'{" " * indent_size}Moves:  {self.move_list}\n'
            print_string += f'{" " * indent_size}PKRS:   {self.pokerus}'
        return print_string

class save_section:

    def __init__(self, section_bytes):
        self.bytes_ = section_bytes
    
    @property
    def id(self):
        section_id_bytes = self.bytes_[0xff4 : 0xff4 + 0x2]
        return int.from_bytes(section_id_bytes, byteorder='little')
    
    @property
    def index(self):
        section_index_bytes = self.bytes_[0xffc : 0xff4c + 0x4]
        return int.from_bytes(section_index_bytes, byteorder='little') 
    
    # amount of data to use when calculating checksum
    @property
    def size(self):
        section_size_lookup = [0xf2c, 0xf80, 0xf80, 0xf80, 0xf08, 0xf80, 0xf80, 0xf80, 0xf80, 0xf80, 0xf80, 0xf80, 0xf80, 0x7d0]
        return section_size_lookup[self.id]

    # the checksum that currently resides in section
    @property
    def existing_checksum(self):
        section_checksum_bytes = self.bytes_[0xff6 : 0xff6 + 0x2]
        return int.from_bytes(section_checksum_bytes, byteorder='little')

    
    def calculate_checksum(self):
        section_sum = 0
        it = iter(self.bytes_[0:self.size])
        for a in it:
            b = next(it)
            c = next(it)
            d = next(it)
            value = (d << 24) | (c << 16) | (b << 8) | a
            section_sum = (section_sum + value) & 0xFFFFFFFF
        checksum = ((section_sum >> 16) + (section_sum & 0xFFFF)) & 0xFFFF
        return checksum
        
    def fix_checksum(self):
        checksum = self.calculate_checksum()
        self.bytes_[0xff6 : 0xff6 + 0x2] = checksum.to_bytes(2, byteorder='little')
    
    @property
    def valid(self):
        return self.existing_checksum == self.calculate_checksum()

class save_block:

    def __init__(self, save_bytes):
        self.bytes_ = save_bytes
        self.__sections = []

        self.__pc_buffers = {}
        self.box_data = []
        self.pokemon_list = []

        self.__read_sections()
        self.__build_pokemon_list()

    @property
    def valid(self):
        return all([section.valid for section in self.__sections])
    
    @property
    def index(self):
        # a save block doesn't have an index, but we will go through all sections
        # and make sure all indexes are the same, and use that as the index for the block
        check_index = self.__sections[0].index
        if all([check_index == section.index for section in self.__sections]):
            return check_index
        else:
            print('Not all section indexes are equal!')
           
    def __build_pokemon_list(self):
        # saves don't necessarily have the sections in the correct order, 
        # so first we will add box data to a dict and then access it once save is fully parsed
        for section in self.__sections:
            if section.id >= 5:
                self.__pc_buffers[section.id] = section.bytes_[0 : section.size]

        for bank in sorted(self.__pc_buffers.keys()):
            self.box_data.extend(self.__pc_buffers[bank])
        if len(self.box_data) != 33744:
            print(f'Error Box data size!: {len(self.box_data)}')

        box_pokemon_data = self.box_data[0x0004:0x8344]
        # 420 pokemon in the box data, each has 80 bytes
        for i in range(420):
            this_pokemon_bytes = box_pokemon_data[i*80 : (i*80)+80]
            this_pokemon = pokemon(this_pokemon_bytes)
            self.pokemon_list.append(this_pokemon)
        
    def __write_pokemon_list(self):
        pokemon_data = []
        for poke in self.pokemon_list:
            pokemon_data.extend(poke.bytes_)
        # We only replace the actual pokemon data,
        # box names, wallpaper, and current box is left as is
        self.box_data[0x0004:0x8344] = pokemon_data

        box_data_written = 0
        for bank in sorted(self.__pc_buffers.keys()):
            # get the size of the section
            section_size = len(self.__pc_buffers[bank])
            # or probably section_size = section_size_lookup[bank]
            
            # then write the same amount of data from our new data to the buffer
            self.__pc_buffers[bank] = self.box_data[box_data_written : box_data_written+section_size]
            
            # update our iterator
            box_data_written = box_data_written + section_size


    def __read_sections(self):
        for i in range(14):
            section_data = self.bytes_[i*0x1000 : i*0x1000+0x1000]
            this_section = save_section(section_data)
            self.__sections.append( this_section )

    def __rebuild_sections(self):       
        # the only sections we need to manage now are the pokemon box data ones
        # the other sections already contain their data
        for i, section in enumerate(self.__sections):
            if section.id >= 5:
                section.bytes_[0 : section.size] = self.__pc_buffers[section.id]

            section.fix_checksum()
            
            self.bytes_[i*0x1000 : i*0x1000+0x1000] = section.bytes_
   
    def commit(self):
        # build the pc buffer (sections 5 and onwards) from box data
        self.__write_pokemon_list()
        
        # write pc buffers to sections
        # rebuild this class (save_block)'s bytes with all of bytes from each section
        self.__rebuild_sections()

    def hide_secret_data(self, secret_data):
        bytes_per_poke = 67
        needed_pokemon = math.ceil(len(secret_data)/bytes_per_poke)
        if needed_pokemon > len(self.pokemon_list):
            raise ValueError('Not enough room to write this data!')

        # start with last pokemon in last box, work backwards
        pokemon_index = len(self.pokemon_list) - 1
        chunk_size = bytes_per_poke
        for i in range(0, len(secret_data), chunk_size):
            chunk = secret_data[i:i+chunk_size]
            if len(chunk) < chunk_size:
                # padding with 0s, if the final pokemon/chunk needs it
                chunk.extend([0] * (chunk_size - len(chunk)))
            self.pokemon_list[pokemon_index].hide_secret_data(chunk)
            
            # make sure we can read back the same data
            check_chunk = self.pokemon_list[pokemon_index].extract_secret_data()
            for x in range(chunk_size):
                if chunk[x] != check_chunk[x]:
                    raise ValueError('Error: Data returned is not data written.')

            pokemon_index -= 1

    def extract_secret_data(self):
        pokemon_index = len(self.pokemon_list) - 1
        if not self.pokemon_list[pokemon_index].egg:
            raise ValueError('Last pokemon in last box is not an egg.')
        
        extracted_data = bytearray()
        while self.pokemon_list[pokemon_index].egg:
            temp = self.pokemon_list[pokemon_index].extract_secret_data()
            extracted_data.extend(temp)
            pokemon_index -= 1
        return extracted_data
    
    def verify_secret_data(self, secret_data):
        bytes_per_poke = 67
        needed_pokemon = math.ceil(len(secret_data)/bytes_per_poke)
        if needed_pokemon > len(self.pokemon_list):
            raise ValueError('Not enough room to write this data!')

        # start with last pokemon in last box, work backwards
        pokemon_index = len(self.pokemon_list) - 1
        chunk_size = bytes_per_poke
        # flag to store if data is validated OK
        status = True
        for i in range(0, len(secret_data), chunk_size):
            chunk = secret_data[i:i+chunk_size]
            if len(chunk) < chunk_size:
                # padding with 0s, if the final pokemon/chunk needs it
                chunk.extend([0] * (chunk_size - len(chunk)))
           
            # make sure we can read back the same data
            check_chunk = self.pokemon_list[pokemon_index].extract_secret_data()
            for x in range(chunk_size):
                if chunk[x] != check_chunk[x]:
                    status = False
                    # add a debug option that prints this
                    # box = (pokemon_index//30) + 1
                    # cell = (pokemon_index % 30) + 1
                    # print(f'Incorrect Chunk {x} for Pokemon@ Box:{box} Cell:{cell}')
                    # print(f'Expected: {chunk[x]:08b}')
                    # print(f'Found   : {check_chunk[x]:08b}')
            pokemon_index -= 1
        
        return status

    def string_to_names(self, input_string):
        # if we don't have enough pokemon to rename for this text, error
        if len(input_string) > 4200:
            raise ValueError('Input string is too long!')
        
        name_length = 10
        pokemon_index = 0
        for i in range(0, len(input_string), name_length):
            this_name = input_string[i:i+name_length]
            if self.pokemon_list[pokemon_index].is_clear():
                self.pokemon_list[pokemon_index].national_dex_id = 1
            self.pokemon_list[pokemon_index].name = this_name
            pokemon_index += 1


class save:

    def __init__(self, save_bytes):
        self.__bytes = save_bytes
        self.saveA = save_block(self.__bytes[0: 0xE000])
        self.saveB = save_block(self.__bytes[0xE000: 0x1C000])

    @property
    def active_save(self):
        # If saveA is more recent than B
        if self.saveA.index >= self.saveB.index:
            if self.saveA.valid:
                return self.saveA
            elif self.saveB.valid:
                return self.saveB
        else:
            if self.saveB.valid:
                return self.saveB
            elif self.saveA.valid:
                return self.saveA
        raise ValueError('No valid save blocks!')

    @property
    def backup_save(self):
        if self.active_save == self.saveA:
            return self.saveB
        return self.saveA

    def get_bytes(self):
        return self.__bytes
    
    # Call commit method that will trickle down each part of the save
    # and make sure the bytes are up to date, finalizing the save
    def commit(self):
        self.saveA.commit()
        self.saveB.commit()
        self.__bytes[0: 0xE000] = self.saveA.bytes_
        self.__bytes[0xE000: 0x1C000] = self.saveB.bytes_



with open(args.save_path, 'rb') as fh:
    save_data = bytearray(fh.read())
    if len(save_data) != 131072:
        raise ValueError('Save data is the wrong size.')
pokemon_save = save(save_data)


selected_save = pokemon_save.active_save
if args.use_backup_save:
    selected_save = pokemon_save.backup_save

if args.text_to_b64_names:
    b64_bytes = base64.standard_b64encode(bytes(args.text_to_b64_names, 'utf-8'))
    b64_string = b64_bytes.decode('utf-8')
    selected_save.string_to_names(b64_string)

    pokemon_save.commit()
    with open(args.save_path, 'wb') as fh:
        fh.write(pokemon_save.get_bytes())

if args.store:
    with open(args.store, 'rb') as fh:
        secret_data = bytearray(fh.read())

    selected_save.hide_secret_data(secret_data)
    
    pokemon_save.commit()
    with open(args.save_path, 'wb') as fh:
        fh.write(pokemon_save.get_bytes())

if args.extract:
    secret_data = selected_save.extract_secret_data()
    if args.num_bytes_extract:
        secret_data = secret_data[0:int(args.num_bytes_extract)]

    with open(args.extract, 'wb') as fh:
        fh.write(secret_data)

if args.verify:
    with open(args.verify, 'rb') as fh:
        secret_data = bytearray(fh.read())

    success = selected_save.verify_secret_data(secret_data)

    if success:
        print('Data validated OK!')
    else:
        print('Data could not be validated')