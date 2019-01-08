from basic_types import Action, Value, Effect, change_value, roll_back_action, apply_effect, unapply_effect, Timer


def test_create_empty_action():
    action = Action(name='test_action', id='1')
    assert action.full_description == 'Changing value from None to None'


def test_create_empty_value():
    value = Value(name='test_value', id='2')
    assert value.full_description == '0'


def test_change_integer_value_from_0_to_10():
    value = Value(name='test_value', value=0, id='1')

    def f(v: Value) -> Value:
        v = v._replace(value=10)
        return v

    action = Action(name='test_action', id='1', function=f)
    new_value = change_value(value_to_change=value, action_to_perform=action, rollback_function=lambda x: x)
    assert new_value.value == 10
    assert len(new_value.actions_sequence) == 1


def test_series_of_changes():
    value = Value(name='test_value', value=0, id='1')

    def change_to_11(v: Value) -> Value:
        v = v._replace(value=11)
        return v

    def change_to_12(v: Value) -> Value:
        v = v._replace(value=12)
        return v

    action = Action(function=change_to_11, id='1')
    new_value = change_value(value_to_change=value, action_to_perform=action, rollback_function=lambda x: x)

    assert new_value.value == 11
    assert len(new_value.actions_sequence) == 1

    new_action = Action(function=change_to_12, id='1')
    another_value = change_value(value_to_change=new_value, action_to_perform=new_action, rollback_function=lambda x: x)
    assert another_value.value == 12
    assert len(another_value.actions_sequence) == 2


def test_change_from_action():
    def change_to_100(v: Value) -> Value:
        v = v._replace(value=100)
        return v

    value = Value(name='some', id='1')
    action = Action(function=change_to_100, id='1')
    value = change_value(value_to_change=value, action_to_perform=action, rollback_function=None)
    assert value.value == 100
    assert value.last_action != action  # they should not be so since we're adding fulfilled action
    assert value.last_action.id == action.id  # but ID should be the same


def test_that_previous_value_is_still_accessible():
    def change_to_55(v: Value) -> Value:
        v = v._replace(value=55)
        return v
    value = Value(name='some', value=4, id='1')
    value = change_value(
            value_to_change=value,
            action_to_perform=Action(function=change_to_55, id='1'),
            rollback_function=None)
    assert value.value == 55
    assert value.actions_sequence[-1].previous_value.value == 4


def test_change_and_then_default_rollback():

    def changing_function(v: Value) -> Value:
        v = v._replace(value=100)
        return v

    value = Value(name='some', value=1, id='1')
    action = Action(function=changing_function, id='1')
    value = change_value(action_to_perform=action, value_to_change=value, rollback_function=None)
    assert value.value == 100
    rollback_function = value.actions_sequence[-1].rollback_function
    rollback_action = Action(function=rollback_function, id='12')
    previous_value = change_value(value_to_change=value, action_to_perform=rollback_action, rollback_function=None)
    assert previous_value.value == 1


def test_non_default_rollback():
    def changing_function(v: Value) -> Value:
        v = v._replace(value=100)
        return v

    def rollback_function(v: Value) -> Value:
        v = v._replace(value=v.value + 5)
        return v

    value = Value(name='some', value=14, id='1')
    new_value = change_value(
            action_to_perform=Action(function=changing_function, id='1'),
            value_to_change=value,
            rollback_function=rollback_function)
    assert new_value.value == 100

    rolled_back_value = change_value(
            action_to_perform=Action(function=new_value.last_action.rollback_function, id='1'),
            value_to_change=new_value,
            rollback_function=rollback_function)
    assert rolled_back_value.value == 105


def test_multiple_action_aplying():
    def increment(v: Value) -> Value:
        v = v._replace(value=v.value + 1)
        return v

    value = Value(name='some', value=0, id='1')
    value = change_value(
            value_to_change=value,
            action_to_perform=Action(function=increment, id='1'),
            rollback_function=None)
    value = change_value(
            value_to_change=value,
            action_to_perform=Action(function=increment, id='2'),
            rollback_function=None)
    value = change_value(
            value_to_change=value,
            action_to_perform=Action(function=increment, id='3'),
            rollback_function=None)
    assert value.value == 3
    assert len(value.actions_sequence) == 3


def test_that_rollback_returns_the_same_object_if_no_actions_were_performed_yet():
    value = Value(name='some', value=15, id='1')
    new_value = roll_back_action(value=value)
    assert new_value == value


