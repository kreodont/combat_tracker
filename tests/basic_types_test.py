from basic_types import Action, Value, Effect, change_value, roll_back_value, \
    apply_effect_to_value, unapply_effect_from_value, Timer, subscribe_effect_to_timer, timer_tick, DiceThrow, Formula
from dataclasses import replace


def test_create_empty_action():
    action = Action(name='test_action')
    assert action.full_description == 'No full description'


def test_create_empty_value():
    value = Value(name='test_value', value='0')
    assert value.full_description == 'No full description'


def test_that_empty_action_doesnt_change_value():
    old_value = Value(value=42)
    new_value = change_value(value_to_change=old_value, changing_function=None, rollback_function=None).actual_value
    assert old_value == new_value


def test_change_integer_value_from_0_to_10():
    value = Value(name='test_value', value=0)

    def f(v: Value) -> Value:
        v = replace(v, value=10)
        return v

    new_value = change_value(
            value_to_change=value,
            changing_function=f,
            rollback_function=None).actual_value
    assert new_value.value == 10
    assert len(new_value.actions_sequence) == 1


def test_series_of_changes():
    value = Value(name='test_value', value=0)

    def change_to_11(v: Value) -> Value:
        v = replace(v, value=11)
        return v

    def change_to_12(v: Value) -> Value:
        v = replace(v, value=12)
        return v

    new_value = change_value(value_to_change=value, changing_function=change_to_11, rollback_function=None).actual_value

    assert new_value.value == 11
    assert len(new_value.actions_sequence) == 1

    another_value = change_value(
            value_to_change=new_value,
            changing_function=change_to_12,
            rollback_function=None).actual_value
    assert another_value.value == 12
    assert len(another_value.actions_sequence) == 2


def test_that_previous_value_is_still_accessible():
    def change_to_55(v: Value) -> Value:
        v = replace(v, value=55)
        return v

    value = Value(name='some', value=4)
    value = change_value(
            value_to_change=value,
            changing_function=change_to_55,
            rollback_function=None).actual_value
    assert value.value == 55
    assert value.actions_sequence[-1].previous_value.value == 4


def test_change_and_then_default_rollback():

    def changing_function(v: Value) -> Value:
        v = replace(v, value=100)
        return v

    value = Value(name='some', value=1)
    value = change_value(
            changing_function=changing_function,
            value_to_change=value,
            rollback_function=None,
    ).actual_value
    assert value.value == 100
    rollback_function = value.actions_sequence[-1].rollback_function
    previous_value = change_value(value_to_change=value, changing_function=rollback_function).actual_value
    assert previous_value.value == 1


def test_non_default_rollback():
    def changing_function(v: Value) -> Value:
        v = replace(v, value=100)
        return v

    def rollback_function(v: Value) -> Value:
        v = replace(v, value=v.value + 5)
        return v

    value = Value(name='some', value=14)
    new_value = change_value(
            changing_function=changing_function,
            value_to_change=value,
            rollback_function=rollback_function).actual_value
    assert new_value.value == 100

    rolled_back_value = change_value(
            changing_function=rollback_function,
            value_to_change=new_value,
            rollback_function=rollback_function).actual_value
    assert rolled_back_value.value == 105


def test_multiple_action_aplying():
    def increment(v: Value) -> Value:
        v = replace(v, value=v.value + 1)
        return v

    value = Value(name='some', value=0)
    value = change_value(
            value_to_change=value,
            changing_function=increment,
            rollback_function=None).actual_value
    value = change_value(
            value_to_change=value,
            changing_function=increment,
            rollback_function=None).actual_value
    value = change_value(
            value_to_change=value,
            changing_function=increment,
            rollback_function=None).actual_value
    assert value.value == 3
    assert len(value.actions_sequence) == 3


def test_that_rollback_returns_the_same_object_if_no_actions_were_performed_yet():
    value = Value(name='some', value=15)
    new_value = roll_back_value(value=value)  # last action by default
    assert new_value == value


def test_that_rollback_works_with_last_action():
    def changing_function(v: Value) -> Value:
        v = replace(v, value='Changed Value')
        return v

    initial_value = Value(name='some', value='Initial Value')
    changed_value = change_value(
            value_to_change=initial_value,
            changing_function=changing_function,
            rollback_function=None).actual_value

    assert changed_value.value == 'Changed Value'
    previous_value = roll_back_value(value=changed_value)
    assert previous_value == initial_value


def test_that_rollback_returns_the_same_object_if_wrong_action_id_specified():
    def set_14(v: Value) -> Value:
        v = replace(v, value=14)
        return v

    initial_value = Value(name='Some', value=13)
    changed_value = change_value(
            value_to_change=initial_value,
            changing_function=set_14,
            rollback_function=None).actual_value
    assert changed_value.value == 14
    rolled_back_value = roll_back_value(value=changed_value, action_id_to_rollback='12')
    assert rolled_back_value == changed_value


