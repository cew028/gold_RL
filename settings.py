import tcod

# The context (as I understand it, the window)
screen_width = 80
screen_height = 50

tileset = tcod.tileset.load_tilesheet(
    "tileset.png", 32, 8, tcod.tileset.CHARMAP_TCOD
)

main_context = tcod.context.new_terminal(
    screen_width,
    screen_height,
    tileset=tileset,
    title="GOLD",
    vsync=True,
)

# Character information
player_name = ""
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
class_number = -1
list_of_difficulties = [
    "Extreme (Easy)",
    "Standard (Medium)",
    "Classic (Hard)"
]
difficulty = ""
difficulty_number = -1