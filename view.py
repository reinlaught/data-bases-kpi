from datetime import datetime


class View:
    # --- ГОЛОВНІ МЕНЮ ---
    def show_main_menu(self):
        print("\n" + "=" * 30)
        print(" Г О Л О В Н Е   М Е Н Ю ")
        print("=" * 30)
        print("1. Виведення таблиці (TOP-10)")
        print("2. Додавання даних")
        print("3. Видалення даних")
        print("4. Редагування даних")
        print("5. Пошук (Гнучкий, ID, Записи)")
        print("6. Генерація даних (Random)")
        print("7. Очистити всю базу [DANGER]")
        print("8. Вихід")
        return input("Оберіть дію (1-8): ")

    def get_global_purge_confirmation(self):
        print("\nНЕБЕЗПЕЧНА ЗОНА")
        print("Ви збираєтесь безповоротно видалити ВСІ дані з усіх таблиць!")
        print("Відновити дані буде неможливо.")
        print("Щоб підтвердити операцію, введіть точну фразу: 'YES I WANT'")

        val = input("Введіть підтвердження: ").strip()

        # Повертає True тільки якщо введено точно цю фразу (регістр важливий для безпеки)
        if val == "YES I WANT":
            return True
        return False

    def show_entity_selection(self, action_name):
        print(f"\n--- {action_name}: Оберіть таблицю ---")
        print("1. Користувачі (Users)")
        print("2. Записи (Entries)")
        print("3. Нагадування (Reminders)")
        print("0. Назад")
        return input("Ваш вибір: ")

    def show_search_menu(self):
        print("\n--- МЕНЮ ПОШУКУ ---")
        print("1. Гнучкий пошук (фільтри + статистика)")
        print("2. Пошук за ID")
        print("3. Показати всі записи користувача (за ID)")
        print("4. Показати всі нагадування користувача")
        print("0. Назад")
        return input("Ваш вибір: ")

    # --- ВИВЕДЕННЯ ІНФОРМАЦІЇ ---
    def show_message(self, message):
        print(f"\n>>> {message}")

    def print_table(self, headers, rows):
        if not rows:
            print("\nТаблиця порожня або даних немає.")
            return
        if isinstance(rows, str):  # Якщо це текст помилки
            print(f"\nПОМИЛКА: {rows}")
            return

        col_width = 22
        header_row = " | ".join([f"{h:<{col_width}}" for h in headers])
        div_line = "-" * len(header_row)

        print(div_line)
        print(header_row)
        print(div_line)

        for row in rows:
            formatted_row = []
            for item in row:
                # --- ВИПРАВЛЕННЯ ФОРМАТУВАННЯ ДАТИ ---
                if isinstance(item, datetime):
                    # Обрізаємо мікросекунди, залишаємо YYYY-MM-DD HH:MM:SS
                    formatted_row.append(item.strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    formatted_row.append(str(item))

            row_str = " | ".join([f"{val:<{col_width}}" for val in formatted_row])
            print(row_str)
        print(div_line)

    def show_search_results(self, results, exec_time):
        print(f"\nРезультати пошуку (Час: {exec_time:.2f} мс):")
        headers = ["ID", "User", "Email", "Entries Found", "Reminders Found"]
        self.print_table(headers, results)

    # --- ВВЕДЕННЯ ДАНИХ (CREATE) ---
    def get_user_input(self):
        print("\n[Введення User]")
        try:
            uid_input = input("ID (Enter для авто-генерації): ").strip()
            uid = int(uid_input) if uid_input else None

            uname = input("Username: ").strip()
            if not uname: return print("Помилка: Username пустий!")

            email = input("Email: ").strip()
            if not email: return print("Помилка: Email пустий!")

            pwd = input("Password: ").strip()
            if not pwd: return print("Помилка: Password пустий!")

            return uid, uname, email, pwd
        except ValueError:
            return print("Помилка: ID не число!")

    def get_entry_input(self):
        print("\n[Введення Entry]")
        try:
            eid_input = input("Entry ID (Enter для авто-генерації): ").strip()
            eid = int(eid_input) if eid_input else None

            title = input("Title: ").strip()
            if not title: return print("Помилка: Title пустий!")

            text = input("Text: ").strip()
            if not text: return print("Помилка: Text пустий!")

            uid_input = input("User ID (FK): ").strip()
            if not uid_input: return print("Помилка: Вкажіть User ID!")
            uid = int(uid_input)

            return eid, title, text, uid
        except ValueError:
            return print("Помилка: ID не число!")

    def get_reminder_input(self):
        print("\n[Введення Reminder]")
        try:
            rid_input = input("Reminder ID (Enter для авто-генерації): ").strip()
            rid = int(rid_input) if rid_input else None

            eid_input = input("Entry ID (FK): ").strip()
            if not eid_input: return print("Помилка: Вкажіть Entry ID!")
            eid = int(eid_input)

            remind_at = input("Date (YYYY-MM-DD HH:MM:SS): ").strip()
            if not remind_at: return print("Помилка: Дата пуста!")

            match input("Active (1 - Так, 0 - Ні): ").strip():
                case '1':
                    is_active = True
                case '0':
                    is_active = False
                case _:
                    is_active = True

            return rid, eid, remind_at, is_active
        except ValueError:
            return print("Помилка вводу!")

    def show_delete_options(self, entity_name):
        print(f"\n--- Опції видалення: {entity_name} ---")
        print("1. Видалити за ID (конкретний запис)")

        if entity_name == "User":
            print("2. Видалити за Username")
            print("3. Видалити за Email")
            print("4. Видалити ВСІХ користувачів (Очистити таблицю) [НОВЕ]")  # <---

        elif entity_name == "Entry":
            print("2. Видалити ВСІ записи певного автора")
            print("3. Видалити ВСІ записи (Очистити таблицю) [НОВЕ]")  # <---

        elif entity_name == "Reminder":
            print("2. Видалити нагадування за датою")
            print("3. Видалити за статусом")
            print("4. Видалити ВСІ нагадування (Очистити таблицю) [НОВЕ]")  # <---

        print("0. Назад")
        return input("Ваш вибір: ")

    def confirm_table_clear(self, entity_name):
        print(f"\nВи збираєтесь видалити ВСІ дані з таблиці {entity_name}!")
        if entity_name == "User":
            print("(Це також видалить всі записи та нагадування!)")
        elif entity_name == "Entry":
            print("(Це також видалить всі нагадування!)")

        choice = input("Напишіть 'yes' для підтвердження: ").strip().lower()
        return choice == 'yes'

    # Допоміжний метод для отримання булевого статусу
    def get_status_input_simple(self):
        val = input("Введіть статус для видалення (1 - Активні, 0 - Неактивні): ").strip()
        if val == '1': return True
        if val == '0': return False
        print("Помилка: Введіть 1 або 0.")
        return None

    def get_delete_criteria(self, prompt):
        val = input(f"{prompt}: ").strip()
        if not val:
            print("Помилка: Значення не може бути пустим.")
            return None
        return val

    def confirm_cascade_delete(self, message):
        print(f"\nУВАГА: {message}")
        print("Бажаєте видалити цей об'єкт разом з усіма залежними даними?")
        choice = input("Введіть 'yes' для підтвердження або Enter для скасування: ").strip().lower()
        return choice == 'yes'

    # --- ВВЕДЕННЯ ДАНИХ (UPDATE) ---
    def _input_or_keep(self, prompt, current_value):
        """Допоміжний метод: повертає нове значення або старе, якщо натиснуто Enter"""
        # Якщо current_value це дата, форматуємо її для краси при відображенні
        display_val = current_value
        if isinstance(current_value, datetime):
            display_val = current_value.strftime("%Y-%m-%d %H:%M:%S")

        val = input(f"{prompt} [Enter = залишити '{display_val}']: ").strip()
        if not val:
            return current_value
        return val

    def get_edit_user_input(self, current_data):
        print(f"\n--- Редагування User (ID: {current_data[0]}) ---")
        try:
            new_id = int(self._input_or_keep("Новий ID", current_data[0]))
            new_uname = self._input_or_keep("Новий Username", current_data[1])
            new_email = self._input_or_keep("Новий Email", current_data[2])
            new_pwd = self._input_or_keep("Новий Password", current_data[3])
            return new_id, new_uname, new_email, new_pwd
        except ValueError:
            print("Помилка: ID має бути числом!")
            return None

    def get_edit_entry_input(self, current_data):
        print(f"\n--- Редагування Entry (ID: {current_data[0]}) ---")
        try:
            new_id = int(self._input_or_keep("Новий Entry ID", current_data[0]))
            new_title = self._input_or_keep("Новий Title", current_data[1])
            new_text = self._input_or_keep("Новий Text", current_data[2])
            new_uid = int(self._input_or_keep("Новий User ID", current_data[3]))
            return new_id, new_title, new_text, new_uid
        except ValueError:
            print("Помилка: ID має бути числом!")
            return None

    def get_edit_reminder_input(self, current_data):
        print(f"\n--- Редагування Reminder (ID: {current_data[0]}) ---")
        try:
            new_id = int(self._input_or_keep("Новий Reminder ID", current_data[0]))
            new_eid = int(self._input_or_keep("Новий Entry ID", current_data[1]))
            new_date = self._input_or_keep("Нова дата", current_data[2])

            curr_active_str = "1" if current_data[3] else "0"
            new_active_str = self._input_or_keep("Active (1/0)", curr_active_str)
            new_active = True if new_active_str == '1' else False

            return new_id, new_eid, new_date, new_active
        except ValueError:
            print("Помилка: ID має бути числом!")
            return None

    # --- ДОПОМІЖНІ МЕТОДИ ---
    def get_id_input(self, entity_name, context="Видалення"):
        match context:
            case "Видалення":
                action = "видалити"
            case "Редагування":
                action = "редагувати"
            case _:
                action = "знайти"

        print(f"\n[{context}: {entity_name}]")
        raw = input(f"Введіть ID ({entity_name}), який треба {action}: ").strip()

        if not raw:
            print(f"\nПОМИЛКА: Ви не ввели ID!")
            return None
        try:
            return int(raw)
        except ValueError:
            print(f"\nПОМИЛКА: ID має бути числом.")
            return None

    def get_search_input(self):
        print("\n--- ГНУЧКИЙ ПОШУК (Enter щоб пропустити) ---")
        u = input("Ім'я користувача: ").strip()
        email = input("Email (або частина): ").strip()
        t = input("Заголовок запису: ").strip()
        txt = input("Текст запису: ").strip()
        df = input("Дата від: ").strip()
        dt = input("Дата до: ").strip()

        match input("Активний (1 - Так, 0 - Ні, Enter - Всі): ").strip():
            case '1':
                is_active = True
            case '0':
                is_active = False
            case _:
                is_active = None

        return {
            'username': u if u else None, 'email': email if email else None,
            'title': t if t else None, 'text': txt if txt else None,
            'is_active': is_active, 'date_from': df if df else None,
            'date_to': dt if dt else None
        }

    def get_generation_count(self):
        print("\n[Генерація даних]")
        try:
            val = input("Скільки записів згенерувати? (напр. 1000): ").strip()
            count = int(val)
            if count <= 0:
                print("Число має бути більше 0.")
                return None
            return count
        except ValueError:
            print("Помилка: Введіть ціле число.")
            return None