def test_explicitly_specified_rollback():
    def set_14(v: Value) -> Value:
        v = replace(v, value=14)
        return v

    initial_value = Value(name='Some', value=13)

    changed_value = change_value(
            value_to_change=initial_value,
            changing_function=set_14,
            rollback_function=None).actual_value

    assert changed_value.value == 14
    rolled_back_value = roll_back_value(value=changed_value, action_id_to_rollback=changed_value.last_action.id)
    assert rolled_back_value == initial_value


def test_that_if_intermediate_action_was_rolled_back_then_all_following_will_be_recalculated():
    def increment(v: Value) -> Value:
        v = replace(v, value=v.value + 1)
        return v

    initial_value = Value(name='some', value=1)

    v_1 = change_value(
            value_to_change=initial_value,
            changing_function=increment,
            rollback_function=None).actual_value
    assert v_1.value == 2

    v_2 = change_value(
            value_to_change=v_1,
            changing_function=increment,
            rollback_function=None).actual_value
    assert v_2.value == 3

    final_value = change_value(
            value_to_change=v_2,
            changing_function=increment,
            rollback_function=None).actual_value
    assert final_value.value == 4
    assert len(final_value.actions_sequence) == 3

    final_value = roll_back_value(value=final_value, action_id_to_rollback=v_2.last_action.id)
    assert final_value.value == 3
    assert len(final_value.actions_sequence) == 2


def test_several_roll_backs():
    def increment_by_10(v: Value) -> Value:
        v = replace(v, value=v.value + 10)
        # v = v._replace(value=v.value + 10)
        return v

    initial_value = Value(name='some', value=100)
    v_1 = change_value(
            changing_function=increment_by_10,
            value_to_change=initial_value,
            rollback_function=None).actual_value
    assert v_1.value == 110

    v_2 = change_value(
            value_to_change=v_1,
            changing_function=increment_by_10,
            rollback_function=None).actual_value
    assert v_2.value == 120

    final_value = change_value(
            changing_function=increment_by_10,
            value_to_change=v_2,
            rollback_function=None).actual_value
    assert final_value.value == 130
    assert len(final_value.actions_sequence) == 3

    rolled_back_value = roll_back_value(value=final_value, action_id_to_rollback=v_2.last_action.id)
    rolled_back_value = roll_back_value(value=rolled_back_value, action_id_to_rollback=v_1.last_action.id)
    assert rolled_back_value.value == 110
    assert len(rolled_back_value.actions_sequence) == 1


def test_simple_effect_apply():
    def increment_by_10(v: Value) -> Value:
        v = replace(v, value=v.value + 10)
        return v

    value = Value(value=10, name='some')
    effect_action = Action(function=increment_by_10)
    effect = Effect(name='Increment by 10', action=effect_action)
    value, effect = apply_effect_to_value(effect=effect, value=value)
    assert value.value == 20
    assert len(value.actions_sequence) == 2
    assert value.actions_sequence[0].id != value.actions_sequence[1].id


def test_effect_unapply():
    def increment_by_10(v: Value) -> Value:
        v = replace(v, value=v.value + 10)
        return v

    def rollback_function(v: Value) -> Value:
        v = replace(v, value=v.value - 10)
        return v

    value = Value(value=10, name='some')
    effect_action = Action(function=increment_by_10)
    effect = Effect(
            name='Increment by 10', action=effect_action, short_description='Значение увеличивается на 10')
    value, effect = apply_effect_to_value(effect=effect, value=value)
    assert value.value == 20
    assert len(value.actions_sequence) == 2
    value = unapply_effect_from_value(effect=effect, value=value, rollback_function=rollback_function)
    assert value.value == 10
    assert len(value.actions_sequence) == 4  # Apply effect, change value, unapply effect, change value back


def test_effect_unapplication_from_effect():
    def set_200(v: Value) -> Value:
        v = replace(v, value=200)
        return v

    value = Value(value=10, name='some')
    effect_action = Action(function=set_200)
    effect = Effect(
            name='Increment by 10', action=effect_action, short_description='Значение увеличивается на 10')
    value, effect = apply_effect_to_value(effect=effect, value=value)
    assert value.value == 200
    rollback_function = value.last_action.rollback_function
    value = unapply_effect_from_value(effect=effect, value=value, rollback_function=rollback_function)
    assert value.value == 10


def test_that_2_consequence_actions_have_different_id():
    action1 = Action()
    action2 = Action()
    assert action1.id != action2.id


