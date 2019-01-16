from game import Game
from basic_types import Value, Action, change_value


def test_new_game_creation():
    game = Game()
    assert game.name == 'Noname game'
    assert len(game.objects_dict) == 0
    assert len(game.actions_list) == 0


def test_making_action():
    game = Game()
    new_value = Value(value="12 негритят")
    game = game.make_action(action=Action(actual_value=new_value))
    assert game.last_action.actual_value.value == '12 негритят'
    assert list(game.objects_dict.values())[0].value == '12 негритят'


def test_that_if_object_id_is_not_in_game_and_previous_value_is_not_none_action_has_no_effect():
    game = Game()
    new_value = Value(value=10)
    changed_value = change_value(value_to_change=new_value, action_to_perform=Action(), rollback_function=None)
    print(changed_value)
