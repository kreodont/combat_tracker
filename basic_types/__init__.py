import typing
import datetime
from uuid import uuid4, UUID
import random
from dataclasses import dataclass, replace, field
from formula_parser import parse_formula_string


@dataclass(frozen=True)
class Value:
    value: typing.Any
    name: str = 'Noname value'
    id: UUID = field(default_factory=uuid4)
    actions_sequence: typing.Tuple['Action', ...] = ()
    subscribers: list = ()
    short_description: str = 'No short description'
    full_description: str = 'No full description'
    children: typing.List['Value'] = ()
    parent: typing.Optional['Value'] = None

    # def __repr__(self):
    #     return f'{self.name}: {self.value}'

    def append_action_to_sequence(self, a: 'Action') -> 'Value':
        return replace(self, actions_sequence=self.actions_sequence + (a,))
        # return self._replace(actions_sequence=self.actions_sequence + (a, ))

    @property
    def last_action(self):
        if not self.actions_sequence:
            return None
        else:
            return self.actions_sequence[-1]


@dataclass(frozen=True)
class Action:
    id: UUID = field(default_factory=uuid4)
    time: datetime.datetime = field(default_factory=datetime.datetime.now)
    duration_in_seconds: float = 0
    name: str = f'Noname action'
    previous_value: typing.Optional[Value] = None
    actual_value: typing.Optional[Value] = None
    function: typing.Optional[typing.Callable] = None
    rollback_function: typing.Optional[typing.Callable] = None
    short_description: str = f'No short description'
    full_description: str = f'No full description'
    visibility_level: str = 'visible'


@dataclass(frozen=True)
class Effect:
    """
    Effect is an Action that has a duration
    """
    name: str
    action: Action
    id: UUID = field(default_factory=uuid4)
    finished: bool = False
    duration_in_seconds: float = float("inf")
    short_description: str = 'No short description for effect'
    full_description: str = 'No full description for effect'

    # values: typing.List[Value] = []

    def get_value(self):
        if self.finished:
            return self.action.previous_value
        return self.action.actual_value


@dataclass(frozen=True)
class Timer:
    name: str = 'Noname timer'
    ticks: typing.Tuple[float, ...] = field(default_factory=tuple)
    # actions_list: typing.List[Action] = field(default_factory=tuple)
    subscribed_effects_dict: typing.Dict[Effect, dict] = field(default_factory=dict)

    @property
    def seconds_passed(self):
        return sum(self.ticks) if self.ticks else 0

    @staticmethod
    def untick(*, action: Action):
        return timer_untick(action=action)

    def find_effect_by_id(self, *, effect_id) -> typing.Optional[Effect]:
        matching_effects = [e for e in self.subscribed_effects_dict.keys() if e.id == effect_id]
        if not matching_effects:
            return None
        return matching_effects[0]


@dataclass(frozen=True)
class Formula:
    """
    Special value with random part i.e. 6d20 + 10
    """
    text_representation: str
    name: str = 'Noname formula'
    id: UUID = field(default_factory=uuid4)

    def parse(self) -> typing.List[Action]:
        lex_tokens = parse_formula_string(self.text_representation)
        actions_list = []
        is_negative = False
        token_number = 0
        for lex in lex_tokens:
            token_number += 1
            lex_type, lex_value = getattr(lex, 'type'), getattr(lex, 'value')
            if lex_type == 'sign':
                if lex_value == '-':
                    is_negative = True
                elif lex_value == '+':
                    is_negative = False

            elif lex_type == 'number':
                numeric_value = float(lex_value)
                if is_negative:
                    numeric_value = -numeric_value
                number_action = Action(
                        name=f'Action for token {token_number} from formula [{self.text_representation}]',
                        actual_value=Value(
                                name=f'Current value for token {token_number} from '
                                f'formula [{self.text_representation}]',
                                value=numeric_value),
                        previous_value=Value(
                                name=f'Previous value for token {token_number} from '
                                f'formula [{self.text_representation}]',
                                value=0)
                )
                actions_list.append(number_action)

            elif lex_type == 'dice':
                lex_value = lex_value.replace('к', 'd').replace('д', 'd')
                dice_quantity, dice_max = lex_value.split('d')
                if not dice_quantity:
                    dice_quantity = 1
                else:
                    dice_quantity = int(dice_quantity)
                dice_max = int(dice_max)
                if dice_max < 0:
                    raise ValueError('Dice max must be >= 0')
                if dice_max == 0:
                    dice_min = 0
                else:
                    dice_min = 1
                for dice_number in range(1, dice_quantity + 1):
                    dice_throw = DiceThrow(
                            minimal_possible_value=dice_min,
                            maximal_possible_value=dice_max,
                            name=f'Dice d{dice_max} throw {dice_number} for token {token_number} for '
                            f'formula [{self.text_representation}]',
                            is_negative=is_negative)
                    throwing_action = dice_throw.throw()
                    actions_list.append(throwing_action)

        return actions_list


