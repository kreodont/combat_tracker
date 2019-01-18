from dataclasses import dataclass, field
import typing
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Character:
    id: UUID = field(default_factory=uuid4)
    name: str = 'Noname character'
    strength: int = 0
    relationships: typing.Dict['Character', tuple] = field(default_factory=dict)


if __name__ == '__main__':
    print(Character(name='Kolobok'))
