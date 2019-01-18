from dataclasses import dataclass, field, replace
import typing
from basic_types import Action, Value, Timer
from uuid import UUID
import pickle


@dataclass(frozen=True)
class Game:
    """
    Requirements:
    1. Game is the sequence of actions and objects
    2. New object creation is an action from sequence of actions
    3. Objects are values that store different objects?
    4. Full text search must be supported by name, short_description, full_description
    """
    actions_list: typing.Tuple[Action, ...] = field(default_factory=tuple)
    objects_dict: typing.Dict[UUID, Value] = field(default_factory=dict)
    timer: Timer = field(default_factory=Timer)
    name: str = 'Noname game'

    @property
    def last_action(self) -> typing.Optional[Action]:
        if not self.actions_list:
            return None
        return self.actions_list[-1]

    def make_action(self, *, action: Action) -> 'Game':
        new_game_state = self
        # Object did't exist before that action

        # If object is not in Game, but the action is not an action for object creation (previous is not None)
        # That can be if creation action was reverted, so object is no longer exists
        if action.actual_value.id not in self.objects_dict and action.previous_value is not None:
            return self  # Do nothing

        new_game_state = replace(new_game_state,
                                 objects_dict={**new_game_state.objects_dict,
                                               **{action.actual_value.id: action.actual_value}},
                                 actions_list=new_game_state.actions_list + (action,))

        return new_game_state

    def cancel_action(self, *, action_id: UUID) -> 'Game':
        list_actions_to_cancel = [a for a in self.actions_list if a.id == action_id]
        if not list_actions_to_cancel:
            return self

        action_to_cancel = list_actions_to_cancel[0]
        number_action_to_cancel = self.actions_list.index(action_to_cancel)

        # if the action was new object creation, we then must ignore all actions made with this object
        if action_to_cancel.previous_value is None:
            ignoring_object_id = action_to_cancel.actual_value.id
        else:
            ignoring_object_id = None

        game_with_action_cancelled = Game()
        for action in self.actions_list[:number_action_to_cancel]:
            game_with_action_cancelled = game_with_action_cancelled.make_action(action=action)

        for action in self.actions_list[number_action_to_cancel + 1:]:
            if ignoring_object_id and action.previous_value and action.previous_value.id == ignoring_object_id:
                continue
            game_with_action_cancelled = game_with_action_cancelled.make_action(action=action)

        return game_with_action_cancelled

    def full_text_search(self, *, text_to_search) -> typing.Dict[UUID, Value]:
        return {k: v for k, v in self.objects_dict.items() if
                text_to_search in v.name or
                text_to_search in v.short_description or
                text_to_search in v.full_description or
                text_to_search in str(v.value)}

    def save_to_disk(self, *, filename) -> str:
        try:
            with open(filename, 'wb') as output_file:
                pickle.dump(self, output_file)
                return 'OK'
        except Exception as e:
            return str(e)

    @staticmethod
    def load_from_disk(*, filename) -> 'Game':
        try:
            with open(filename, 'rb') as input_file:
                loaded_game = pickle.load(input_file)
                return loaded_game

        except Exception as e:
            print(e)
            return Game()


if __name__ == '__main__':
    game = Game()
    print(game)
