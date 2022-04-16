"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
import lzma
import pickle
import random
import traceback
from typing import Optional

import tcod

import color
from dice_roller import dice_roller
from engine import Engine
import entity_factories
from game_map import GameWorld
import input_handlers
import render_functions
import settings

# Load the background image and remove the alpha channel.
background_image = tcod.image.load("menu_background.png")[:, :, :3]

def new_game() -> Engine:
    """Return a brand new game session as an Engine instance."""
    map_width = 80
    map_height = 43
    
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    
    player = copy.deepcopy(entity_factories.player)
    player.name = settings.player_name
    player.character_class = settings.player_class
    
    engine = Engine(player=player)
    
    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
    )
    
    engine.game_world.generate_floor()
    engine.update_fov()
    
    engine.message_log.add_message(
        f"Hello and welcome, {player.name}, to the dungeon.", color.welcome_text
    )
    
    # Rolling for stats.
    if settings.difficulty == "Extreme (Easy)":
        # Extreme generates stats via 3d20k1.
        engine.player.charisma = dice_roller(3,20,1)
        engine.player.constitution = dice_roller(3,20,1)
        engine.player.dexterity = dice_roller(3,20,1)
        engine.player.intelligence = dice_roller(3,20,1)
        engine.player.strength = dice_roller(3,20,1)
        engine.player.wisdom = dice_roller(3,20,1)
    elif settings.difficulty == "Standard (Medium)":
        # Standard generates stats via 3d10k2.
        engine.player.charisma = dice_roller(3,10,2)
        engine.player.constitution = dice_roller(3,10,2)
        engine.player.dexterity = dice_roller(3,10,2)
        engine.player.intelligence = dice_roller(3,10,2)
        engine.player.strength = dice_roller(3,10,2)
        engine.player.wisdom = dice_roller(3,10,2)
    elif settings.difficulty == "Classic (Hard)":
        # Classic generates stats via 3d6.
        engine.player.charisma = dice_roller(3,6,3)
        engine.player.constitution = dice_roller(3,6,3)
        engine.player.dexterity = dice_roller(3,6,3)
        engine.player.intelligence = dice_roller(3,6,3)
        engine.player.strength = dice_roller(3,6,3)
        engine.player.wisdom = dice_roller(3,6,3)

    # Adding items to inventory.    
    # Gold:
    starting_gold = dice_roller(3,6,3)*10
    gold = copy.deepcopy(entity_factories.gold)
    gold.stack = starting_gold
    gold.parent = engine.player.inventory
    engine.player.inventory.items.append(gold)
    
    # Starting weapon:
    dagger = copy.deepcopy(entity_factories.dagger)
    dagger.parent = engine.player.inventory
    engine.player.inventory.items.append(dagger)
    engine.player.equipment.toggle_equip(dagger, add_message=False)
    
    # Starting armor:
    leather_armor = copy.deepcopy(entity_factories.leather_armor)
    leather_armor.parent = engine.player.inventory
    engine.player.inventory.items.append(leather_armor)
    engine.player.equipment.toggle_equip(leather_armor, add_message=False)
    return engine

def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine

class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""
    def on_render(self, console: tcod.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)
        
        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "GOLD",
            fg=color.menu_title,
            alignment=tcod.CENTER,
        )
        console.print(
            console.width // 2,
            console.height // 2,
            "By Eric",
            fg=color.menu_title,
            alignment=tcod.CENTER,
        )
        
        menu_width = 24
        for i, text in enumerate(
            ["[N] Play a new game", "[C] Continue last game", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),
            )
    
    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.K_q, tcod.event.K_ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.K_c:
            try:
                return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc() # Print to stderr.
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.K_n:
            return CharacterCreator()
        return None

