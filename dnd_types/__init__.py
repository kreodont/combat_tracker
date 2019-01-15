from basic_types import Formula, Action
import typing
from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class Attack:
    name: str
    id: str
    formula: Formula
    short_description: str = 'Attack without a short description'
    long_description: str = 'Attack without a long description'

    def roll(self) -> 'Roll':
        roll_object = Roll(
                name=f'Roll for attack "{self.name}"',
                id=str(uuid4()),
                main_action=Action(
                        id=str(uuid4()),
                        name=f'Main action for roll for attack {self.name}'),
                dependent_actions=self.formula.parse()

        )
        return roll_object


@dataclass(frozen=True)
class Roll:
    name: str
    id: str
    main_action: Action
    dependent_actions: typing.List[Action]
    short_description: str = 'Roll without a short description'
    long_description: str = 'Roll without a long description'

    @property
    def value(self):
        return sum((a.actual_value.value for a in self.dependent_actions))
