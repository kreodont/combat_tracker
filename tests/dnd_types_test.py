from dnd_types import Roll, Formula, Action


def test_simple_attack():
    r = Roll(
            name='Simple attack',
            # id='1',
            formula=Formula(
                    id='1',
                    name='Simple Formula',
                    text_representation='5d6 + 10'),
            type='attack',
            main_action=Action(id='4'))
    print(r.value)
    assert 16 <= r.value <= 40


def test_that_different_attacks_have_different_ids():
    roll_1 = Roll(
            name='Roll 1',
            formula=Formula(
                    id='1',
                    name='some',
                    text_representation='d20'),
            type='attack',
            main_action=Action(id='1'))

    roll_2 = Roll(
            name='Roll 2',
            formula=Formula(
                    id='1',
                    name='some',
                    text_representation='d20'),
            type='attack',
            main_action=Action(id='1'))

    assert roll_1.id != roll_2.id
