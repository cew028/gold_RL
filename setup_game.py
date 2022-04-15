"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
import lzma
import pickle
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
            return CharacterCreator(new_game())
        return None

class CharacterCreator(input_handlers.EventHandler):    
    def __init__(self, engine: Engine):
        super().__init__(engine)
        
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
        ):
            # The player has entered their details but then selected "[N]" when asked to confirm their choices.
            settings.player_name = ""
            settings.player_class = ""
            settings.class_number = -1
            settings.difficulty = ""
            settings.difficulty_number = -1
        elif(
            key == tcod.event.K_y
            and settings.player_name != "" 
            and settings.player_class != "" 
            and settings.difficulty != ""
        ):
            # The player has entered their details and selected "[Y]" when asked to confirm their choices.
            self.engine.message_log.add_message(
                f"Hello and welcome, {settings.player_name}, to the dungeon.", color.welcome_text
            )
            
            # Rolling for stats.
            if settings.difficulty == "Extreme (Easy)":
                self.engine.player.charisma = dice_roller(3,20,1)
                self.engine.player.constitution = dice_roller(3,20,1)
                self.engine.player.dexterity = dice_roller(3,20,1)
                self.engine.player.intelligence = dice_roller(3,20,1)
                self.engine.player.strength = dice_roller(3,20,1)
                self.engine.player.wisdom = dice_roller(3,20,1)
            elif settings.difficulty == "Standard (Medium)":
                self.engine.player.charisma = dice_roller(3,10,2)
                self.engine.player.constitution = dice_roller(3,10,2)
                self.engine.player.dexterity = dice_roller(3,10,2)
                self.engine.player.intelligence = dice_roller(3,10,2)
                self.engine.player.strength = dice_roller(3,10,2)
                self.engine.player.wisdom = dice_roller(3,10,2)
            elif settings.difficulty == "Classic (Hard)":
                self.engine.player.charisma = dice_roller(3,6,3)
                self.engine.player.constitution = dice_roller(3,6,3)
                self.engine.player.dexterity = dice_roller(3,6,3)
                self.engine.player.intelligence = dice_roller(3,6,3)
                self.engine.player.strength = dice_roller(3,6,3)
                self.engine.player.wisdom = dice_roller(3,6,3)

            # Adding items to inventory.
            starting_gold = dice_roller(3,6,3)*10
            gold = copy.deepcopy(entity_factories.gold)
            gold.stack = starting_gold
            gold.parent = self.engine.player.inventory
            self.engine.player.inventory.items.append(gold)
            
            dagger = copy.deepcopy(entity_factories.dagger)
            dagger.parent = self.engine.player.inventory
            self.engine.player.inventory.items.append(dagger)
            self.engine.player.equipment.toggle_equip(dagger, add_message=False)
            
            leather_armor = copy.deepcopy(entity_factories.leather_armor)
            leather_armor.parent = self.engine.player.inventory
            self.engine.player.inventory.items.append(leather_armor)
            self.engine.player.equipment.toggle_equip(leather_armor, add_message=False)
            
            return input_handlers.MainGameEventHandler(self.engine) 
        return super().ev_keydown(event)
    
    def on_render(self, console: tcod.Console) -> None:
        character_creator_console = tcod.Console(console.width, console.height)
        character_creator_console.draw_frame(0, 0, character_creator_console.width, character_creator_console.height)
        character_creator_console.print_box(
            0, 0, character_creator_console.width, 1, "┤Character Creation├", alignment=tcod.CENTER
        )
        
        character_creator_console.print(2, 2, "Name:")
        
        character_creator_console.print(2, 5, "Class:")
        for i, character_class in enumerate(settings.list_of_classes):
            class_key = chr(ord("A") + i)
            
            class_string = f"[{class_key}] {character_class}"
            
            character_creator_console.print(3, 7+i, class_string, fg=color.menu_text)
        character_creator_console.print(7, 7+settings.class_number, settings.player_class, fg=color.gold)
        
        character_creator_console.print(2, 19, "Rolling for stats:")
        for i, text in enumerate(settings.list_of_difficulties):
            difficulty_key = chr(ord("A") + len(settings.list_of_classes) + i)
            
            difficulty_string = f"[{difficulty_key}] {text}"
            
            character_creator_console.print(3, 21+i, difficulty_string, fg=color.menu_text)
        character_creator_console.print(7, 21+settings.difficulty_number, settings.difficulty, fg=color.gold)
        
        character_creator_console.print(2, 26, "Seed:")
        
        if settings.player_name == "":
            settings.player_name = render_functions.ask_for_text(x=8, y=2, console=character_creator_console)
        else:
            character_creator_console.print(8, 2, settings.player_name, fg=color.gold)
        
        # TODO: Manage the seed.
        
        if settings.player_name != "" and settings.player_class != "" and settings.difficulty != "":
            character_creator_console.print(2, 29, "Confirm the above? [Y] or [N]", fg=color.menu_text)

        
        character_creator_console.blit(console, 0, 0,)