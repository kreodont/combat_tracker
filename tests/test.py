from temp import Action, Value, Effect, change_value, roll_back_action, apply_effect


def test_create_empty_action():
    action = Action(name='test_action', id='1')
    assert action.full_description == 'Changing value from None to None'


def test_create_empty_value():
    value = Value(name='test_value', id='2')
    assert value.full_description == '0'


def test_change_integer_value_from_0_to_10():
    value = Value(name='test_value', value=0)

    def f(v: Value) -> Value:
        v = v._replace(value=10)
        return v

    action = Action(name='test_action', id='1', function=f)
    new_value = change_value(value_to_change=value, action_to_perform=action)
    assert new_value.value == 10
    assert len(new_value.actions_sequence) == 1


def test_series_of_changes():
    value = Value(name='test_value', value=0)

    def change_to_11(v: Value) -> Value:
        v = v._replace(value=11)
        return v

    def change_to_12(v: Value) -> Value:
        v = v._replace(value=12)
        return v

    action = Action(function=change_to_11)
    new_value = change_value(value_to_change=value, action_to_perform=action)

    assert new_value.value == 11
    assert len(new_value.actions_sequence) == 1

    new_action = Action(function=change_to_12)
    another_value = change_value(value_to_change=new_value, action_to_perform=new_action)
    assert another_value.value == 12
    assert len(another_value.actions_sequence) == 2


def test_change_from_action():
    def change_to_100(v: Value) -> Value:
        v = v._replace(value=100)
        return v

    value = Value(name='some')
    action = Action(function=change_to_100)
    value = action.change_value(value=value)
    assert value.value == 100
    assert value.last_action != action  # they should not be so since we're adding fulfilled action
    assert value.last_action.id == action.id  # but ID should be the same


def test_that_previous_value_is_still_accessible():
    def change_to_55(v: Value) -> Value:
        v = v._replace(value=55)
        return v
    value = Value(name='some', value=4)
    value = Action(function=change_to_55).change_value(value=value)
    assert value.value == 55
    assert value.actions_sequence[-1].previous_value.value == 4


def test_change_and_then_default_rollback():

    def changing_function(v: Value) -> Value:
        v = v._replace(value=100)
        return v

    value = Value(name='some', value=1)
    action = Action(function=changing_function)
    value = action.change_value(value=value)
    assert value.value == 100
    rollback_function = value.actions_sequence[-1].rollback_function
    action = Action(function=rollback_function)
    previous_value = action.change_value(value=value)
    assert previous_value.value == 1


def test_non_default_rollback():
    def changing_function(v: Value) -> Value:
        v = v._replace(value=100)
        return v

    def rollback_function(v: Value) -> Value:
        v = v._replace(value=v.value + 5)
        return v

    value = Value(name='some', value=14)
    new_value = Action(function=changing_function).change_value(value=value, rollback_function=rollback_function)
    assert new_value.value == 100
    rolled_back_value = Action(function=new_value.last_action.rollback_function).change_value(value=new_value)
    assert rolled_back_value.value == 105


def test_multiple_action_aplying():
    def changing_function(v: Value) -> Value:
        v = v._replace(value=v.value + 1)
        return v

    value = Value(name='some', value=0)
    value = Action(function=changing_function).change_value(value=value)
    value = Action(function=changing_function).change_value(value=value)
    value = Action(function=changing_function).change_value(value=value)
    assert value.value == 3
    assert len(value.actions_sequence) == 3


def test_that_rollback_returns_the_same_object_if_no_actions_were_performed_yet():
    value = Value(name='some', value=15)
    new_value = roll_back_action(value=value)
    assert new_value == value


def test_that_rollback_works_with_last_action():
    def changing_function(v: Value) -> Value:
        v = v._replace(value='Changed Value')
        return v

    initial_value = Value(name='some', value='Initial Value')
    changed_value = Action(function=changing_function).change_value(value=initial_value)
    assert changed_value.value == 'Changed Value'
    previous_value = roll_back_action(value=changed_value)
    assert previous_value == initial_value