def test_that_rollback_works_with_last_action():
    def changing_function(v: Value) -> Value:
        v = v._replace(value='Changed Value')
        return v

    initial_value = Value(name='some', value='Initial Value', id='1')
    changed_value = change_value(
            value_to_change=initial_value,
            action_to_perform=Action(function=changing_function, id='1'),
            rollback_function=None)

    assert changed_value.value == 'Changed Value'
    # TODO: change roll_back_action to accept only action as a parameter, not value
    previous_value = roll_back_action(value=changed_value)
    assert previous_value == initial_value


def test_that_rollback_returns_the_same_object_if_wrong_action_id_specified():
    def set_14(v: Value) -> Value:
        v = v._replace(value=14)
        return v

    initial_value = Value(name='Some', value=13, id='1')
    changed_value = change_value(
            value_to_change=initial_value,
            action_to_perform=Action(function=set_14, id='123'),
            rollback_function=None)
    assert changed_value.value == 14
    rolled_back_value = roll_back_action(value=changed_value, action_id='12')
    assert rolled_back_value == changed_value


def test_explicitly_specified_rollback():
    def set_14(v: Value) -> Value:
        v = v._replace(value=14)
        return v

    initial_value = Value(name='Some', value=13, id='1')

    changed_value = change_value(
            value_to_change=initial_value,
            action_to_perform=Action(function=set_14, id='123'),
            rollback_function=None)

    assert changed_value.value == 14
    rolled_back_value = roll_back_action(value=changed_value, action_id='123')
    assert rolled_back_value == initial_value


def test_that_if_intermediate_action_was_rolled_back_then_all_following_will_be_recalculated():
    def increment(v: Value) -> Value:
        v = v._replace(value=v.value + 1)
        return v

    initial_value = Value(name='some', value=1, id='1')

    v_1 = change_value(
            value_to_change=initial_value,
            action_to_perform=Action(function=increment, id='first_increment'),
            rollback_function=None)
    assert v_1.value == 2

    v_2 = change_value(
            value_to_change=v_1,
            action_to_perform=Action(function=increment, id='second_increment'),
            rollback_function=None)
    assert v_2.value == 3

    final_value = change_value(
            value_to_change=v_2,
            action_to_perform=Action(function=increment, id='third_increment'),
            rollback_function=None)
    assert final_value.value == 4
    assert len(final_value.actions_sequence) == 3

    final_value = roll_back_action(value=final_value, action_id='second_increment')
    assert final_value.value == 3
    assert len(final_value.actions_sequence) == 2


def test_several_roll_backs():
    def increment_by_10(v: Value) -> Value:
        v = v._replace(value=v.value + 10)
        return v

    initial_value = Value(name='some', value=100, id='1')
    v_1 = change_value(
            action_to_perform=Action(function=increment_by_10, id='first_increment'),
            value_to_change=initial_value,
            rollback_function=None)
    assert v_1.value == 110

    v_2 = change_value(
            value_to_change=v_1,
            action_to_perform=Action(function=increment_by_10, id='second_increment'),
            rollback_function=None)
    assert v_2.value == 120

    final_value = change_value(
            action_to_perform=Action(function=increment_by_10, id='third_increment'),
            value_to_change=v_2,
            rollback_function=None)
    assert final_value.value == 130
    assert len(final_value.actions_sequence) == 3

    rolled_back_value = roll_back_action(value=final_value, action_id='second_increment')
    rolled_back_value = roll_back_action(value=rolled_back_value, action_id='first_increment')
    assert rolled_back_value.value == 110
    assert len(rolled_back_value.actions_sequence) == 1


def test_rollback_from_value_object():
    def increment_by_10(v: Value) -> Value:
        v = v._replace(value=v.value + 10)
        return v

    initial_value = Value(name='some', value=100, id='1')
    v_1 = change_value(
            action_to_perform=Action(function=increment_by_10, id='first_increment'),
            value_to_change=initial_value,
            rollback_function=None)
    assert v_1.value == 110

    v_2 = change_value(
            action_to_perform=Action(function=increment_by_10, id='second_increment'),
            value_to_change=v_1,
            rollback_function=None)
    assert v_2.value == 120

    final_value = change_value(
            action_to_perform=Action(function=increment_by_10, id='third_increment'),
            value_to_change=v_2,
            rollback_function=None)
    assert final_value.value == 130
    assert len(final_value.actions_sequence) == 3

    rolled_back_value = final_value.roll_back_action(action_id='second_increment')
    rolled_back_value = rolled_back_value.roll_back_action(action_id='first_increment')
    assert rolled_back_value.value == 110
    assert len(rolled_back_value.actions_sequence) == 1


