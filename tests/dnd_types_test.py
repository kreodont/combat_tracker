from dnd_types import Roll, Formula, Action, Rule


def test_simple_attack():
    r = Roll(
            name='Simple attack',
            formula=Formula(
                    name='Simple Formula',
                    text_representation='5d6 + 10'),
            type='attack',
            main_action=Action())
    assert 16 <= r.value <= 40


def test_that_different_attacks_have_different_ids():
    roll_1 = Roll(
            name='Roll 1',
            formula=Formula(
                    name='some',
                    text_representation='d20'),
            type='attack',
            main_action=Action())

    roll_2 = Roll(
            name='Roll 2',
            formula=Formula(
                    name='some',
                    text_representation='d20'),
            type='attack',
            main_action=Action())

    assert roll_1.id != roll_2.id


def test_if_attack_main_action_is_cancelled_all_rolls_are_also_cancelled():
    roll = Roll(type='attack', formula=Formula(text_representation='5d1 + 12'))
    assert roll.value == 17
    canceled_roll = roll.cancel()
    assert canceled_roll.value == 0


def test_that_each_throw_in_roll_can_be_canceled_separately():
    roll = Roll(type='attack', formula=Formula(text_representation='6d1 - d0 + 4'))
    assert roll.value == 10
    new_roll = roll.cancel_single_throw(throw_number=3)
    assert new_roll.value == 9
    yet_new_roll = new_roll.cancel_single_throw(throw_number=7)
    assert yet_new_roll.value == 5
    yet_new_roll = yet_new_roll.cancel_single_throw(throw_number=6)  # canceling d0 doesn't take any effect
    assert yet_new_roll.value == 5


def test_that_specifying_roll_number_more_than_roll_has_takes_no_effect():
    roll = Roll(type='attack', formula=Formula(text_representation='d20'))
    roll_value = roll.value
    assert 1 <= roll_value <= 20
    new_roll = roll.cancel_single_throw(throw_number=1)  # there is only 0th value
    assert new_roll.value == roll_value


def test_that_after_roll_cancelled_previous_value_of_the_roll_still_accessible():
    roll = Roll(type='attack', formula=Formula(text_representation='d1 - d0 + 2'))
    assert roll.value == 3
    changed_roll = roll.cancel()
    assert changed_roll.value == 0
    assert changed_roll.previous_value == 3


def test_that_roll_value_can_be_set_manually():
    roll = Roll(type='attack', formula=Formula(text_representation='d20'))
    roll_value = roll.value
    assert 1 <= roll_value <= 20
    manuall_roll = roll.manual_set_value(manual_value=42)
    assert manuall_roll.value == 42
    assert manuall_roll.previous_value == roll_value


def test_simple_rule():
    def d20_check(roll: Roll):
        if roll.formula.text_representation != 'd20':
            return False, 'Правило применимо только к броскам d20'
        if 1 <= roll.value <= 20:
            return True, ''
        return False, 'Значение броска d20 должно находиться в пределах от 1 до 20'
    rule = Rule(check_function=d20_check)
    assert rule.check_function(Roll(formula=Formula(text_representation='d20'), type='attack')) == (True, '')
    assert rule.check_function(Roll(
            formula=Formula(text_representation='2d20'),
            type='attack')) == (False, 'Правило применимо только к броскам d20')
    wrong_d20_roll = Roll(formula=Formula(text_representation='d20'), type='attack').manual_set_value(manual_value=30)
    assert rule.check_function(wrong_d20_roll) == (False, 'Значение броска d20 должно находиться в пределах от 1 до 20')
