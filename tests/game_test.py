from game import Game
from basic_types import Value, Action, change_value
from character import Character


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


def test_cancel_object_creation_action():
    game = Game()
    create_action = Action(actual_value=Value(value=42))
    game = game.make_action(action=create_action)
    created_value = game.last_action.actual_value
    game = game.make_action(
            action=change_value(
                    value_to_change=created_value,
                    changing_function=lambda x: Value(value=43),
            ),
    )
    game = game.make_action(
            action=change_value(
                    value_to_change=created_value,
                    changing_function=lambda x: Value(value=43),
            ),
    )
    assert len(game.actions_list) == 3
    assert len(game.objects_dict) == 1
    game = game.make_action(action=Action(actual_value=Value(value='Another value')))
    assert len(game.actions_list) == 4
    assert len(game.objects_dict) == 2
    game = game.cancel_action(action_id=create_action.id)
    assert len(game.actions_list) == 1
    assert len(game.objects_dict) == 1


def test_save_and_load():
    game = Game()
    game = game.make_action(action=Action(actual_value=Value(value=42)))
    save_game_result = game.save_to_disk(filename='test_save_and_load.game')
    assert save_game_result == 'OK'
    loaded_game = Game.load_from_disk(filename='test_save_and_load.game')
    assert loaded_game == game


def test_that_long_actions_change_timer():
    game = Game()
    game = game.make_action(action=Action(actual_value=Value(value=42), duration_in_seconds=13))
    assert game.timer.seconds_passed == 13


def test_that_canceling_long_action_rolls_back_timer():
    game = Game()
    long_action = Action(actual_value=Value(value=42), duration_in_seconds=13)
    game = game.make_action(action=long_action)
    assert game.timer.seconds_passed == 13
    game = game.cancel_action(action_id=long_action.id)
    assert game.timer.seconds_passed == 0


def test_that_it_is_possible_to_add_2_characters_with_same_name():
    game = Game()
    game = game.add_character(character_name='Kolobok')
    assert len(game.objects_dict) == 1
    game = game.add_character(character_name='Kolobok')
    assert len(game.objects_dict) == 2
    character_1 = list(game.objects_dict.values())[0].value
    character_2 = list(game.objects_dict.values())[1].value
    assert character_1.name == character_2.name == 'Kolobok'
    game = game.cancel_action_by_number(action_number=0)
    assert len(game.objects_dict) == 1


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