class CharacterCreator(input_handlers.BaseEventHandler):
    """Handle the character creation (name, class, difficulty, world seed) rendering and input."""
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        key = event.sym
        index = key - tcod.event.K_a
        
        if 0 <= index < len(settings.list_of_classes) and settings.player_class == "":
            # Detecting the keypress that selects the player's class.
            settings.class_number = index
            settings.player_class = settings.list_of_classes[settings.class_number]
        elif len(settings.list_of_classes) <= index < len(settings.list_of_classes)+len(settings.list_of_difficulties) and settings.difficulty == "":
            # Detecting the keypress that selects the player's difficulty level. 
            # Offset by the number of classes so that alphabetically it picks up where the last list left off.
            settings.difficulty_number = index - len(settings.list_of_classes)
            settings.difficulty = settings.list_of_difficulties[settings.difficulty_number]
        elif(
            key == tcod.event.K_n 
            and settings.player_name != "" 
            and settings.player_class != "" 
            and settings.difficulty != ""
            and settings.seed != ""
        ):
            # The player has entered their details but then selected "[N]" when asked to confirm their choices.
            # This resets all the choices back to the default and the player must select again.
            settings.player_name = ""
            settings.player_class = ""
            settings.class_number = -1
            settings.difficulty = ""
            settings.difficulty_number = -1
            settings.seed = ""
        elif(
            key == tcod.event.K_y
            and settings.player_name != "" 
            and settings.player_class != "" 
            and settings.difficulty != ""
            and settings.seed != ""
        ):
            # The player has entered their details and selected "[Y]" when asked to confirm their choices.
            # This generates the game.
            return input_handlers.MainGameEventHandler(new_game()) 
        return None
    
    def on_render(self, console: tcod.Console) -> None:
        # First, draw a window-sized border.
        console.draw_frame(0, 0, console.width, console.height)
        console.print_box(
            0, 0, console.width, 1, "┤Character Creation├", alignment=tcod.CENTER
        )
        
        console.print(2, 2, "Name:")
        
        console.print(2, 5, "Class:")
        for i, character_class in enumerate(settings.list_of_classes):
            # Draw "[letter] character_class" for each class in list_of_classes.
            # This is maleable to more or fewer classes (though for now there's just 10 classes.)
            class_key = chr(ord("A") + i)
            
            class_string = f"[{class_key}] {character_class}"
            
            console.print(3, 7+i, class_string, fg=color.menu_text)
        console.print(7, 7+settings.class_number, settings.player_class, fg=color.gold) # When the class has been chosen, this highlights it gold.
        
        console.print(2, 19, "Rolling for stats:")
        for i, text in enumerate(settings.list_of_difficulties):
            # Draw "[letter] difficulty" for each choice in list_of_difficulties.
            # The letters start where they left off from the list_of_classes above.
            # Like above, this is flexible for having more or fewer difficulty settings.
            difficulty_key = chr(ord("A") + len(settings.list_of_classes) + i)
            
            difficulty_string = f"[{difficulty_key}] {text}"
            
            console.print(3, 21+i, difficulty_string, fg=color.menu_text)
        console.print(7, 21+settings.difficulty_number, settings.difficulty, fg=color.gold) # When the difficulty has been chosen, this highlights it gold.
        
        if settings.player_name == "":
            settings.player_name = render_functions.ask_for_text(x=8, y=2, console=console)
        else:
            console.print(8, 2, settings.player_name, fg=color.gold) # When the name has been entered, this highlights it gold.
        
        if settings.player_class != "" and settings.difficulty != "":
            console.print(2, 26, "Seed:")
            if settings.seed == "":
                settings.seed = render_functions.ask_for_text(x=8, y=26, console=console)
            else:
                console.print(8, 26, settings.seed, fg=color.gold) # When the seed has been entered, this highlights it gold.
        
        random.seed(settings.seed) 
        
        if settings.player_name != "" and settings.player_class != "" and settings.difficulty != "":
            console.print(2, 29, "Confirm the above? [Y] or [N]", fg=color.menu_text)

        console.blit(console, 0, 0,)