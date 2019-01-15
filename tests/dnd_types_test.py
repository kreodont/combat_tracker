from dnd_types import Attack, Formula


def test_simple_attack():
    a = Attack(
            name='Simple attack',
            id='1',
            formula=Formula(
                    id='1',
                    name='Simple Formula',
                    text_representation='5d6 + 10'))
    roll = a.roll()
    print(roll.value)
    assert 16 <= roll.value <= 40
