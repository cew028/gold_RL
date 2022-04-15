from __future__ import annotations

import random

def dice_roller(number: int, size: int, keep: int) -> int:
    """Rolls 'number' d 'size', and keeps the highest 'keep'. 
    If 'keep' is larger than or equal to 'number', all the dice are kept.
    Returns the sum of the remaining dice."""
    rolls = []
    for i in range(0, number):
        rolls.append(random.randint(1, size)) # Creates a list of dice rolls.
    rolls.sort() # Sorts them from smallest to largest.
    for i in range(keep, number):
        rolls = rolls[1:] # One at a time removes the smallest entry in the list.
    return sum(rolls)
