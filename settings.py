import tcod

# The seed
# --------
seed = ""

# The context (as I understand it, the window)
# --------------------------------------------
screen_width = 80
screen_height = 50

tileset = tcod.tileset.load_tilesheet(
    "tileset.png", # path
    16, # the number of columns
    16, # the number of rows
    tcod.tileset.CHARMAP_CP437 # charmap
)

main_context = tcod.context.new_terminal(
    screen_width,
    screen_height,
    tileset=tileset,
    title="GOLD",
    vsync=True,
)

# Character information
# ---------------------
player_name = "" 
# player_name should only be grabbed during character creation. 
# Afterwards, always use "player.name".
# We need this because we create a player name before we have a player object to hold its name.
list_of_classes = [
    "Cleric", 
    "Druid", 
    "Dwarf", 
    "Elf", 
    "Fighter", 
    "Halfling", 
    "Magic-User", 
    "Paladin", 
    "Ranger", 
    "Warlock"
]
player_class = "" 
# player_class should only be grabbed during character creation. 
# Afterwards, always use "player.combat_class".
# We need this because we create a player class before we have a player object to hold its class.
class_number = -1
list_of_difficulties = [
    "Extreme (Easy)", 
    "Standard (Medium)", 
    "Classic (Hard)" 
]
difficulty = ""
difficulty_number = -1

# Controls
# --------