def test_change_from_value_object():
    def increment_by_10(v: Value) -> Value:
        v = v._replace(value=v.value + 10)
        return v

    value = Value(name='some', value=-5, id='1')
    value = value.change(action_to_perform=Action(function=increment_by_10, id='1'))
    value = value.change(action_to_perform=Action(function=increment_by_10, id='1'))
    value = value.change(action_to_perform=Action(function=increment_by_10, id='1'))
    value = value.change(action_to_perform=Action(function=increment_by_10, id='1'))
    assert value.value == 35
    assert len(value.actions_sequence) == 4


def test_simple_effect_apply():
    def increment_by_10(v: Value) -> Value:
        v = v._replace(value=v.value + 10)
        return v

    value = Value(value=10, name='some', id='1')
    effect_action = Action(function=increment_by_10, id='12')
    effect = Effect(name='Increment by 10', action=effect_action, id='1')
    value = apply_effect(effect=effect, value=value)
    assert value.value == 20
    assert len(value.actions_sequence) == 2
    assert value.actions_sequence[0].id != value.actions_sequence[1].id


def test_effect_unapply():
    def increment_by_10(v: Value) -> Value:
        v = v._replace(value=v.value + 10)
        return v

    def rollback_function(v: Value) -> Value:
        v = v._replace(value=v.value - 10)
        return v

    value = Value(value=10, name='some', id='1')
    effect_action = Action(function=increment_by_10, id='2')
    effect = Effect(
            name='Increment by 10', action=effect_action, short_description='Значение увеличивается на 10', id='1')
    value = apply_effect(effect=effect, value=value)
    assert value.value == 20
    assert len(value.actions_sequence) == 2
    value = unapply_effect(effect=effect, value=value, rollback_function=rollback_function)
    assert value.value == 10
    assert len(value.actions_sequence) == 4  # Apply effect, change value, unapply effect, change value back


def test_effect_unapplication_from_effect():
    def set_200(v: Value) -> Value:
        v = v._replace(value=200)
        return v

    value = Value(value=10, name='some', id='1')
    effect_action = Action(function=set_200, id='4')
    effect = Effect(
            name='Increment by 10', action=effect_action, short_description='Значение увеличивается на 10', id='1')
    value = apply_effect(effect=effect, value=value)
    assert value.value == 200
    rollback_function = value.last_action.rollback_function
    value = unapply_effect(effect=effect, value=value, rollback_function=rollback_function)
    assert value.value == 10


def test_that_2_consequence_actions_have_different_id():
    action1 = Action(id='1')
    action2 = Action(id='2')
    assert action1.id != action2.id


def test_that_2_different_values_always_have_different_id():
    value1 = Value(name='value1', id='1')
    value2 = Value(name='value2', id='3')
    assert value1.id != value2.id


def test_that_2_different_effects_always_have_different_id():
    effect1 = Effect(name='effect1', action=Action(id='1'), id='1')
    effect2 = Effect(name='effect1', action=Action(id='1'), id='')
    assert effect1.id != effect2.id


def test_that_default_effect_duration_is_infinite():
    effect = Effect(name='effect1', action=Action(id='1'), id='1')
    assert effect.duration_in_seconds > 9999999999999999999  # 317 million years


def test_that_default_timer_time_is_zero():
    timer = Timer(name='default', actions_list=[], subscribers={}, ticks=[])
    assert timer.seconds_passed == 0


def test_that_timer_tick_changes_timers_ticks():
    timer = Timer(ticks=[20], name='default', actions_list=[], subscribers={})
    assert timer.seconds_passed == 20
    timer = timer.tick(seconds=50)
    assert timer.seconds_passed == 70
    assert len(timer.actions_list) == 1


def test_that_timer_tick_can_be_undone():
    timer = Timer(name='My timer', actions_list=[], subscribers={}, ticks=[])
    assert timer.seconds_passed == 0
    timer = timer.tick(seconds=5)
    assert timer.seconds_passed == 5
    assert len(timer.actions_list) == 1
    timer = timer.untick(action=timer.actions_list[0])
    assert timer.seconds_passed == 0
    assert timer.actions_list == []


def test_that_timer_tick_finishes_effect():
    def set_20(v: Value) -> Value:
        v = v._replace(value=20)
        return v

    action_make_20 = Action(id='4', function=set_20)
    effect = Effect(name='make 20', action=action_make_20, id='effect_0', duration_in_seconds=20)
    value = Value(value=10, name='1', id='10')
    value = apply_effect(effect=effect, value=value)
    timer = Timer(name='Global', actions_list=[], subscribers={}, ticks=[])
    timer.subscribe_effect(effect=effect)
    assert value.value == 20
    timer = timer.tick(seconds=40)
    assert timer.seconds_passed == 40
    effect = list(timer.subscribers.keys())[0]
    assert effect.finished is True
    # assert value.value == 10
