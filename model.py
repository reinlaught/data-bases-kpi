import psycopg
import time
from psycopg import errors


class Model:
    def __init__(self, db_name, user, password, host, port):
        self.conn_info = f"dbname={db_name} user={user} password={password} host={host} port={port}"
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = psycopg.connect(self.conn_info)
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(f"Помилка підключення: {e}")
            return False

    def disconnect(self):
        if self.cursor: self.cursor.close()
        if self.connection: self.connection.close()

    # --- ВИВЕДЕННЯ ТОП-10 ---
    def get_top_users(self, limit=10):
        try:
            self.cursor.execute('SELECT id, username, email FROM public."user" ORDER BY id LIMIT %s', (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            return str(e)

    def get_top_entries(self, limit=10):
        try:
            self.cursor.execute('SELECT entry_id, title, text, user_id FROM public.entry ORDER BY entry_id LIMIT %s',
                                (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            return str(e)

    def get_top_reminders(self, limit=10):
        try:
            self.cursor.execute(
                'SELECT reminder_id, entry_id, remind_at, active FROM public.reminder ORDER BY reminder_id LIMIT %s',
                (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            return str(e)

    # --- ДОДАВАННЯ ---
    def add_user(self, user_id, username, email, password):
        try:
            if user_id is None:
                self.cursor.execute('SELECT COALESCE(MAX(id), 0) + 1 FROM public."user"')
                user_id = self.cursor.fetchone()[0]
                print(f"(Автоматично обрано ID: {user_id})")

            query = 'INSERT INTO public."user" (id, username, email, password) VALUES (%s, %s, %s, %s)'
            self.cursor.execute(query, (user_id, username, email, password))
            self.connection.commit()
            return "Користувача успішно додано."
        except errors.UniqueViolation:
            self.connection.rollback()
            return "Помилка: Такий ID, email або username вже існує."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    def add_entry(self, entry_id, title, text, user_id):
        try:
            if entry_id is None:
                self.cursor.execute('SELECT COALESCE(MAX(entry_id), 0) + 1 FROM public.entry')
                entry_id = self.cursor.fetchone()[0]
                print(f"(Автоматично обрано ID: {entry_id})")

            query = "INSERT INTO public.entry (entry_id, title, text, user_id) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (entry_id, title, text, user_id))
            self.connection.commit()
            return "Запис успішно додано."
        except errors.ForeignKeyViolation:
            self.connection.rollback()
            return f"Помилка: User ID {user_id} не існує."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    def add_reminder(self, reminder_id, entry_id, remind_at, active):
        try:
            if reminder_id is None:
                self.cursor.execute('SELECT COALESCE(MAX(reminder_id), 0) + 1 FROM public.reminder')
                reminder_id = self.cursor.fetchone()[0]
                print(f"(Автоматично обрано ID: {reminder_id})")

            query = "INSERT INTO public.reminder (reminder_id, entry_id, remind_at, active) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (reminder_id, entry_id, remind_at, active))
            self.connection.commit()
            return "Нагадування успішно додано."
        except errors.ForeignKeyViolation:
            self.connection.rollback()
            return f"Помилка: Entry ID {entry_id} не існує."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    # --- ВИДАЛЕННЯ ---
    def delete_user(self, user_id):
        try:
            self.cursor.execute('DELETE FROM public."user" WHERE id = %s', (user_id,))
            if self.cursor.rowcount > 0:
                self.connection.commit()
                return f"Користувача {user_id} видалено."
            self.connection.rollback()
            return "ID не знайдено."
        except errors.ForeignKeyViolation:
            self.connection.rollback()
            return "Неможливо видалити: є пов'язані записи."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    def delete_entry(self, entry_id):
        try:
            self.cursor.execute('DELETE FROM public.entry WHERE entry_id = %s', (entry_id,))
            if self.cursor.rowcount > 0:
                self.connection.commit()
                return f"Запис {entry_id} видалено."
            return "ID не знайдено."
        except errors.ForeignKeyViolation:
            self.connection.rollback()
            return "Неможливо видалити: є пов'язані нагадування."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    def delete_reminder(self, reminder_id):
        try:
            self.cursor.execute('DELETE FROM public.reminder WHERE reminder_id = %s', (reminder_id,))
            if self.cursor.rowcount > 0:
                self.connection.commit()
                return f"Нагадування {reminder_id} видалено."
            return "ID не знайдено."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    # Видалення користувача за Username або Email
    def delete_user_by_attr(self, attr_name, value):
        try:
            query = f'DELETE FROM public."user" WHERE {attr_name} = %s'
            self.cursor.execute(query, (value,))

            if self.cursor.rowcount > 0:
                self.connection.commit()
                return f"Видалено користувачів: {self.cursor.rowcount}."
            else:
                self.connection.rollback()
                return f"Користувача з {attr_name}='{value}' не знайдено."
        except errors.ForeignKeyViolation:
            self.connection.rollback()
            return "Неможливо видалити: є пов'язані записи."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    # Видалення всіх записів певного автора (за Username)
    def delete_entries_by_author(self, username):
        try:
            query = """
                DELETE FROM public.entry 
                WHERE user_id = (SELECT id FROM public."user" WHERE username = %s)
            """
            self.cursor.execute(query, (username,))

            if self.cursor.rowcount > 0:
                self.connection.commit()
                return f"Видалено записів автора '{username}': {self.cursor.rowcount}."
            else:
                return f"Записів автора '{username}' не знайдено (або автора не існує)."
        except errors.ForeignKeyViolation:
            self.connection.rollback()
            return "Неможливо видалити: є пов'язані нагадування."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    # Видалення нагадувань за датою (тільки по дню, ігноруючи час)
    def delete_reminders_by_date(self, date_str):
        try:
            query = "DELETE FROM public.reminder WHERE DATE(remind_at) = %s"
            self.cursor.execute(query, (date_str,))

            if self.cursor.rowcount > 0:
                self.connection.commit()
                return f"Видалено нагадувань за {date_str}: {self.cursor.rowcount}."
            else:
                return "Нагадувань за цю дату не знайдено."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    # --- КАСКАДНЕ ВИДАЛЕННЯ (FORCE DELETE) ---
    def delete_user_cascade(self, user_id):
        try:
            self.cursor.execute("""
                DELETE FROM public.reminder 
                WHERE entry_id IN (SELECT entry_id FROM public.entry WHERE user_id = %s)
            """, (user_id,))

            self.cursor.execute('DELETE FROM public.entry WHERE user_id = %s', (user_id,))

            self.cursor.execute('DELETE FROM public."user" WHERE id = %s', (user_id,))

            self.connection.commit()
            return f"Успішно видалено користувача {user_id} та всі його дані."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка каскадного видалення: {e}"

    def delete_user_cascade_by_attr(self, attr_name, value):
        try:
            query_find = f'SELECT id FROM public."user" WHERE {attr_name} = %s'
            self.cursor.execute(query_find, (value,))
            res = self.cursor.fetchone()

            if not res:
                return f"Користувача з {attr_name}='{value}' не знайдено."

            user_id = res[0]

            return self.delete_user_cascade(user_id)

        except Exception as e:
            return f"Помилка каскаду: {e}"

    def delete_entry_cascade(self, entry_id):
        try:
            self.cursor.execute('DELETE FROM public.reminder WHERE entry_id = %s', (entry_id,))

            self.cursor.execute('DELETE FROM public.entry WHERE entry_id = %s', (entry_id,))

            self.connection.commit()
            return f"Успішно видалено запис {entry_id} та його нагадування."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка каскадного видалення: {e}"

    def delete_entries_cascade_by_author(self, username):
        try:
            query_rem = """
                DELETE FROM public.reminder 
                WHERE entry_id IN (
                    SELECT entry_id FROM public.entry 
                    WHERE user_id = (SELECT id FROM public."user" WHERE username = %s)
                )
            """
            self.cursor.execute(query_rem, (username,))

            query_ent = """
                DELETE FROM public.entry 
                WHERE user_id = (SELECT id FROM public."user" WHERE username = %s)
            """
            self.cursor.execute(query_ent, (username,))

            if self.cursor.rowcount > 0:
                self.connection.commit()
                return f"Успішно видалено всі записи та нагадування автора '{username}'."
            else:
                self.connection.rollback()
                return f"Записів автора '{username}' не знайдено."

        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    def delete_reminders_by_status(self, is_active):
        try:
            query = "DELETE FROM public.reminder WHERE active = %s"
            self.cursor.execute(query, (is_active,))

            if self.cursor.rowcount > 0:
                self.connection.commit()
                status_str = "активних" if is_active else "неактивних"
                return f"Успішно видалено {self.cursor.rowcount} {status_str} нагадувань."
            else:
                return "Нагадувань з таким статусом не знайдено."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    # --- ОЧИЩЕННЯ КОНКРЕТНИХ ТАБЛИЦЬ ---
    def clear_table_users(self):
        try:
            self.cursor.execute('TRUNCATE TABLE public."user" RESTART IDENTITY CASCADE')
            self.connection.commit()
            return "Таблицю Users (та всі залежні дані) повністю очищено. ID скинуто."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    def clear_table_entries(self):
        try:
            self.cursor.execute('TRUNCATE TABLE public.entry RESTART IDENTITY CASCADE')
            self.connection.commit()
            return "Таблицю Entries (та залежні нагадування) повністю очищено. ID скинуто."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    def clear_table_reminders(self):
        try:
            self.cursor.execute('TRUNCATE TABLE public.reminder RESTART IDENTITY CASCADE')
            self.connection.commit()
            return "Таблицю Reminders повністю очищено. ID скинуто."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка: {e}"

    # --- ПОШУК ЗА ІДЕНТИФІКАТОРОМ ---
    def find_user_by_id(self, user_id):
        try:
            query = 'SELECT id, username, email, password FROM public."user" WHERE id = %s'
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            return str(e)

    def find_entry_by_id(self, entry_id):
        try:
            query = 'SELECT entry_id, title, text, user_id FROM public.entry WHERE entry_id = %s'
            self.cursor.execute(query, (entry_id,))
            return self.cursor.fetchall()
        except Exception as e:
            return str(e)

    def find_reminder_by_id(self, reminder_id):
        try:
            query = 'SELECT reminder_id, entry_id, remind_at, active FROM public.reminder WHERE reminder_id = %s'
            self.cursor.execute(query, (reminder_id,))
            return self.cursor.fetchall()
        except Exception as e:
            return str(e)

    # --- ГНУЧКИЙ ПОШУК ---
    def search_flexible(self, filters):
        start_time = time.time()

        query = """
            SELECT 
                u.id, 
                u.username, 
                u.email, 
                COUNT(DISTINCT e.entry_id) as entries_count,
                COUNT(DISTINCT r.reminder_id) as reminders_count
            FROM public."user" u
            LEFT JOIN public.entry e ON u.id = e.user_id
            LEFT JOIN public.reminder r ON e.entry_id = r.entry_id
            WHERE 1=1
        """
        params = []

        if filters.get('username'):
            query += " AND u.username ILIKE %s"
            params.append(f"%{filters['username']}%")

        if filters.get('email'):
            query += " AND u.email ILIKE %s"
            params.append(f"%{filters['email']}%")

        if filters.get('title'):
            query += " AND e.title ILIKE %s"
            params.append(f"%{filters['title']}%")

        if filters.get('text'):
            query += " AND e.text ILIKE %s"
            params.append(f"%{filters['text']}%")

        if filters.get('is_active') is not None:
            query += " AND r.active = %s"
            params.append(filters['is_active'])

        if filters.get('date_from') and filters.get('date_to'):
            query += " AND r.remind_at BETWEEN %s AND %s"
            params.append(filters['date_from'])
            params.append(filters['date_to'])

        query += " GROUP BY u.id, u.username, u.email ORDER BY u.id"

        try:
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            exec_time = (time.time() - start_time) * 1000
            return results, exec_time
        except Exception as e:
            return str(e), 0

    def get_user_entries_details(self, user_id):
        try:
            self.cursor.execute('SELECT username FROM public."user" WHERE id = %s', (user_id,))
            user = self.cursor.fetchone()

            if not user:
                return "Користувача з таким ID не знайдено."

            query = """
                SELECT entry_id, title, text 
                FROM public.entry 
                WHERE user_id = %s
                ORDER BY entry_id
            """
            self.cursor.execute(query, (user_id,))
            results = self.cursor.fetchall()

            return user[0], results
        except Exception as e:
            return str(e), []

    # --- ОТРИМАННЯ НАГАДУВАНЬ КОНКРЕТНОГО КОРИСТУВАЧА ---
    def get_user_reminders_details(self, user_id):
        try:
            self.cursor.execute('SELECT username FROM public."user" WHERE id = %s', (user_id,))
            user = self.cursor.fetchone()

            if not user:
                return "Користувача з таким ID не знайдено."

            query = """
                SELECT r.reminder_id, e.title, r.remind_at, r.active
                FROM public.reminder r
                JOIN public.entry e ON r.entry_id = e.entry_id
                WHERE e.user_id = %s
                ORDER BY r.remind_at
            """
            self.cursor.execute(query, (user_id,))
            results = self.cursor.fetchall()

            return user[0], results
        except Exception as e:
            return str(e), []

    # --- ГЕНЕРАЦІЯ ДАНИХ ---
    def generate_users(self, count):
        start_time = time.time()
        try:
            self.cursor.execute('SELECT COALESCE(MAX(id), 0) FROM public."user"')
            start_id = self.cursor.fetchone()[0] + 1

            query = """
                INSERT INTO public."user" (id, username, email, password)
                SELECT 
                    i, 

                    -- Username: 6 випадкових літер + підкреслення + ID
                    (SELECT array_to_string(ARRAY(
                        SELECT chr(trunc(65 + random() * 25)::int) 
                        FROM generate_series(1, 6 + (i - i))
                    ), '')) || '_' || i,

                    -- Email: 3 випадкові літери + ID + домен
                    (SELECT array_to_string(ARRAY(
                        SELECT chr(trunc(65 + random() * 25)::int) 
                        FROM generate_series(1, 3 + (i - i))
                    ), '')) || i || '@gen.com',

                    -- Password: 10 випадкових літер
                    (SELECT array_to_string(ARRAY(
                        SELECT chr(trunc(65 + random() * 25)::int) 
                        FROM generate_series(1, 10 + (i - i))
                    ), ''))

                FROM generate_series(%s::int, %s::int) AS i
                ON CONFLICT DO NOTHING
            """
            self.cursor.execute(query, (start_id, start_id + count - 1))
            self.connection.commit()

            exec_time = (time.time() - start_time) * 1000
            return f"Успішно згенеровано {count} користувачів за {exec_time:.2f} мс."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка генерації User: {e}"

    def generate_entries(self, count):
        self.cursor.execute('SELECT count(*) FROM public."user"')
        if self.cursor.fetchone()[0] == 0:
            return "Помилка: Немає користувачів! Спочатку згенеруйте Users."

        start_time = time.time()
        try:
            self.cursor.execute('SELECT COALESCE(MAX(entry_id), 0) FROM public.entry')
            start_id = self.cursor.fetchone()[0] + 1

            query = """
                WITH all_ids AS (
                    SELECT array_agg(id) as id_list FROM public."user"
                )
                INSERT INTO public.entry (entry_id, title, text, user_id)
                SELECT 
                    i,

                    -- TITLE: 10 випадкових літер
                    (SELECT array_to_string(ARRAY(
                        SELECT chr(trunc(65 + random() * 25)::int) 
                        FROM generate_series(1, 10 + (i - i))
                    ), '')),

                    -- TEXT: 10 випадкових літер
                    (SELECT array_to_string(ARRAY(
                        SELECT chr(trunc(65 + random() * 25)::int) 
                        FROM generate_series(1, 10 + (i - i))
                    ), '')),

                    -- User ID: випадковий з існуючих
                    id_list[floor(random() * array_length(id_list, 1) + 1)]

                FROM generate_series(%s::int, %s::int) AS i, all_ids
            """
            self.cursor.execute(query, (start_id, start_id + count - 1))
            self.connection.commit()

            exec_time = (time.time() - start_time) * 1000
            return f"Успішно згенеровано {count} записів за {exec_time:.2f} мс."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка генерації Entry: {e}"

    def generate_reminders(self, count):
        self.cursor.execute('SELECT count(*) FROM public.entry')
        if self.cursor.fetchone()[0] == 0:
            return "Помилка: Немає записів (Entries)! Спочатку згенеруйте Entries."

        start_time = time.time()
        try:
            self.cursor.execute('SELECT COALESCE(MAX(reminder_id), 0) FROM public.reminder')
            start_id = self.cursor.fetchone()[0] + 1

            query = """
                WITH all_ids AS (
                    SELECT array_agg(entry_id) as id_list FROM public.entry
                )
                INSERT INTO public.reminder (reminder_id, entry_id, remind_at, active)
                SELECT 
                    i,
                    -- Беремо випадковий ID з масиву id_list
                    id_list[floor(random() * array_length(id_list, 1) + 1)],

                    timestamp '2025-09-01 08:00:00' + 
                    random() * (timestamp '2026-06-30 20:00:00' - timestamp '2025-09-01 08:00:00'),

                    (random() > 0.5)
                FROM generate_series(%s::int, %s::int) AS i, all_ids
            """
            self.cursor.execute(query, (start_id, start_id + count - 1))
            self.connection.commit()

            exec_time = (time.time() - start_time) * 1000
            return f"Успішно згенеровано {count} нагадувань за {exec_time:.2f} мс."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка генерації Reminder: {e}"

    # --- РЕДАГУВАННЯ (UPDATE) ---
    def update_user(self, current_id, new_id, new_username, new_email, new_password):
        try:
            query = """
                UPDATE public."user" 
                SET id = %s, username = %s, email = %s, password = %s 
                WHERE id = %s
            """
            self.cursor.execute(query, (new_id, new_username, new_email, new_password, current_id))
            self.connection.commit()
            return "Користувача успішно оновлено."
        except errors.UniqueViolation:
            self.connection.rollback()
            return "Помилка: Такий ID, Username або Email вже зайняті."
        except errors.ForeignKeyViolation:
            self.connection.rollback()
            return "Помилка: Не можна змінити ID, бо існують пов'язані записи."
        except errors.StringDataRightTruncation:
            self.connection.rollback()
            return "Помилка: Дані занадто довгі! Максимум 20 символів."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка оновлення: {e}"

    def update_entry(self, current_id, new_id, new_title, new_text, new_user_id):
        try:
            query = """
                UPDATE public.entry 
                SET entry_id = %s, title = %s, text = %s, user_id = %s 
                WHERE entry_id = %s
            """
            self.cursor.execute(query, (new_id, new_title, new_text, new_user_id, current_id))
            self.connection.commit()
            return "Запис успішно оновлено."
        except errors.ForeignKeyViolation:
            self.connection.rollback()
            return f"Помилка: User ID {new_user_id} не існує."
        except errors.StringDataRightTruncation:
            self.connection.rollback()
            return "Помилка: Текст або заголовок занадто довгі (макс. 20 символів)."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка оновлення: {e}"

    def update_reminder(self, current_id, new_id, new_entry_id, new_date, new_active):
        try:
            query = """
                UPDATE public.reminder 
                SET reminder_id = %s, entry_id = %s, remind_at = %s, active = %s 
                WHERE reminder_id = %s
            """
            self.cursor.execute(query, (new_id, new_entry_id, new_date, new_active, current_id))
            self.connection.commit()
            return "Нагадування успішно оновлено."
        except errors.ForeignKeyViolation:
            self.connection.rollback()
            return f"Помилка: Entry ID {new_entry_id} не існує."
        except errors.DatatypeMismatch: # Якщо ввели дату у поганому форматі
             self.connection.rollback()
             return "Помилка: Невірний формат дати."
        except Exception as e:
            self.connection.rollback()
            return f"Помилка оновлення: {e}"

# --- ПОВНЕ ОЧИЩЕННЯ БАЗИ ---
    def delete_all_data(self):
        try:
            query = 'TRUNCATE TABLE public."user", public.entry, public.reminder RESTART IDENTITY CASCADE'
            self.cursor.execute(query)
            self.connection.commit()
            return "Всі таблиці успішно очищено. База даних порожня."
        except Exception as e:
            self.connection.rollback()
            return f"Критична помилка очищення: {e}"