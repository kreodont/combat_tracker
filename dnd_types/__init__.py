from basic_types import Action, Formula, Value
import typing
from dataclasses import dataclass, field, replace
from uuid import uuid4, UUID


def default_main_action() -> Action:
    return Action(name=f'Action roll performed')


@dataclass(frozen=True)
class Roll:
    formula: Formula
    type: str
    name: str = 'Noname roll'
    main_action: Action = field(default_factory=default_main_action)
    id: UUID = field(default_factory=uuid4)
    dependent_actions: typing.List[Action] = field(default_factory=list, hash=False)
    short_description: str = 'Roll without a short description'
    long_description: str = 'Roll without a long description'

    def __post_init__(self):
        if not self.dependent_actions:
            self.dependent_actions.extend(self.formula.parse())

    def cancel(self) -> 'Roll':
        cancelled_actions_list = []
        for a in self.dependent_actions:
            cancelled_actions_list.append(replace(a,
                                                  name=f'Action {self.name} cancelled',
                                                  previous_value=a.actual_value,
                                                  actual_value=a.previous_value))
        cancelled_roll = replace(self,
                                 name=f'Roll {self.name} cancelled',
                                 dependent_actions=cancelled_actions_list)
        return cancelled_roll

    def cancel_single_throw(self, *, throw_number: int) -> 'Roll':
        if len(self.dependent_actions) <= throw_number:
            return self
        action_to_cancel = self.dependent_actions[throw_number]
        action_to_cancel = replace(action_to_cancel,
                                   actual_value=action_to_cancel.previous_value,
                                   previous_value=action_to_cancel.actual_value)

        new_actions_list = self.dependent_actions
        new_actions_list[throw_number] = action_to_cancel
        return replace(self, dependent_actions=new_actions_list)

    def manual_set_value(self, *, manual_value: int) -> 'Roll':
        manual_value_action = Action(actual_value=Value(value=manual_value), previous_value=Value(value=0))
        previous_actions_list = []
        for a in self.dependent_actions:
            previous_actions_list.append(replace(a, previous_value=a.actual_value, actual_value=Value(value=0)))
        return replace(self, dependent_actions=previous_actions_list + [manual_value_action, ])

    @property
    def value(self):
        return sum((a.actual_value.value for a in self.dependent_actions))

    @property
    def previous_value(self):
        return sum((a.previous_value.value for a in self.dependent_actions))


@dataclass(frozen=TabError)
class Rule:
    check_function: typing.Callable[..., typing.Tuple[bool, str]]
    name: str = 'Noname rule'
    id: UUID = field(default_factory=uuid4)
    description = 'No description'
    source = 'Source not defined'
