"""Catálogo completo: junta criaturas, animales, personajes y objetos en un único registro."""
from src import creatures, people, things, zoo

GROUPS = {
    "originales": list(creatures.CREATURES),
    "animales": list(zoo.ANIMALS),
    "personajes": list(people.PEOPLE),
    "objetos": list(things.THINGS),
}

for _reg, _parts in ((zoo.ANIMALS, zoo.ANIMAL_PARTS), (people.PEOPLE, people.PEOPLE_PARTS),
                     (things.THINGS, things.THING_PARTS)):
    for _name, _obj in _reg.items():
        creatures.CREATURES.setdefault(_name, _obj)
        creatures.PARTS.setdefault(_name, _parts.get(_name, {"body": (0, -300)}))

ALL = creatures.CREATURES
