class Player:
    __count = 0

    def __init__(self, name, points=0):
        Player.__count += 1
        self.__id = Player.__count
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

    def get_id(self):
        return self.__id


class Lobby:
    def __init__(self, people_amount, time, name, password):
        self.__ides = []
        self.__people_amount = people_amount
        self.__time = time
        self.__name = name
        self.__password = password

    def start_game(self):
        pass

    def get_people_amount(self):
        return self.__people_amount

    def get_time(self):
        return self.__time

    def get_name(self):
        return self.__name

    def get_password(self):
        return self.__password

    def add_id(self, id):
        if isinstance(id, int):
            self.__ides.append(id)
        else:
            raise ValueError("Id must be int type")

    def get_ides(self):
        return self.__ides

    def is_winner(self):
        pass
