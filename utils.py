import os
import platform
from colorama import Fore

T_INFO = Fore.LIGHTCYAN_EX
T_WARNING = Fore.YELLOW
T_SUCCESS = Fore.GREEN
T_GOODBYE = Fore.BLUE
T_RESET = Fore.RESET
main_menu_options = {
    1: 'Получить координаты по адресу',
    2: 'Настройки',
    3: 'О программе',
    0: 'Выход',
}
settings_menu_options = {
    1: 'Добавить API ключи',
    2: 'Выбрать язык ответа',
    3: 'Текущие настройки',
    0: 'Назад',
}
lang_menu_options = {
    1: 'ru',
    2: 'en',
    0: 'Назад'
}


def clear_terminal() -> None:
    if platform.system().lower() == "windows":
        os.system('cls')
    else:
        os.system('reset')
