from game import Game
from character import Character


def test_changing_character_parameters():
    game = Game()
    game = game.add_character(character_name='Kolobok')
    game = game.make_action(
            action=Character.change_character_field_action(
                    container_value=list(game.objects_dict.values())[0],
                    field_name='strength',
                    new_field_value=16))
    kolobok = list(game.objects_dict.values())[0].value  # type: Character
    assert kolobok.strength == 16
    game = game.cancel_action_by_number(action_number=1)  # canceling changing strength to 16
    kolobok = list(game.objects_dict.values())[0].value
    assert kolobok.strength == 0
    game = game.cancel_last_action()
    assert len(game.objects_dict) == 0


def test_change_several_parameters():
    game = Game()
    game = game.add_character(character_name='Kolobok')
    game = game.make_action(
            action=Character.change_character_several_fields_action(
                    container_value=list(game.objects_dict.values())[0],
                    changing_dict={
                        'strength': 14,
                        'dexterity': 8,
                        'stupidity': 22,
                    }))
    kolobok = list(game.objects_dict.values())[0].value  # type: Character
    assert kolobok.strength == 14
    assert kolobok.dexterity == 8
    assert not hasattr(kolobok, 'stupidity')