@dataclass(frozen=True)
class DiceThrow:
    minimal_possible_value: int
    maximal_possible_value: int
    name: str = 'Noname dice throw'
    id: UUID = field(default_factory=uuid4)
    is_negative: bool = False

    def throw(self) -> Action:
        result = random.randint(self.minimal_possible_value, self.maximal_possible_value)
        if self.is_negative:
            result = -result

        throwing_action = Action(
                name=f'Action for DiceThrow "{self.name}"',
                time=datetime.datetime.now(),
                previous_value=Value(name=f'Previous value for DiceThrow is zero', value=0),
                actual_value=Value(name=f'Throw value', value=result)
        )
        return throwing_action

    def several_throws(self, number: int) -> typing.List[Action]:
        actions = []
        for _ in range(number):
            actions.append(self.throw())
        return actions


def change_value(*,
                 value_to_change: Value,
                 changing_function: typing.Optional[typing.Callable[[Value, ], Value]] = None,
                 rollback_function: typing.Optional[typing.Callable[[Value, ], Value]] = None,
                 change_name: str = ''
                 ) -> Action:
    # Getting changing action by apllying changing function to the old value

    # If changing action is None, return zero action
    if changing_function is None:
        return Action(
                actual_value=value_to_change,
                previous_value=value_to_change,
                function=changing_function,
                rollback_function=rollback_function)

    new_value = replace(value_to_change, value=changing_function(value_to_change).value)
    # new_value = value_to_change._replace(value=action_to_perform.function(value_to_change).value)

    # If rollback function is not defined, it will be default: restore the previous state
    if rollback_function is None:
        def default_rollback(v: Value = None) -> Value:
            if not v:
                pass
            old_value = value_to_change
            return old_value

        rollback_function = default_rollback
    if change_name == '':
        change_name = f'Changing value {value_to_change.name} from {value_to_change.value} to {new_value.value}'
    changing_action = Action(
            actual_value=new_value,
            previous_value=value_to_change,
            name=change_name,
            rollback_function=rollback_function)

    # fulfilled_action = action_to_perform._replace(
    #         previous_value=value_to_change,
    #         actual_value=new_value,
    #         rollback_function=rollback_function)

    new_value = new_value.append_action_to_sequence(changing_action)
    changing_action = replace(changing_action, actual_value=new_value)
    return changing_action


def timer_tick(*, timer: Timer, seconds: float) -> Action:
    new_ticks = timer.ticks + (seconds, )
    new_timer = replace(timer, ticks=new_ticks)
    # ticking_action = change_value(
    #         value_to_change=Value(value=timer),
    #         changing_function=lambda x: replace(x, ticks=new_ticks))

    for effect, start_time_dict in new_timer.subscribed_effects_dict.copy().items():
        if effect.finished:
            continue
        start_time = start_time_dict['start_time']
        # If it is time for effect to finish
        if start_time + effect.duration_in_seconds <= new_timer.seconds_passed:
            del new_timer.subscribed_effects_dict[effect]  # unsubscribe effect
            finished_effect, set_finished_action = set_effect_finished(effect=effect)
            new_timer.subscribed_effects_dict[finished_effect] = start_time_dict

    ticking_action = Action(
            name=f'Timer {timer.name} ticks on {seconds} seconds',
            previous_value=Value(value=timer),
            actual_value=Value(value=new_timer))

    return ticking_action
    # def rollback_timer_tick_function(timer_):
    #     timer_ticks = list(timer_.ticks)
    #     if seconds in timer_ticks:
    #         timer_ticks.remove(seconds)
    #     timer_ = replace(timer_, ticks=tuple(timer_ticks))
    #     return timer_
    #
    # action_tick = Action(
    #         name=f'Timer "{timer.name}" changed by {seconds} seconds',
    #         rollback_function=rollback_timer_tick_function(timer),
    # )
    #
    # timer.actions_list.append(action_tick)
    # timer = replace(timer, ticks=timer.ticks + (seconds, ))
    # for effect, start_time_dict in timer.subscribed_effects_dict.copy().items():
    #     if effect.finished:
    #         continue
    #     start_time = start_time_dict['start_time']
    #     # If it is time for effect to finish
    #     if start_time + effect.duration_in_seconds <= timer.seconds_passed:
    #         del timer.subscribed_effects_dict[effect]  # unsubscribe effect
    #         finished_effect, set_finished_action = set_effect_finished(effect=effect)
    #         timer.actions_list.append(set_finished_action)
    #         timer.subscribed_effects_dict[finished_effect] = start_time_dict
    #
    # return timer