def test_that_rollback_returns_the_same_object_if_wrong_action_id_specified():
    def set_14(v: Value) -> Value:
        v = v._replace(value=14)
        return v

    initial_value = Value(name='Some', value=13)
    changed_value = Action(function=set_14, id='123').change_value(value=initial_value)
    assert changed_value.value == 14
    rolled_back_value = roll_back_action(value=changed_value, action_id='12')
    assert rolled_back_value == changed_value


def test_explicitly_specified_rollback():
    def set_14(v: Value) -> Value:
        v = v._replace(value=14)
        return v

    initial_value = Value(name='Some', value=13)
    changed_value = Action(function=set_14, id='123').change_value(value=initial_value)
    assert changed_value.value == 14
    rolled_back_value = roll_back_action(value=changed_value, action_id='123')
    assert rolled_back_value == initial_value


def test_that_if_intermediate_action_was_rolled_back_then_all_following_will_be_recalculated():
    def increment(v: Value) -> Value:
        v = v._replace(value=v.value + 1)
        return v

    initial_value = Value(name='some', value=1)
    v_1 = Action(function=increment, id='first_increment').change_value(value=initial_value)
    assert v_1.value == 2
    v_2 = Action(function=increment, id='second_increment').change_value(value=v_1)
    assert v_2.value == 3
    final_value = Action(function=increment, id='third_increment').change_value(value=v_2)
    assert final_value.value == 4
    assert len(final_value.actions_sequence) == 3
    final_value = roll_back_action(value=final_value, action_id='second_increment')
    assert final_value.value == 3
    assert len(final_value.actions_sequence) == 2


def test_several_roll_backs():
    def increment_by_10(v: Value) -> Value:
        v = v._replace(value=v.value + 10)
        return v

    initial_value = Value(name='some', value=100)
    v_1 = Action(function=increment_by_10, id='first_increment').change_value(value=initial_value)
    assert v_1.value == 110
    v_2 = Action(function=increment_by_10, id='second_increment').change_value(value=v_1)
    assert v_2.value == 120
    final_value = Action(function=increment_by_10, id='third_increment').change_value(value=v_2)
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

    initial_value = Value(name='some', value=100)
    v_1 = Action(function=increment_by_10, id='first_increment').change_value(value=initial_value)
    assert v_1.value == 110
    v_2 = Action(function=increment_by_10, id='second_increment').change_value(value=v_1)
    assert v_2.value == 120
    final_value = Action(function=increment_by_10, id='third_increment').change_value(value=v_2)
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

    value = Value(name='some', value=-5)
    value = value.change(action_to_perform=Action(function=increment_by_10))
    value = value.change(action_to_perform=Action(function=increment_by_10))
    value = value.change(action_to_perform=Action(function=increment_by_10))
    value = value.change(action_to_perform=Action(function=increment_by_10))
    assert value.value == 35
    assert len(value.actions_sequence) == 4


def test_empty_effect_applied():
    effect = Effect(name='test effect', action=Action(function=lambda x: x))
    assert effect.applied is False


def test_simple_effect_apply():
    def increment_by_10(v: Value) -> Value:
        v = v._replace(value=v.value + 10)
        return v

    value = Value(value=10, name='some')
    effect_action = Action(function=increment_by_10)
    effect = Effect(name='Increment by 10', action=effect_action)
    value = apply_effect(effect=effect, value=value)
    assert value.value == 20
    assert len(value.actions_sequence) == 2


def test_effect_application_from_effect_object():
    def increment_by_10(v: Value) -> Value:
        v = v._replace(value=v.value + 10)
        return v

    value = Value(value=10, name='some')
    effect_action = Action(function=increment_by_10)
    effect = Effect(name='Increment by 10', action=effect_action, short_description='Значение увеличивается на 10')
    value = effect.apply(value=value)
    assert value.value == 20
    assert len(value.actions_sequence) == 2
