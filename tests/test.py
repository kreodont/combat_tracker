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
    action = change_value(value, action)
    assert action.actual_value.value == 10
    assert len(action.actual_value.actions_sequence) == 1


def test_series_of_changes():
    value = Value(name='test_value', value=0)
    # print(f'Len: {len(value.actions_sequence)}\n')

    def change_to_11(v: Value) -> Value:
        v = v._replace(value=11)
        return v

    def change_to_12(v: Value) -> Value:
        v = v._replace(value=12)
        return v

    action = Action(function=change_to_11)
    action = change_value(value, action)
    assert action.actual_value.value == 11
    assert len(action.actual_value.actions_sequence) == 1

    action = Action(function=change_to_12)
    action = change_value(value, action)
    assert action.actual_value.value == 12
    assert len(action.actual_value.actions_sequence) == 2