def timer_untick(*, action: Action) -> Timer:
    timer = action.previous_value.value
    # timer.actions_list.remove(action)
    return timer


def roll_back_value(*, value: Value, action_id_to_rollback: str = "last") -> Value:
    if not value.actions_sequence:
        return value

    if action_id_to_rollback == 'last':
        return value.last_action.rollback_function(value)

    matching_actions = [a for a in value.actions_sequence if a.id == action_id_to_rollback]
    if not matching_actions:
        return value

    action = matching_actions[0]
    action_number = value.actions_sequence.index(action)
    rolled_back_value = action.rollback_function(value)
    if action_number < len(value.actions_sequence):  # Not the last action, need to repeat all following
        actions_to_repeat = [a for a in value.actions_sequence[action_number + 1:]]
        for a in actions_to_repeat:
            rolled_back_value = change_value(
                    changing_function=a.rollback_function,
                    value_to_change=rolled_back_value,
                    rollback_function=action.function).actual_value

    return rolled_back_value


def apply_effect_to_value(*,
                          effect: Effect,
                          value: Value,
                          short_description: str = '',
                          full_description: str = '') -> typing.Tuple[Value, Effect]:
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
    # effect_action = effect.action
    # effect_action = effect_action._replace(short_description=short_description, full_description=full_description)
    # effect = effect._replace(action=effect_action)

    application_action = Action(
            name=f'Effect {effect.name} was applied to value {value.name} (no value changing yet)',
            previous_value=value,
            short_description=short_description,
            full_description=full_description)

    updated_value = value.append_action_to_sequence(application_action)
    updated_value = change_value(
            value_to_change=updated_value,
            changing_function=effect.action.function,
            rollback_function=None).actual_value
    effect_action = effect.action
    effect_action = replace(effect_action,
                            short_description=short_description,
                            full_description=full_description,
                            previous_value=value,
                            actual_value=updated_value)
    # effect_action = effect_action._replace(
    #         short_description=short_description,
    #         full_description=full_description,
    #         previous_value=value,
    #         actual_value=updated_value)
    effect = replace(effect, action=effect_action)
    # effect._replace(action=effect_action)
    return updated_value, effect


def unapply_effect_from_value(*, effect: Effect, value: Value, rollback_function: typing.Callable) -> Value:
    remove_effect_action = Action(
            name=f'Effect "{effect.name}" removing from value "{value.name}"',
            previous_value=value,
            function=effect.action.rollback_function,
            short_description=f'Removing effect {effect.name} from {value.name}',
            full_description=f'Removing effect {effect.name} from {value.name}')
    # rollback_action = Action(function=rollback_function)
    value = value.append_action_to_sequence(remove_effect_action)
    value = change_value(
            value_to_change=value,
            changing_function=rollback_function,
            rollback_function=None,
    ).actual_value
    return value


def subscribe_effect_to_timer(*, effect: Effect, timer: Timer) -> Timer:
    timer.subscribed_effects_dict[effect] = {'start_time': timer.seconds_passed}
    return timer


def set_effect_finished(*, effect: Effect) -> typing.Tuple[Effect, Action]:
    def rollback_function():
        return replace(effect, finished=True)
        # return effect._replace(finished=False)

    set_finished_action = Action(
            name=f'Effect {effect.name} set finished',
            rollback_function=rollback_function)

    finished_effect = replace(effect, finished=True)
    # finished_effect = effect._replace(finished=True)

    return finished_effect, set_finished_action


if __name__ == '__main__':
    pass
