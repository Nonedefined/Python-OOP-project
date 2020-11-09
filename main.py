from telebot import types
import telebot
import string
import random
import datetime
import time
from abc import ABC, abstractmethod


lobbies = []
players = []
words = ["apple", "usa"]
all_hints = {"apple": ["It is fruit", "It grows on trees", "It can be yellow, green, red color",
                       "There is company with the such name"],
             "usa": ["It is a country", "Independence Day is celebrated on July 4", "Country name is an abbreviation",
                     "It borders on Canada, Mexico and Russia"]}

definitions = ["lemon", "phone", "cup"]


class Player:
    def __init__(self, name, id, points=0):
        self.__in_lobby = False
        self.__guessing_word = False
        self.__word = ""
        self.__id = id
        self.__name = name
        self.__points = points

    @property
    def user_name(self):
        return self.__name

    @user_name.setter
    def user_name(self, name):
        if isinstance(name, str):
            self.__name = name
        else:
            raise ValueError("Name must be str type")

    @property
    def user_points(self):
        return self.__points

    @user_points.setter
    def user_points(self, points):
        if isinstance(points, int):
            self.__points = points
        else:
            raise ValueError("Points must be int type")

    @property
    def is_in_lobby(self):
        return self.__in_lobby

    @is_in_lobby.setter
    def is_in_lobby(self, in_lobby):
        self.__in_lobby = in_lobby

    @property
    def is_guessing_word(self):
        return self.__guessing_word

    @is_guessing_word.setter
    def is_guessing_word(self, guessing_word):
        self.__guessing_word = guessing_word

    def get_word(self):
        return self.__word

    def set_word(self, word):
        self.__word = word

    def get_id(self):
        return self.__id


class Admin(Player):
    def __init__(self, name_lobby, name, id, points=0):
        self.__status_people = True
        self.__status_time = False
        self.__name_lobby = name_lobby
        Player.__init__(self, name, id, points)

    def get_name_lobby(self):
        return self.__name_lobby

    def get_status_people(self):
        return self.__status_people

    def change_status_people(self):
        self.__status_people = not self.__status_people

    def get_status_time(self):
        return self.__status_time

    def change_status_time(self):
        self.__status_time = not self.__status_time


class Lobby(ABC):
    def __init__(self, name, people_amount=0, time=0):
        self.__ides = []
        self.__people_amount = people_amount
        self.__time = time
        self.__name = name

    @property
    def people_amount(self):
        return self.__people_amount

    @people_amount.setter
    def people_amount(self, amount):
        self.__people_amount = amount

    @property
    def time_game(self):
        return self.__time

    @time_game.setter
    def time_game(self, time):
        self.__time = time

    def get_name(self):
        return self.__name

    def add_id(self, id_player):
        if isinstance(id_player, int):
            self.__ides.append(id_player)
            self.__ides = list(set(self.__ides))
        else:
            raise ValueError("Id must be int type")

    def get_ides(self):
        return self.__ides


class Game(ABC):
    @abstractmethod
    def start_game(self):
        pass

    @abstractmethod
    def is_winner(self, *args):
        pass

    @abstractmethod
    def random_word(self):
        pass

    @abstractmethod
    def get_word(self):
        pass


class Guessword(Lobby, Game):
    def __init__(self, name, people_amount=0, time=0):
        self.__word = ""
        self.__hints = []
        self.__winner_id = 0
        self.__is_winner = False
        super().__init__(name, people_amount=0, time=0)

    def start_game(self):
        pass

    def change_is_winner(self):
        self.__is_winner = True

    def is_winner(self):
        return self.__is_winner

    def set_winner(self, id):
        self.__winner_id = id

    def get_winner(self):
        return self.__winner_id

    def get_word(self):
        return self.__word

    def get_hints(self):
        return self.__hints

    def random_word(self):
        self.__word = words[random.randint(0, len(words) - 1)]
        self.__hints = all_hints[self.__word]


class Encyclopedia(Lobby, Game):
    def __init__(self, name, people_amount=0, time=0):
        self.__definition = ""
        super().__init__(name, people_amount=0, time=0)

    def start_game(self):
        pass

    def is_winner(self, players_with_points):
        max_points = 0
        id_player = 0
        for player in players_with_points:
            if max_points < player.user_points:
                max_points = player.user_points
                id_player = player.get_id()
        return max_points, id_player

    def get_word(self):
        return self.__definition

    def random_word(self):
        self.__definition = definitions[random.randint(0, len(definitions) - 1)]


