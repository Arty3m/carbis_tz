import textwrap
from time import sleep
import httpx
from dadata import Dadata
from utils import T_RESET, T_INFO, T_WARNING, T_SUCCESS, T_GOODBYE, main_menu_options, settings_menu_options, \
    lang_menu_options, clear_terminal
from db import DB

db: DB = DB('config.db')

LANG: str = 'ru'
HAVE_CONNECT: bool = False


def startup_config_load() -> Dadata:
    """Загружает конфиги из БД"""
    global LANG
    api_key, secret_key, LANG = db.get_settings()
    return Dadata(api_key, secret_key)


def test_dadata_connection(dadata: Dadata) -> bool:
    """
    Возвращает True, если есть соединение с сервисом dadata
            Параметры:
                    dadata (Dadata): объект Dadata
            Возвращаемое значение:
                    bool
    """
    try:
        dadata.get_daily_stats()
        return True
    except httpx.HTTPStatusError:
        return False


def get_user_option() -> int:
    """Возвращает int значение выбора пользователя"""
    try:
        option: int = int(input('\n>> '))
        return option
    except ValueError:
        print_message(msg='Нет такого варианта', time_sleep=0)
        return -1


def about() -> None:
    """Пункт меню "О программе" """
    while True:
        clear_terminal()
        show_title(title='О программе')
        print_message('Данная программа предоставляет вам удобный доступ к API сервиса dadata.ru.'
                      '\nОна поможет определить точные координаты, интересующего вас места.\n\n\t\t made by Kolbun Artyom',
                      type_msg=T_INFO,
                      clear_window=False, count_nl=0)
        print(' 0. Назад')
        option: int = get_user_option()
        if option == 0:
            break


def show_menu(title: str, menu_options: dict) -> None:
    """
    Отображает меню
            Параметры:
                    title (str): заголовок
                    menu_options (dict): возможные пункты меню
    """
    clear_terminal()
    show_title(title=title)
    for key in menu_options.keys():
        print(f'{key:2}. {menu_options[key]}')


def show_title(title: str) -> None:
    """Отображает заголовок"""
    print(f'\t{title}\n\t' + '~' * len(title) + '\n')


def get_coords_by_address() -> None:
    """Пункт меню "Получить координаты по адресу" """
    while True:
        clear_terminal()
        show_title(title='Получить координаты места')
        user_query: str = input('Введите адрес в свободной форме: (Прим. Москва Бутово)\n\n 0. Назад\n\n>> ')
        if user_query == '0':
            break
        suggested: dict = {i: el['value'] for i, el in
                           enumerate(dadata.suggest('address', query=user_query, count=10, language=LANG))}
        if not suggested:
            print_message(msg='К сожалению ничего не нашлось', type_msg=T_WARNING, time_sleep=3)
        else:
            option: int = 0
            while option < 1 or option > len(suggested.keys()):
                clear_terminal()
                show_title(title='Получить координаты места')
                print(f'Возможно вы имели ввиду один из этих вариантов:\n')
                for i, el in suggested.items():
                    print(f'{i + 1:2}. {el}')
                print(' 0. Назад')
                option: int = get_user_option()
                if option == 0:
                    break
            if option:
                result: dict = dadata.clean(name='address', source=suggested[option - 1])
                lat: str | None = result["geo_lat"]
                lon: str | None = result["geo_lon"]
                if lat and lon:
                    clear_terminal()
                    show_title(title='Координаты места')
                    print_message(msg=f'Для адреса {suggested[option - 1]} Широта: {lat} Долгота: {lon}',
                                  type_msg=T_SUCCESS, clear_window=False, count_nl=0, count_enl=1)
                    print(' 0. Назад')
                    option: int = get_user_option()
                    if option == 0:
                        break

                else:
                    print_message(msg='К сожалению не удалось найти координаты =(\n Попробуйте указать что-то ещё',
                                  type_msg=T_WARNING, time_sleep=3)


def settings() -> None:
    """Отображает меню "Настройки" """
    while True:
        show_menu(title='Настройки', menu_options=settings_menu_options)
        option: int = get_user_option()
        if option == 0:
            break
        elif option == 1:
            entering_tokens()
        elif option == 2:
            entering_lang()
        elif option == 3:
            show_curr_settings()


