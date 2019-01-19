from dataclasses import dataclass, field, replace, asdict
import typing
from uuid import UUID, uuid4
from basic_types import Action, Value
from dacite import from_dict


@dataclass(frozen=True)
class Character:
    id: UUID = field(default_factory=uuid4)
    name: str = 'Noname character'
    strength: int = 0
    dexterity: int = 0

    relationships: typing.Dict['Character', tuple] = field(default_factory=dict)

    def change_field(self, *, field_name: str, new_value: typing.Any) -> 'Character':
        if field_name not in self.__dict__:
            return self

        self_as_dict = asdict(self)
        self_as_dict[field_name] = new_value
        return from_dict(data_class=Character, data=self_as_dict)

    def change_several_fields(self, *, name_value_dict: typing.Dict[str, typing.Any]) -> 'Character':
        self_as_dict = asdict(self)
        for field_name, new_value in name_value_dict.items():
            if field_name not in self.__dict__:
                continue

            self_as_dict[field_name] = new_value
        return from_dict(data_class=Character, data=self_as_dict)

    @staticmethod
    def change_character_field_action(*,
                                      container_value: Value,
                                      field_name: str,
                                      new_field_value: typing.Any,
                                      ) -> typing.Optional[Action]:
        old_character = container_value.value
        if not isinstance(old_character, Character):
            return None

        new_character = old_character.change_field(field_name=field_name, new_value=new_field_value)
        return Action(previous_value=container_value,
                      actual_value=replace(container_value, value=new_character),
                      name=f'Action for change character "{old_character.name}" field '
                      f'{field_name} to {new_field_value}')

    @staticmethod
    def change_character_several_fields_action(*,
                                               container_value: Value,
                                               changing_dict: typing.Dict[str, typing.Any],
                                               ) -> typing.Optional[Action]:
        old_character = container_value.value
        if not isinstance(old_character, Character):
            return None

        new_character = old_character.change_several_fields(name_value_dict=changing_dict)
        return Action(previous_value=container_value,
                      actual_value=replace(container_value, value=new_character),
                      name=f'Action for change character "{old_character.name}" field: {changing_dict}')


if __name__ == '__main__':
    print(Character(name='Kolobok'))
