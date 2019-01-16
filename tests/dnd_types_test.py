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
    cancelled_roll = roll.cancell()
    assert cancelled_roll.value == 0
