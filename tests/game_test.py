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
    changing_action = Action(actual_value=new_value)
    game = game.make_action(action=changing_action)
    assert game.last_action.actual_value.value == '12 негритят'
    assert len(game.objects_dict) == 1
    assert list(game.objects_dict.values())[0].value == '12 негритят'


def test_that_if_object_id_is_not_in_game_and_previous_value_is_not_none_action_has_no_effect():
    game = Game()
    value = Value(value=10)
    changed_value = change_value(value_to_change=value).actual_value
    game = game.make_action(action=Action(previous_value=value, actual_value=changed_value))
    assert len(game.objects_dict) == 0
    assert len(game.actions_list) == 0


def test_that_if_value_was_in_game_it_can_be_changed_with_action():
    game = Game()
    game = game.make_action(action=Action(actual_value=Value(value=13)))
    assert game.last_action.actual_value.value == 13
    game = game.make_action(
            action=change_value(
                    value_to_change=game.last_action.actual_value,
                    changing_function=lambda x: Value(value=14)),
    )
    assert game.last_action.actual_value.value == 14
    assert len(game.actions_list) == 2
    assert len(game.objects_dict) == 1


def test_cancel_last_action():
    game = Game()
    game = game.make_action(action=Action(actual_value=Value(value=42)))

    assert game.last_action.actual_value.value == 42
    action = change_value(
                    value_to_change=game.last_action.actual_value,
                    changing_function=lambda x: Value(value=x.value * 10),
    )
    game_with_changed_value = game.make_action(action=action)
    assert game_with_changed_value.last_action.actual_value.value == 420
    game_with_canceled_last_action = game_with_changed_value.cancel_action(action_id=action.id)
    assert game_with_canceled_last_action.last_action.actual_value.value == 42
    assert len(game_with_canceled_last_action.actions_list) == 1
    assert len(game_with_canceled_last_action.objects_dict) == 1
    assert game_with_canceled_last_action.last_action.actual_value == game.last_action.actual_value