def lobby_name():
    name = [string.ascii_lowercase[random.randint(0, 25)] for i in range(5)]
    random.shuffle(name)
    return ''.join(name)


def add_user(id, name, lobby_name=None, choice=None):
    for i in players:
        if id == i.get_id():
            players.remove(i)
    if not choice:
        players.append(Player(name, id))
    else:
        players.append(Admin(lobby_name, name, id))


class TimeNotInRangeError(Exception):
    def __init__(self, time, message="is not in range"):
        self.time = time
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.time} {self.message}'


class Bot:
    @staticmethod
    def lobby_text():
        txt = ""
        for player in players:
            for lobby in lobbies:
                if isinstance(player, Admin):
                    if player.get_name_lobby() == lobby.get_name():
                        txt += "Lobby name: " + lobby.get_name() + "\nPeople " + str(
                            len(lobby.get_ides())) + " / " + str(lobby.people_amount) + \
                               "\nTime for one hint - " + str(lobby.time_game) + " sec"
        return txt

    @staticmethod
    def start_buttons():
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text="Create lobby", callback_data="type lobby")
        but_2 = types.InlineKeyboardButton(text="Join lobby", callback_data="Join lobby")
        key.add(but_1, but_2)
        return key

    def __init__(self, token):
        self.bot = telebot.TeleBot(token=token)

        @self.bot.message_handler(commands=["start"])
        def start(message):
            self.bot.send_message(message.chat.id, "Choose action", reply_markup=self.start_buttons())

        @self.bot.callback_query_handler(func=lambda call: call.data == "start")
        def start_callback(call):
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.send_message(call.from_user.id, "Choose action", reply_markup=self.start_buttons())

        @self.bot.callback_query_handler(func=lambda call: call.data == "type lobby")
        def type_lobby(call):
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton(text="Guess the word", callback_data="Guess the word")
            but_2 = types.InlineKeyboardButton(text="Encyclopedia", callback_data="Guess the word")
            but_3 = types.InlineKeyboardButton(text="Back", callback_data="start")
            key.add(but_1, but_2)
            key.add(but_3)
            self.bot.send_message(call.from_user.id, "Choose the game", reply_markup=key)

        @self.bot.callback_query_handler(func=lambda call: call.data == "lobby menu")
        def lobby_menu(call):
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton(text="Update", callback_data="lobby menu")
            key.add(but_1)
            txt = self.lobby_text()
            self.bot.send_message(call.from_user.id, "Please wait for the admin to start the game.\n" + txt,
                                  reply_markup=key)

        @self.bot.message_handler(commands=[""])
        def lobby_menu(message):
            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton(text="Update", callback_data="lobby menu")
            key.add(but_1)
            txt = self.lobby_text()
            self.bot.send_message(message.chat.id, "Please wait for the admin to start the game.\n" + txt, reply_markup=key)

        @self.bot.callback_query_handler(func=lambda call: call.data == "admin lobby menu")
        def admin_lobby_menu(call):
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            txt = self.lobby_text()
            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton(text="Update", callback_data="admin lobby menu")
            but_2 = types.InlineKeyboardButton(text="Start game", callback_data="start game")
            key.add(but_1, but_2)
            self.bot.send_message(call.from_user.id, txt, reply_markup=key)

        @self.bot.message_handler(commands=[""])
        def admin_lobby_menu(message):
            txt = self.lobby_text()
            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton(text="Update", callback_data="admin lobby menu")
            but_2 = types.InlineKeyboardButton(text="Start game", callback_data="start game")
            key.add(but_1, but_2)
            self.bot.send_message(message.chat.id, txt, reply_markup=key)

        @self.bot.callback_query_handler(func=lambda call: call.data == "start game")
        def start_game(call):
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            for player in players:
                for game in lobbies:
                    if isinstance(player, Admin):
                        if player.get_name_lobby() == game.get_name():
                            game.random_word()
                            now = datetime.datetime.now()
                            now_sec = now.second
                            hints = game.get_hints()
                            counter = 0
                            for pl in players:
                                if pl.get_id() in game.get_ides():
                                    pl.is_guessing_word = True
                            while True:
                                is_time = datetime.datetime.now()
                                is_time_sec = is_time.second
                                if (is_time_sec - now_sec) > game.time_game and counter < len(hints):
                                    for pl in game.get_ides():
                                        self.bot.send_message(pl, hints[counter])
                                    counter += 1
                                    now = datetime.datetime.now()
                                    now_sec = now.second
                                elif (is_time_sec - now_sec) < 0:
                                    now = datetime.datetime.now()
                                    now_sec = now.second
                                    is_time = datetime.datetime.now()
                                    is_time_sec = is_time.second
                                if game.is_winner():
                                    for pl in players:
                                        if pl.get_id() in game.get_ides():
                                            pl.is_guessing_word = True
                                            self.bot.send_message(pl.get_id(), f"We have a [winner](tg://user?id={str(game.get_winner())})", parse_mode='Markdown')
                                    lobbies.remove(game)
                                    break

        @self.bot.callback_query_handler(func=lambda call: call.data == "Guess the word")
        def game_guess_word(call):
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            key = types.InlineKeyboardMarkup()
            name = lobby_name()
            lobbies.append(Guessword(name))
            add_user(call.from_user.id, call.message.chat.username, name, 1)
            self.bot.send_message(call.from_user.id, "Input amount of people 2-100", reply_markup=key)

        @self.bot.callback_query_handler(func=lambda call: call.data == "Join lobby")
        def join_lobby(call):
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            add_user(call.from_user.id, call.message.chat.username)
            self.bot.send_message(call.from_user.id, "Input lobby name")

        @self.bot.message_handler()
        def message_handler(message):
            for player in players:
                if player.get_id() == message.from_user.id:
                    if isinstance(player, Admin) and player.get_status_people():
                        for lobby in lobbies:
                            if player.get_name_lobby() == lobby.get_name():
                                if message.text.isdigit():
                                    try:
                                        if 2 <= int(message.text) <= 100:
                                            lobby.people_amount = int(message.text)
                                            lobby.add_id(message.from_user.id)
                                            self.bot.send_message(message.from_user.id, "Input time for one hint 10-30")
                                            player.change_status_people()
                                            player.change_status_time()
                                        else:
                                            raise TimeNotInRangeError(int(message.text))
                                    except TimeNotInRangeError as e:
                                        self.bot.send_message(message.from_user.id, e)
                                else:
                                    self.bot.send_message(message.from_user.id, "Not correct form")

                    elif isinstance(player, Admin) and player.get_status_time():
                        for lobby in lobbies:
                            if player.get_name_lobby() == lobby.get_name():
                                if message.text.isdigit():
                                    try:
                                        if 10 <= int(message.text) <= 30:
                                            lobby.time_game = int(message.text)
                                            player.change_status_time()
                                            player.is_in_lobby = True
                                            admin_lobby_menu(message)
                                        else:
                                            raise TimeNotInRangeError(int(message.text))
                                    except TimeNotInRangeError as e:
                                        self.bot.send_message(message.from_user.id, e)

                                else:
                                    self.bot.send_message(message.from_user.id, "Not correct form")

                    elif isinstance(player, Player) and (not player.is_in_lobby):
                        exist = False
                        for lobby in lobbies:
                            if lobby.get_name() == message.text:
                                lobby.add_id(message.from_user.id)
                                player.is_in_lobby = True
                                exist = True
                                lobby_menu(message)
                        if not exist:
                            self.bot.send_message(message.from_user.id, "There is no such lobby")
                            start(message)

                    elif player.is_guessing_word:
                        for lobby in lobbies:
                            if message.from_user.id in lobby.get_ides():
                                message.text = message.text.lower()
                                player.set_word(message.text)
                                if message.text == lobby.get_word():
                                    self.bot.send_message(message.from_user.id, "Right")
                                    lobby.set_winner(message.from_user.id)
                                    lobby.change_is_winner()
                                else:
                                    self.bot.send_message(message.from_user.id, "Wrong")

    def start(self):
        self.bot.polling()


if __name__ == "__main__":
    while True:
        try:
            bot = Bot("1319075806:AAEdpZth2FhpI_Us7eQ8vRO6Vl51LAcrvFo")
            bot.start()
        except Exception as e:
            print(e)
            time.sleep(15)
