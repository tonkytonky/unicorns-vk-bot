from random import randint, choice
import json

from vk_api import VkApi, AuthError
from vk_api.longpoll import VkLongPoll, VkEventType


class Model:
    TEAM_INFO_PATH = 'team_info.json'

    @staticmethod
    def get_random_int():
        """Получить случайное целое число в диапазоне до int32"""
        return randint(0, 2 ** 32 - 1)

    @classmethod
    def load_team_info(cls):
        with open(cls.TEAM_INFO_PATH, 'r', encoding='utf-8') as team_info_file:
            return json.load(team_info_file)

    @classmethod
    def get_closest_game(cls):
        team_info = cls.load_team_info()
        return team_info['closest_game']

    @classmethod
    def get_random_team_member(cls):
        team_info = cls.load_team_info()
        return choice(team_info['team_members'])


class Bot:
    LOGIN, PASSWORD = 'yaprostosmotryu@ya.ru', 'uniCORNS'
    BOT_ID = 532316079

    @classmethod
    def get_commands_dict(cls):
        return {
            'привет': cls.greet,
            'ближайшая игра': cls.get_closest_game,
            'капитанит': cls.who_is_capitan,
            'умеешь': cls.what_can_you_do,
            'понятно': cls.what_can_you_do,
        }

    @classmethod
    def cant_understand(cls):
        answers = [
            'Да, даа...',
            'Чего??',
            'Чего??',
            'Не поняяятно :)',
            'Не поняяятно :)',
            'Не поняяятно :)',
            'Я такого не проходила...',
        ]
        return choice(answers)

    @classmethod
    def greet(cls):
        answers = [
            'Всем чмоки в этом чатике! <3',
            'Всем чмоки в этом чатике! <3',
            'Привет, привет!',
            'Бонжур! :)',
            'Гутентаг! :)',
        ]
        return choice(answers)

    @classmethod
    def get_closest_game(cls):
        return Model.get_closest_game()

    @classmethod
    def who_is_capitan(cls):
        captain = Model.get_random_team_member()['name']
        answers = [
            'Сегодня идёт {}. Без вопросов.',
            '{}. И никаких там "нихачу, нибуду"!',
            '{}. И никаких там "нихачу, нибуду"!',
            '{}. И никаких там "нихачу, нибуду"!',
            'Ммм... {}!'
            'Ммм... {}!'
        ]
        return choice(answers).format(captain)

    @classmethod
    def what_can_you_do(cls):
        answer = [
            'Я умею:',
            '',
            '* Здороваться — Напишите "Привет"',
            '* Подсказать ближайшую игру — Спросите "Когда ближайшая игра?"',
            '* Назначить капитана — Спросите "Кто капитанит?"',
            '* Приносить удачу :)',
            '* Учусь собирать статистику игр...',
        ]
        return '\n'.join(answer)


class Controller:
    @classmethod
    def parse_request(cls, request):
        commands_dict = Bot.get_commands_dict()
        for command, action in commands_dict.items():
            if command in request.lower():
                return action()
        return Bot.cant_understand()


def main():
    """
    Пример использования longpoll
    https://vk.com/dev/using_longpoll
    https://vk.com/dev/using_longpoll_2
    """

    vk_api = VkApi(Bot.LOGIN, Bot.PASSWORD)
    vk_method = vk_api.get_api()

    try:
        vk_api.auth(token_only=True)
    except AuthError as error_msg:
        print(error_msg)
        return

    longpoll = VkLongPoll(vk_api)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and not event.from_me:
            # Личное сообщение
            if event.from_user:
                # Добавить логирование
                # print(f'Личное сообщение от {event.user_id}:')
                # print(f'    {event.text}')
                answer = Controller.parse_request(event.text)
                vk_method.messages.send(
                    user_id=event.user_id,
                    message=answer,
                    random_id=Model.get_random_int()
                )
            # Упоминание в чате
            elif event.from_chat and hasattr(event, 'mentions') and Bot.BOT_ID in event.mentions:
                # Добавить логирование
                # print(f'Сообщение в чате {event.chat_id} от {event.user_id}:')
                # print(f'    {event.text}')
                # answer = choice(Bot.ANSWERS)
                # print(f'    Ответ: {answer}')
                answer = Controller.parse_request(event.text)
                vk_method.messages.send(
                    chat_id=event.chat_id,
                    message=answer,
                    random_id=Model.get_random_int()
                )
            # Остальные сообщения
            else:
                # Добавить логирование
                # print(f'Сообщение в чате {event.chat_id} от {event.user_id}:')
                # print(f'    {event.text}')
                pass


if __name__ == '__main__':
    main()
