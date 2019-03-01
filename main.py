import json
from random import randint, choice
from re import sub

from vk_api import VkApi, AuthError
from vk_api.longpoll import VkLongPoll, VkEventType


class Helper:
    @staticmethod
    def normalize_phrase(request):
        request = sub(r'[-—,.:?]', '', request)  # Удалить знаки припенания
        request = sub(r'\s+', ' ', request)  # Заменить повторяющиеся пробелы на один
        request = request.replace('ё', 'е')  # Заменить букву `ё`
        request = request.strip()  # Удалить пробельные символы в начале и в конце фразы
        request = request.lower()  # Привести фразу к нижнему регистру
        return request


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

    @classmethod
    def get_proverbs(cls):
        return {
            "Два сапога — пара,": "да оба на левую ногу надеты",
            "Собаку съел,": "да хвостом подавился",
            "Голод не тётка,": "пирожка не даст",
            "Губа не дура,": "язык не лопатка: знает, что горько, что сладко",
            "Дуракам закон не писан,": "если писан — то не читан, если читан — то не понят, если понят — то не так",
            "Забот полон рот,": "а перекусить нечего",
            "Заварил кашу —": "не жалей масла",
            "Кто старое помянет, тому глаз вон;": "а кто забудет — тому два",
            "Москва слезам не верит,": "ей дело подавай",
            "Не всё коту масленица,": "будет и Великий пост",
            "Ни рыба, ни мясо — ": "ни кафтан, ни ряса",
            "Новая метла чисто метёт,": "а обломается — под лавкой валяется",
            "Первый парень на деревне,": "а деревня в два двора",
            "Попытка — не пытка,": "а спрос — не беда",
            "Простота хуже воровства,": "если она не от ума. а от заумия",
            "Пьяному море по колено,": "а лужа по уши",
            "Рука руку моет,": "а две руки — лицо",
            "Утро вечера мудренее —": "жена мужа удалее",
            "Чем чёрт не шутит,": "когда Бог спит",
            "Чудеса в решете:": "дыр много, а вылезть негде",
            "Язык мой — враг мой:": "прежде ума рыщет, беды ищет",
            "Куда идём мы с Пяточком?": "Большой-большой секрет!",
        }


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
            'пословица': cls.proverb,
        }

    @classmethod
    def cant_understand(cls, request):
        answers = [
            'Да, даа...',
            'Чего??',
            'Не поняяятно :)',
            'Я такого не проходила...',
        ]
        return choice(answers)

    @classmethod
    def greet(cls, request):
        answers = [
            'Всем чмоки в этом чатике! <3',
            'Гутентаг! :)',
            'Всем чмоки в этом чатике! <3',
            'Привет, привет!',
            'Бонжур! :)',
            'Акунаматата!',
        ]
        return choice(answers)

    @classmethod
    def get_closest_game(cls, request):
        unknown_answer = [
            'Пока не известно.',
            'Не знаю...',
        ]
        answer = Model.get_closest_game()
        if not answer:
            answer = choice(unknown_answer)
        return answer

    @classmethod
    def who_is_capitan(cls, request):
        captain = Model.get_random_team_member()['name']
        answers = [
            'Идёт {}. Без вопросов.',
            '{}. И никаких там "нихачу, нибуду"!',
            'Ммм... {}!',
        ]
        return choice(answers).format(captain)

    @classmethod
    def proverb(cls, request):
        request = request.lower().split('пословица')[1]
        request = Helper.normalize_phrase(request)
        proverbs = Model.get_proverbs()
        for proverb in proverbs:
            if Helper.normalize_phrase(proverb) == request:
                return f'{proverb} {proverbs[proverb]}'
        return f'Что за пословица такая?... Не знаю.'

    @classmethod
    def what_can_you_do(cls, request):
        answer = [
            'Я умею:',
            '',
            '* Здороваться — Напишите "Привет"',
            '* Подсказать ближайшую игру — Спросите "Когда ближайшая игра?"',
            '* Назначить капитана — Спросите "Кто капитанит?"',
            '* Закончить пословицу — Напишите "Пословица" и начало пословицы',
            '',
            '* Приносить удачу :)',
            '* Учусь собирать статистику игр...',
        ]
        return '\n'.join(answer)


class Controller:
    commands_dict = Bot.get_commands_dict()

    @classmethod
    def parse_request(cls, request):
        for command, action in cls.commands_dict.items():
            if command in request.lower():
                return action(request)
        return Bot.cant_understand(request)


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
