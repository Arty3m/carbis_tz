import sqlite3


class DB:
    def __init__(self, db_name: str):
        """Инициализация БД """
        try:
            self.conn = sqlite3.connect(db_name)
        except sqlite3.Error:
            print(f'Не удалось подключиться к базе данных {db_name}')
            return
        self.cursor = self.conn.cursor()
        self.__create_default()

    def __create_default(self):
        """Создает таблицу и заполняет её дефолтными значениями"""
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS settings(
           id INTEGER PRIMARY KEY NOT NULL,
           api_key TEXT,
           secret_key TEXT,
           lang VARCHAR(30));
        """)
        self.conn.commit()
        if not self.cursor.execute('SELECT `id` FROM settings').fetchall():
            base_settings: tuple = ('api_token', 'secret_token', 'ru')
            self.cursor.execute("INSERT INTO settings VALUES(NULL, ?, ?, ?);", base_settings)
            self.conn.commit()

    def update_keys(self, api_key: str, secret_key: str):
        """Обновляет API ключи"""
        self.cursor.execute('UPDATE settings SET api_key=(?), secret_key=(?) WHERE id=1', (api_key, secret_key))
        self.conn.commit()

    def update_lang(self, lang: str) -> None:
        """Обновляет язык, на котором будут приходить ответы"""
        self.cursor.execute('UPDATE settings SET lang=(?) WHERE id=1', (lang,))
        self.conn.commit()

    def get_settings(self) -> tuple[str, str, str]:
        """Возвращает tuple из данных"""
        return self.cursor.execute('SELECT api_key, secret_key, lang FROM settings WHERE id=1').fetchone()
