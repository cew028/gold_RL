from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor

class Stats(BaseComponent):
    parent: Actor
    
    def __init__(
        self, 
        charisma: int = 10,
        constitution: int = 10,
        dexterity: int = 10,
        intelligence: int = 10,
        strength: int = 10,
        wisdom: int = 10,
    ):
        self.charisma = charisma
        self.constitution = constitution
        self.dexterity = dexterity
        self.intelligence = intelligence
        self.strength = strength
        self.wisdom = wisdom