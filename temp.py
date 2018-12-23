import typing


class Value(typing.NamedTuple):
    name: str
    id: str
    value: typing.Any
    actions_sequence: list
    subscribers: list


class Action(typing.NamedTuple):
    name: str
    id: str
    previous_value: Value
    actual_value: Value
    previous_action: 'Action'
    next_action: 'Action'
    visibility_level: int
