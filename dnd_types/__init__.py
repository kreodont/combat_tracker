from basic_types import Action, Formula
import typing
from dataclasses import dataclass, field
from uuid import uuid4, UUID


# @dataclass(frozen=True)
# class Attack:
#     name: str
#     id: str
#     formula: Formula
#     short_description: str = 'Attack without a short description'
#     long_description: str = 'Attack without a long description'
#
#     def roll(self) -> 'Roll':
#         roll_object = Roll(
#                 name=f'Roll for attack "{self.name}"',
#                 id=str(uuid4()),
#                 main_action=Action(
#                         id=str(uuid4()),
#                         name=f'Main action for roll for attack {self.name}'),
#                 dependent_actions=self.formula.parse(),
#                 type='attack'
#
#         )
#         return roll_object


@dataclass(frozen=True)
class Roll:
    name: str
    formula: Formula
    main_action: Action
    type: str
    id: UUID = field(default_factory=uuid4)
    dependent_actions: typing.List[Action] = field(default_factory=list, hash=False)
    short_description: str = 'Roll without a short description'
    long_description: str = 'Roll without a long description'

    def __post_init__(self):
        self.dependent_actions.extend(self.formula.parse())

    @property
    def value(self):
        return sum((a.actual_value.value for a in self.dependent_actions))
