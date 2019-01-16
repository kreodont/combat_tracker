from dnd_types import Roll, Formula, Action


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
