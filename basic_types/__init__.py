import typing
import datetime
import uuid


class Value(typing.NamedTuple):
    name: str
    id: str
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

    def change(self, *, action_to_perform: 'Action', rollback_function: typing.Callable = None):
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
    id: str
    time: datetime.datetime = datetime.datetime.now()
    name: str = f'Action {id} at {time}'
    previous_value: typing.Optional[Value] = None
    actual_value: typing.Optional[Value] = None
    function: typing.Callable[..., Value] = None
    rollback_function: typing.Callable[..., typing.Any] = None
    short_description: str = f'Changing value from {previous_value} to {actual_value}'
    full_description: str = short_description
    visibility_level: str = 'visible'

    # def change_value(self, *, value: Value, rollback_function):
    #     return change_value(value_to_change=value, action_to_perform=self, rollback_function=rollback_function)


class Effect(typing.NamedTuple):
    name: str
    action: Action
    id: str
    finished: bool = False
    duration_in_seconds: float = float("inf")
    short_description: str = ''
    full_description: str = short_description
    # values: typing.List[Value] = []


class Timer(typing.NamedTuple):
    name: str
    ticks: typing.List[float]
    actions_list: typing.List[Action]
    subscribers: typing.Dict[Effect, dict]

    @property
    def seconds_passed(self):
        return sum(self.ticks) if self.ticks else 0

    def tick(self, *, seconds) -> 'Timer':
        return timer_tick(timer=self, seconds=seconds)

    @staticmethod
    def untick(*, action: Action):
        return timer_untick(action=action)

    def subscribe_effect(self, *, effect: Effect) -> 'Timer':
        return subscribe_effect_to_timer(effect=effect, timer=self)


def change_value(*,
                 value_to_change: Value,
                 action_to_perform: Action,
                 rollback_function: typing.Optional[typing.Callable],
                 ) -> Value:
    # Getting new value by apllying Actions function to the old value
    new_value = value_to_change._replace(value=action_to_perform.function(value_to_change).value)

    # If rollback function is not defined, it will be default: restore the previous state
    if rollback_function is None:
        def default_rollback(v: Value = None) -> Value:
            if not v:
                pass
            old_value = value_to_change
            return old_value

        rollback_function = default_rollback

    fulfilled_action = action_to_perform._replace(
            previous_value=value_to_change,
            actual_value=new_value,
            rollback_function=rollback_function)

    new_value = new_value.append_action_to_sequence(fulfilled_action)
    return new_value


def timer_tick(*, timer: Timer, seconds: float) -> Timer:
    def rollback_function():
        timer.ticks.remove(seconds)
        return timer

    action_id = str(uuid.uuid4())

    action_tick = Action(
            id=action_id,
            name=f'Timer "{timer.name}" changed by {seconds} seconds',
            rollback_function=rollback_function,
            time=datetime.datetime.now())

    timer.actions_list.append(action_tick)
    timer.ticks.append(seconds)
    for effect, start_time_dict in timer.subscribers.copy().items():
        if effect.finished:
            continue
        start_time = start_time_dict['start_time']
        if start_time + effect.duration_in_seconds < timer.seconds_passed:
            del timer.subscribers[effect]
            effect, set_finished_action = set_effect_finished(effect=effect)
            timer.actions_list.append(set_finished_action)
            timer.subscribers[effect] = start_time_dict

    return timer


def timer_untick(*, action: Action) -> Timer:
    timer = action.rollback_function()
    timer.actions_list.remove(action)
    return timer


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
            rolled_back_value = change_value(
                    action_to_perform=a,
                    value_to_change=rolled_back_value,
                    rollback_function=action.function)

    return rolled_back_value


def apply_effect(*,
                 effect: Effect,
                 value: Value,
                 short_description: str = '',
                 full_description: str = '') -> Value:
    if not short_description:
        if effect.short_description:
            short_description = effect.short_description
        else:
            short_description = f'Value {value.name} changed due to effect {effect.name} application'
    if not full_description:
        if effect.full_description:
            full_description = effect.full_description
        else:
            full_description = short_description
    # Effect application consists of 2 actions: effect applied to value and value is changed
    effect_action = effect.action
    effect_action = effect_action._replace(short_description=short_description, full_description=full_description)
    effect = effect._replace(action=effect_action)

    application_action = Action(
            name=f'Effect {effect.name} was applied to value {value.name} (no value changing yet)',
            previous_value=value,
            short_description=short_description,
            full_description=full_description, id=str(uuid.uuid4()))

    value = value.append_action_to_sequence(application_action)
    value = change_value(value_to_change=value, action_to_perform=effect.action, rollback_function=None)
    return value


def unapply_effect(*, effect: Effect, value: Value, rollback_function: typing.Callable) -> Value:
    remove_effect_action = Action(
            name=f'Effect "{effect.name}" removing from value "{value.name}"',
            previous_value=value,
            function=effect.action.rollback_function,
            short_description=f'Removing effect {effect.name} from {value.name}',
            full_description=f'Removing effect {effect.name} from {value.name}', id=str(uuid.uuid4()))
    rollback_action = Action(function=rollback_function, id=str(uuid.uuid4()))
    value = value.append_action_to_sequence(remove_effect_action)
    value = value.change(action_to_perform=rollback_action)
    return value


def subscribe_effect_to_timer(*, effect: Effect, timer: Timer) -> Timer:
    timer.subscribers[effect] = {'start_time': timer.seconds_passed}
    return timer


def set_effect_finished(*, effect: Effect) -> typing.Tuple[Effect, Action]:
    def rollback_function():
        return effect._replace(finished=False)

    set_finished_action = Action(
            id=str(uuid.uuid4()),
            name=f'Effect {effect.name} set finished',
            rollback_function=rollback_function)

    effect = effect._replace(finished=True)

    return effect, set_finished_action


if __name__ == '__main__':
    pass
