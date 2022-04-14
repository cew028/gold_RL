from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import copy
import tcod

import color
import settings

if TYPE_CHECKING:
    from engine import Engine
    from game_map import GameMap

def get_names_at_location(x: int, y:int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""
    
    names = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )
    
    return names.capitalize()

def render_bar(
    console: tcod.Console, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)
    
    console.draw_rect(x=0, y=45, width=total_width, height=1, ch=1, bg=color.bar_empty)
    
    if bar_width > 0:
        console.draw_rect(
            x=0, y=45, width=bar_width, height=1, ch=1, bg=color.bar_filled
        )
        
    console.print(
        x=1, y=45, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text
    )

def render_dungeon_level(
    console: tcod.Console, dungeon_level: int, location: Tuple[int, int]
) -> None:
    """Render the level the player is currently on, at the given location."""
    x, y = location
    
    console.print(x=x, y=y, string=f"Dungeon level: {dungeon_level}")

def render_names_at_mouse_location(
    console: tcod.Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location
    
    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )
    
    console.print(x=x, y=y, string=names_at_mouse_location)
    
def ask_for_text(x: int, y: int, console: tcod.Console) -> str:
    console_copy = copy.copy(console)
    buffer = ""
    while True:
        console_copy.blit(console)
        console.print(x, y, buffer, fg=(255,255,255))
        settings.main_context.present(console)
        for event in tcod.event.wait():
            if isinstance(event, tcod.event.TextInput):
                buffer += event.text
            elif isinstance(event, tcod.event.KeyDown):
                if event.sym in {\
                    tcod.event.KeySym.KP_ENTER, tcod.event.KeySym.RETURN, tcod.event.KeySym.RETURN2
                }:
                    return buffer
                elif event.sym in {tcod.event.KeySym.BACKSPACE, tcod.event.KeySym.KP_BACKSPACE}:
                    buffer = buffer[:-1]
                    console.print(x + len(buffer), y, " ",)
                elif event.sym == tcod.event.KeySym.ESCAPE:
                    return "" 