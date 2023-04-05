import abc


# abstract game mode class
class GameMode(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    def switch_to(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    def exit(self):
        pass


class ClassicGameMode(GameMode):

    def run(self):
        pass
