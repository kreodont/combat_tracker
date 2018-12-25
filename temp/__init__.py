import typing
import datetime
import uuid


class Value(typing.NamedTuple):
    name: str
    id: str = uuid.uuid4()
    value: typing.Any = 0
    actions_sequence: typing.List['Action'] = []
    subscribers: list = []
    short_description: str = f'{value}'
    full_description: str = short_description
    children: typing.List['Value'] = []
    parent: typing.Optional['Value'] = None

    def __repr__(self):
        return f'{self.name}: {self.value}'

    def append_action_to_sequence(self, a: 'Action') -> 'Value':
        return self._replace(actions_sequence=self.actions_sequence + [a, ])

    def roll_back_action(self, action_id: str) -> 'Value':
        return roll_back_action(value=self, action_id=action_id)

    def change(self, *, action_to_perform: 'Action', rollback_function: typing.Callable=None):
        return change_value(
                value_to_change=self,
                action_to_perform=action_to_perform,
                rollback_function=rollback_function)

    @property
    def last_action(self):
        if not self.actions_sequence:
            return None
        else:
            return self.actions_sequence[-1]


class Action(typing.NamedTuple):
    id: str = uuid.uuid4()
    time: datetime.datetime = datetime.datetime.now()
    name: str = f'Action {id} at {time}'
    previous_value: typing.Optional[Value] = None
    actual_value: typing.Optional[Value] = None
    function: typing.Callable[..., Value] = None
    rollback_function: typing.Callable[..., Value] = None
    short_description: str = f'Changing value from {previous_value} to {actual_value}'
    full_description: str = short_description
    visibility_level: str = 'visible'

    def change_value(self, *, value: Value, rollback_function=None):
        return change_value(value_to_change=value, action_to_perform=self, rollback_function=rollback_function)


class Effect(typing.NamedTuple):
    name: str
    action: Action
    id: str = uuid.uuid4()
    short_description: str = ''
    full_description: str = short_description
    duration: str = ''
    values: typing.List[Value] = []

    @property
    def applied(self):
        return bool(self.values)

    def apply(self, *, value: Value, short_description: str = '', full_description: str = '') -> Value:
        return apply_effect(
                effect=self, value=value, short_description=short_description, full_description=full_description)


def change_value(*,
                 value_to_change: Value,
                 action_to_perform: Action,
                 rollback_function: typing.Callable=None,
                 ) -> Value:
    new_value = value_to_change._replace(
            value=action_to_perform.function(value_to_change).value,
    )
    if rollback_function is None:
        def defaul_rollback(v: Value = None) -> Value:
            if not v:
                pass
            old_value = value_to_change
            return old_value
        rollback_function = defaul_rollback

    fulfilled_action = action_to_perform._replace(
            previous_value=value_to_change,
            actual_value=new_value,
            rollback_function=rollback_function)

    new_value = new_value.append_action_to_sequence(fulfilled_action)
    # if len(new_value.actions_sequence) > 1:  # if there is going to be 2 or more actions, we should tie them
    #     actions_sequence = new_value.actions_sequence
    #     actions_sequence[-2] = actions_sequence[-2]._replace(next_action=fulfilled_action)
    #     # actions_sequence[-1] = actions_sequence[-1]._replace(previous_action=value_to_change.last_action)
    #     new_value = new_value._replace(actions_sequence=actions_sequence)

    return new_value


def roll_back_action(*, value: Value, action_id: typing.Optional[str] = None) -> Value:
    if not value.actions_sequence:
        return value

    if action_id is None:
        return value.last_action.rollback_function(value)

    matching_actions = [a for a in value.actions_sequence if a.id == action_id]
    if not matching_actions:
        return value

    action = matching_actions[0]
    action_number = value.actions_sequence.index(action)
    rolled_back_value = action.rollback_function(value)
    if action_number < len(value.actions_sequence):  # Not the last action, need to repeat all following
        actions_to_repeat = [a for a in value.actions_sequence[action_number + 1:]]
        for a in actions_to_repeat:
            rolled_back_value = a.change_value(value=rolled_back_value)

    return rolled_back_value


def apply_effect(*, effect: Effect, value: Value, short_description: str = '', full_description: str = '') -> Value:
    if not short_description:
        if effect.short_description:
            short_description = effect.short_description
        else:
            short_description = f'Effect "{effect.name}" was applied to value "{value.name}"'
    if not full_description:
        if effect.full_description:
            full_description = effect.full_description
        else:
            full_description = short_description
    effect_action = effect.action
    application_action = Action(
            name='Effect application',
            previous_value=value,
            short_description=short_description,
            full_description=full_description)

    value = value.append_action_to_sequence(application_action)
    effect_action = effect_action._replace(short_description=short_description, full_description=full_description)
    effect = effect._replace(action=effect_action)
    value = effect.action.change_value(value=value)
    return value


# def unapply_effect(*, effect: Effect, value: Value):
#     effect_action = effect.action


if __name__ == '__main__':
    pass
