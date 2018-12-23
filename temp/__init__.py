import typing
import datetime


class Value(typing.NamedTuple):
    name: str
    id: str
    value: typing.Any = 0
    actions_sequence: list = []
    subscribers: list = []
    short_description: str = f'{value}'
    full_description: str = short_description
    children: typing.List['Value'] = []
    parent: typing.Optional['Value'] = None

    def __repr__(self):
        return f'{self.name}: {self.value}'


class Action(typing.NamedTuple):
    name: str
    id: str
    time: datetime.datetime = datetime.datetime.now()
    previous_value: typing.Optional[Value] = None
    actual_value: typing.Optional[Value] = None
    function: typing.Callable = lambda x: x
    rollback: typing.Callable = lambda x: x
    short_description: str = f'Changing value from {previous_value} to {actual_value}'
    full_description: str = short_description
    visibility_level: str = 'visible'
    next_action: typing.Optional['Action'] = None
    previous_action: typing.Optional['Action'] = None


def change_value(value: Value, action: Action):
    value.actions_sequence.append(action)
    action.function()


def roll_back_action(value: Value, action_id: typing.Optional[str] = None):
    if not value.actions_sequence:
        raise Exception(f'Value {value} action {action_id} was tried to rollback, '
                        f'but there were no actions in this value')
