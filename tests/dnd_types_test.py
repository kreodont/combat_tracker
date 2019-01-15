from dnd_types import Roll, Formula, Action


def test_simple_attack():
    r = Roll(
            name='Simple attack',
            id='1',
            formula=Formula(
                    id='1',
                    name='Simple Formula',
                    text_representation='5d6 + 10'),
            type='attack',
            main_action=Action(id='4'))
    print(r.value)
    assert 16 <= r.value <= 40
