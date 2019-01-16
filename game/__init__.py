from dataclasses import dataclass, field, replace
import typing
from basic_types import Action, Value
from uuid import UUID


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


if __name__ == '__main__':
    game = Game()
    print(game)