def test_that_2_different_values_always_have_different_id():
    value1 = Value(name='value1', value=0)
    value2 = Value(name='value2', value=0)
    assert value1.id != value2.id


def test_that_2_different_effects_always_have_different_id():
    effect1 = Effect(name='effect1', action=Action())
    effect2 = Effect(name='effect1', action=Action())
    assert effect1.id != effect2.id


def test_that_default_effect_duration_is_infinite():
    effect = Effect(name='effect1', action=Action())
    assert effect.duration_in_seconds > 9999999999999999999  # 317 million years


def test_that_default_timer_time_is_zero():
    timer = Timer()
    assert timer.seconds_passed == 0


def test_that_timer_tick_changes_timers_ticks():
    timer = Timer(ticks=(20, ))
    assert timer.seconds_passed == 20
    timer = timer_tick(timer=timer, seconds=50).actual_value.value
    assert timer.seconds_passed == 70


def test_that_timer_tick_can_be_undone():
    timer = Timer(name='My timer')
    assert timer.seconds_passed == 0
    tick_action = timer_tick(timer=timer, seconds=5)
    timer = tick_action.actual_value.value
    assert timer.seconds_passed == 5
    timer = timer.untick(action=tick_action)
    assert timer.seconds_passed == 0


def test_that_timer_tick_finishes_effect():
    def set_20(v: Value) -> Value:
        v = replace(v, value=20)
        # v = v._replace(value=20)
        return v

    action_make_20 = Action(function=set_20)
    effect = Effect(name='Effect make 20 for 20 seconds', action=action_make_20, duration_in_seconds=20)
    value = Value(value=10, name='1')
    value_with_effect_aplied, effect_applied_to_value = apply_effect_to_value(effect=effect, value=value)
    timer = Timer(name='Global')
    timer = subscribe_effect_to_timer(effect=effect_applied_to_value, timer=timer)

    assert value_with_effect_aplied.value == 20
    timer = timer_tick(timer=timer, seconds=10).actual_value.value  # 10 seconds passed, effect not finished yet
    effect_applied_to_value = timer.find_effect_by_id(effect_id=effect.id)
    assert timer.seconds_passed == 10
    assert effect_applied_to_value.finished is False
    value = effect_applied_to_value.get_value()
    assert value.value == 20

    timer = timer_tick(timer=timer, seconds=10).actual_value.value
    assert timer.seconds_passed == 20
    effect_applied_to_value = timer.find_effect_by_id(effect_id=effect.id)
    assert effect_applied_to_value.finished is True
    value = effect_applied_to_value.get_value()
    assert value.value == 10


def test_d20_throw():
    dice_throw = DiceThrow(minimal_possible_value=1, maximal_possible_value=20, name='d20 throw')
    throw_action = dice_throw.throw()
    value = throw_action.actual_value
    assert 1 <= value.value <= 20
    assert isinstance(value.value, int)


def test_custom_dice_throw():
    dice_throw = DiceThrow(minimal_possible_value=15, maximal_possible_value=15, name='custom throw')
    throw_action = dice_throw.throw()
    value = throw_action.actual_value
    assert throw_action.name == 'Action for DiceThrow "custom throw"'
    assert value.value == 15


def test_dice_throw_with_negative_value():
    dice_throw = DiceThrow(
            minimal_possible_value=1,
            maximal_possible_value=6,
            name='minus d6',
            is_negative=True)
    throw_action = dice_throw.throw()
    value = throw_action.actual_value
    assert throw_action.name == 'Action for DiceThrow "minus d6"'
    assert -6 <= value.value <= -1


def test_that_formula_parsed_correctly():
    formula = Formula(name='Test formula', text_representation='2d6 - 12')
    actions = formula.parse()
    assert len(actions) == 3  # action d6, action d6, action -12
    assert actions[2].actual_value.value == -12.0


def test_that_d0_always_returns_0():
    formula = Formula(name='Zero', text_representation='d0')
    actions = formula.parse()
    assert len(actions) == 1
    assert actions[0].actual_value.value == 0


def test_that_d1_always_returns_1():
    formula = Formula(name='One', text_representation='d1')
    actions = formula.parse()
    assert len(actions) == 1
    assert actions[0].actual_value.value == 1


def test_that_d_negative_is_forbidden():
    formula = Formula(name='Minus 5', text_representation='d-5')
    actions = formula.parse()
    total_roll_value = sum((a.actual_value.value for a in actions))
    assert total_roll_value == -5.0


def test_complicated_formula():
    formula = Formula(name='Complicated', text_representation='90d0 - d1 + 3-4d1')
    actions = formula.parse()
    total_roll_value = sum((a.actual_value.value for a in actions))
    assert total_roll_value == -2.0
