from temp import Action, Value, change_value


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
    new_value = change_value(value, action)
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
    new_value = change_value(value, action)

    assert new_value.value == 11
    assert len(new_value.actions_sequence) == 1

    new_action = Action(function=change_to_12)
    another_value = change_value(new_value, new_action)
    assert another_value.value == 12
    assert len(another_value.actions_sequence) == 2


def test_change_from_action():
    def change_to_100(v: Value) -> Value:
        v = v._replace(value=100)
        return v

    value = Value(name='some')
    action = Action(function=change_to_100)
    value = action.change_value(value)
    assert value.value == 100


def test_that_previous_value_is_still_accessible():
    def change_to_55(v: Value) -> Value:
        v = v._replace(value=55)
        return v
    value = Value(name='some', value=4)
    value = Action(function=change_to_55).change_value(value)
    assert value.value == 55
    assert value.actions_sequence[-1].previous_value.value == 4
