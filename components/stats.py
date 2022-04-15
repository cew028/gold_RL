from __future__ import annotations

from components.base_component import BaseComponent

class Stats(BaseComponent):
    parent: Actor
    
    def __init__(
        self, 
        charisma: int = 0,
        constitution: int = 0,
        dexterity: int = 0,
        intelligence: int = 0,
        strength: int = 0,
        wisdom: int = 0,
    ):
        self.charisma = charisma
        self.constitution = constitution
        self.dexterity = dexterity
        self.intelligence = intelligence
        self.strength = strength
        self.wisdom = wisdom