def entering_tokens() -> None:
    """Отображает меню воода API ключей"""
    global HAVE_CONNECT
    global dadata
    while True:
        clear_terminal()
        show_title('Добавление API ключей')
        print('Чтобы выйти, в любой момент введите 0')
        api_key: str = input('\nВведите ваш API_KEY: ')
        if api_key == '0':
            break
        secret_key: str = input('Введите ваш SECRET_KEY: ')
        if secret_key == '0':
            break
        try:
            new_dadata: Dadata = Dadata(api_key, secret_key)
            new_dadata.get_daily_stats()
            print_message(msg='Соединение установлено!', type_msg=T_SUCCESS, time_sleep=1)
            HAVE_CONNECT = True
            db.update_keys(api_key, secret_key)
            dadata = new_dadata
            break
        except httpx.HTTPStatusError:
            print_message(msg='API_KEY или SECRET_KEY некорректны', time_sleep=3)
        except UnicodeEncodeError:
            print_message(msg='Ключи могут содержать только цифры 0-9 и латинские буквы от a-z', time_sleep=3)


def entering_lang() -> None:
    """Отображает меню выбора языка"""
    global LANG
    while True:
        print(f'Выберите язык, на котором будут выдаваться подсказки:')
        show_menu(title='Выбор языка ответа', menu_options=lang_menu_options)
        option: int = get_user_option()
        if option == 0:
            break
        elif option == 1 or option == 2:
            LANG = lang_menu_options[option]
            db.update_lang(LANG)
            print_message(msg=f'Язык был успешно изменён на {LANG}', type_msg=T_SUCCESS, time_sleep=1)
            break


def show_curr_settings() -> None:
    """Отобраажает текущие настройки пользователя"""
    while True:
        clear_terminal()
        show_title(title='Текущие настройки:')
        sett = db.get_settings()
        print(f'API_KEY: {sett[0]}\nSECRET_KEY: {sett[1]}\nЯзык: {sett[2]}\n\n 0. Назад')
        option = get_user_option()
        if option == 0:
            break


def print_message(msg: str | None = None, type_msg: str = T_WARNING, time_sleep: int = 0, clear_window: bool = True,
                  count_nl: int = 3, count_enl: int = 3) -> None:
    """
    Выводит на экран сообщение
            Параметры:
                    msg (str): сообщение
                    type_msg (str): тип сообщения(цвет текста)
                    time_sleep (int): число секунд отображения текста на экране
                    clear_window (bool): очищать ли окно перед выводом сообщения
                    count_nl (int): количество \n перед сообщением
                    count_enl (int): количество \n после сообщения
    """
    if clear_window:
        clear_terminal()
    print('\n' * count_nl + f'{type_msg}{textwrap.fill(msg, width=65, max_lines=3)}{T_RESET}' + '\n' * count_enl)
    sleep(time_sleep)


def welcome_info() -> None:
    """Отобраажает окно приветсвия для первого/ненастроенного запуска"""
    while True:
        clear_terminal()
        print(f'\tДобро пожаловать!\nДанная программа предоставляет вам удобный доступ к API сервиса dadata.ru.'
              f'\nОна поможет определить точные координаты, интересующего вас места.'
              f'\n\nНо сперва нужно добавить ваши API ключи.\n{T_INFO}(Найти их можно в вашем личном кабинете dadata.ru\n'
              f'[https://dadata.ru/profile/#info]){T_RESET}\n')
        print(
            'Добавить их сейчас или вы можете сделать это позже перейдя в Настройки - Добавить API ключи\n 1. Сейчас\n '
            '2. Сделаю это позже')
        option: int = get_user_option()
        if option == 1:
            entering_tokens()
            break
        elif option == 2:
            break


def main_menu() -> None:
    """Отображает главное меню"""
    global HAVE_CONNECT
    while True:
        show_menu(title='Главное меню', menu_options=main_menu_options)
        option: int = get_user_option()
        if option == 1:
            if HAVE_CONNECT:
                get_coords_by_address()
            else:
                print_message('Сперва нужно задать API ключи. Для этого перейдите в Настройки -> Добавить API ключи',
                              time_sleep=3)
        elif option == 2:
            settings()
        elif option == 3:
            about()
        elif option == 0:
            clear_terminal()
            print_message(msg='\t\tВсего доброго!', type_msg=T_GOODBYE, time_sleep=2)
            exit()


if __name__ == '__main__':
    clear_terminal()
    dadata: Dadata = startup_config_load()
    HAVE_CONNECT = test_dadata_connection(dadata)
    if not HAVE_CONNECT:
        welcome_info()
    main_menu()
