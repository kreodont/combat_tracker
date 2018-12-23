import typing
import datetime
import uuid


class Value(typing.NamedTuple):
    name: str
    id: str = uuid.uuid4()
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
    id: str = uuid.uuid4()
    time: datetime.datetime = datetime.datetime.now()
    name: str = f'Action {id} at {time}'
    previous_value: typing.Optional[Value] = None
    actual_value: typing.Optional[Value] = None
    function: typing.Callable[..., Value] = None
    rollback: typing.Callable[..., Value] = None
    short_description: str = f'Changing value from {previous_value} to {actual_value}'
    full_description: str = short_description
    visibility_level: str = 'visible'
    next_action: typing.Optional['Action'] = None
    previous_action: typing.Optional['Action'] = None

    # def change_value(self, value: Value):
    #     return change_value(value, self)


def change_value(value_to_change: Value, action_to_perform: Action):
    new_actions_list = value_to_change.actions_sequence + [action_to_perform]
    value_to_change = value_to_change._replace(actions_sequence=new_actions_list)
    action_to_perform = action_to_perform._replace(
            previous_value=value_to_change.value,
            actual_value=action_to_perform.function(value_to_change))
    return action_to_perform


def roll_back_action(value: Value, action_id: typing.Optional[str] = None):
    if not value.actions_sequence:
        raise Exception(f'Value {value} action {action_id} was tried to rollback, '
                        f'but there were no actions in this value')


if __name__ == '__main__':
    pass
