from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor

class CharacterClass(BaseComponent):
    parent: Actor
    
    def __init__(
        self, 
        character_class: str = "None",
    ):
        self.character_class = character_class