from telebot import types
import telebot
import string
import random
from abc import ABC, abstractmethod

lobbies = []
players = []
words = ["Albert Einstein", "apple", "pen"]
definitions = ["lemon", "phone", "cup"]


class Player:
    def __init__(self, name, id, points=0):
        self.__in_lobby = False
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

    def add_id(self, id):
        if isinstance(id, int):
            self.__ides.append(id)
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


class Guessword(Lobby, Game):
    def __init__(self, name, people_amount=0, time=0):
        self.word = ""
        super().__init__(name, people_amount=0, time=0)

    def start_game(self):
        pass

    def is_winner(self, word):
        if self.word == word:
            return True
        return False

    def random_word(self):
        self.word = words[random.randint(0, len(words) - 1)]


class Encyclopedia(Lobby, Game):
    def __init__(self, name, people_amount=0, time=0):
        self.definition = ""
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

    def random_word(self):
        self.definition = definitions[random.randint(0, len(definitions) - 1)]


def lobby_name():
    name = []
    for i in string.ascii_lowercase:
        if random.randint(0, 5) == 3:
            name.append(i)
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


def start_buttons():
    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text="Create lobby", callback_data="type lobby")
    but_2 = types.InlineKeyboardButton(text="Join lobby", callback_data="Join lobby")
    key.add(but_1, but_2)
    return key


def admin_lobby_buttons():
    key = types.InlineKeyboardMarkup()
    txt = ""
    for player in players:
        for lobby in lobbies:
            if isinstance(player, Admin):
                if player.get_name_lobby() == lobby.get_name():
                    txt += "Lobby name: " + lobby.get_name() + "\nPeople " + str(len(lobby.get_ides())) + " / " + str(lobby.people_amount) + \
                           "\nTime - " + str(lobby.time_game) + " min"

    but_1 = types.InlineKeyboardButton(text="Start game", callback_data="start game")
    but_2 = types.InlineKeyboardButton(text="Update", callback_data="admin lobby menu")
    key.add(but_1, but_2)
    return key, txt


class Bot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token=token)

        @self.bot.message_handler(commands=["start"])
        def start(message):
            self.bot.send_message(message.chat.id, "Choose action", reply_markup=start_buttons())

        @self.bot.callback_query_handler(func=lambda call: call.data == "start")
        def start_callback(call):
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.send_message(call.from_user.id, "Choose action", reply_markup=start_buttons())

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
            key = types.InlineKeyboardMarkup()
            txt = ""
            for player in players:
                for lobby in lobbies:
                    if player.get_name_lobby() == lobby.get_name():
                        txt += "People " + str(len(lobby.get_ides())) + " / " + str(lobby.people_amount) + \
                               "\nTime - " + str(lobby.time_game) + " min"

            but_1 = types.InlineKeyboardButton(text="Start game", callback_data="start game")
            but_2 = types.InlineKeyboardButton(text="Update", callback_data="admin lobby menu")
            key.add(but_1, but_2)
            self.bot.send_message(call.from_user.id, "You are in lobby\n" + txt, reply_markup=key)

        @self.bot.callback_query_handler(func=lambda call: call.data == "admin lobby menu")
        def admin_lobby_menu(call):
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            key, txt = admin_lobby_buttons()
            self.bot.send_message(call.from_user.id, "You are in lobby\n" + txt, reply_markup=key)

        @self.bot.message_handler(commands=[""])
        def admin_lobby_menu(message):
            key, txt = admin_lobby_buttons()
            self.bot.send_message(message.chat.id, "You are in lobby\n" + txt, reply_markup=key)

        @self.bot.callback_query_handler(func=lambda call: call.data == "Guess the word")
        def game_guess_word(call):
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            key = types.InlineKeyboardMarkup()
            name = lobby_name()
            lobbies.append(Guessword(name))
            add_user(call.from_user.id, call.message.chat.username, name, 1)
            self.bot.send_message(call.from_user.id, "Input amount of people", reply_markup=key)

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
                                    lobby.people_amount = int(message.text)
                                    lobby.add_id(message.from_user.id)
                                    self.bot.send_message(message.from_user.id, "Input time in the minutes")
                                    player.change_status_people()
                                    player.change_status_time()
                                else:
                                    self.bot.send_message(message.from_user.id, "Not correct form")

                    elif isinstance(player, Admin) and player.get_status_time():
                        for lobby in lobbies:
                            if player.get_name_lobby() == lobby.get_name():
                                if message.text.isdigit():
                                    lobby.time_game = int(message.text)
                                    player.change_status_time()
                                    player.is_in_lobby = True
                                    admin_lobby_menu(message)
                                else:
                                    self.bot.send_message(message.from_user.id, "Not correct form")

                    elif isinstance(player, Player) and (not player.is_in_lobby):
                        exist = False
                        for lobby in lobbies:
                            if lobby.get_name() == message.text:
                                print(player.is_in_lobby)
                                self.bot.send_message(message.from_user.id, "Good")
                                lobby.add_id(message.from_user.id)
                                player.is_in_lobby = True
                                print(player.is_in_lobby)
                                exist = True
                        if not exist:
                            self.bot.send_message(message.from_user.id, "There is no such lobby")
                            start(message)

    def start(self):
        self.bot.polling()


if __name__ == "__main__":
    bot = Bot("1319075806:AAEdpZth2FhpI_Us7eQ8vRO6Vl51LAcrvFo")
    bot.start()

