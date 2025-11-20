import sys
from model import Model
from view import View


def run():
    # --- ПЕРЕВІРКА ВЕРСІЇ PYTHON ---
    # match-case працює тільки в Python 3.10+
    if sys.version_info < (3, 10):
        print("Помилка: Для роботи цього коду потрібен Python 3.10 або новіше.")
        return

    # --- НАЛАШТУВАННЯ ПІДКЛЮЧЕННЯ ---
    db = Model(
        db_name="postgres",
        user="postgres",
        password="1223334444",
        host="localhost",
        port="5432"
    )
    view = View()

    # Спроба підключення
    if db.connect():
        view.show_message("Підключено до БД успішно!")
    else:
        view.show_message("Не вдалося підключитися до бази даних.")
        return

    while True:
        main_choice = view.show_main_menu()

        match main_choice:
            # --- 8. ВИХІД ---
            case '8':
                db.disconnect()
                view.show_message("Роботу завершено.")
                break
            # --- 7. ОЧИЩЕННЯ БАЗИ ---
            case '7':
                if view.get_global_purge_confirmation():
                    view.show_message("Виконується повне очищення бази...")
                    view.show_message(db.delete_all_data())
                else:
                    view.show_message("Операцію скасовано. Кодова фраза невірна.")

            # --- 6. ГЕНЕРАЦІЯ ДАНИХ ---
            case '6':
                entity_choice = view.show_entity_selection("Генерація рандомних даних")

                if entity_choice == '0': continue

                count = view.get_generation_count()
                if not count: continue

                view.show_message(f"Генеруємо {count} записів... Зачекайте...")

                match entity_choice:
                    case '1':
                        view.show_message(db.generate_users(count))
                    case '2':
                        view.show_message(db.generate_entries(count))
                    case '3':
                        view.show_message(db.generate_reminders(count))
                    case _:
                        view.show_message("Невірний вибір таблиці.")

            # --- 5. ПОШУК ---
            case '5':
                search_type = view.show_search_menu()
                match search_type:
                    case '1':
                        try:
                            filters = view.get_search_input()
                            res, t = db.search_flexible(filters)
                            if isinstance(res, str):
                                view.show_message(res)
                            else:
                                view.show_search_results(res, t)
                        except Exception as e:
                            view.show_message(f"Помилка: {e}")

                    # 5.2 Пошук за ID
                    case '2':
                        entity = view.show_entity_selection("Пошук за ID")
                        match entity:
                            case '1':
                                if uid := view.get_id_input("User", context="Пошук"):
                                    view.print_table(["ID", "Username", "Email", "Password"], db.find_user_by_id(uid))
                            case '2':
                                if eid := view.get_id_input("Entry", context="Пошук"):
                                    view.print_table(["ID", "Title", "Text", "User ID"], db.find_entry_by_id(eid))
                            case '3':
                                if rid := view.get_id_input("Reminder", context="Пошук"):
                                    view.print_table(["ID", "Entry ID", "Date", "Active"], db.find_reminder_by_id(rid))
                            case '0':
                                pass
                            case _:
                                view.show_message("Невірний вибір.")

                    # 5.3 Показати всі ЗАПИСИ користувача
                    case '3':
                        if uid := view.get_id_input("User", context="Пошук записів"):
                            result = db.get_user_entries_details(uid)
                            if isinstance(result, str):
                                view.show_message(result)
                            else:
                                username, entries = result
                                view.show_message(f"Всі записи користувача: {username}")
                                if not entries:
                                    view.show_message("Записів не знайдено.")
                                else:
                                    view.print_table(["Entry ID", "Title", "Text"], entries)

                    # 5.4 Показати всі НАГАДУВАННЯ користувача
                    case '4':
                        if uid := view.get_id_input("User", context="Пошук нагадувань"):
                            result = db.get_user_reminders_details(uid)
                            if isinstance(result, str):
                                view.show_message(result)
                            else:
                                username, reminders = result
                                view.show_message(f"Нагадування користувача: {username}")
                                if not reminders:
                                    view.show_message("Нагадувань не знайдено.")
                                else:
                                    view.print_table(["Rem ID", "Entry Title", "Remind At", "Active"], reminders)

                    case '0':
                        continue
                    case _:
                        view.show_message("Невірний тип пошуку.")

            # --- 4. РЕДАГУВАННЯ ---
            case '4':
                entity_choice = view.show_entity_selection("Редагування даних")
                if entity_choice == '0': continue

                match entity_choice:
                    # Редагування користувача
                    case '1':
                        if uid := view.get_id_input("User", context="Редагування"):
                            if rows := db.find_user_by_id(uid):  # Отримуємо старі дані
                                if new_data := view.get_edit_user_input(rows[0]):
                                    view.show_message(db.update_user(uid, *new_data))
                            else:
                                view.show_message("Користувача не знайдено.")

                    # Редагування запису
                    case '2':
                        if eid := view.get_id_input("Entry", context="Редагування"):
                            if rows := db.find_entry_by_id(eid):
                                if new_data := view.get_edit_entry_input(rows[0]):
                                    view.show_message(db.update_entry(eid, *new_data))
                            else:
                                view.show_message("Запис не знайдено.")

                    # Редагування нагадувальника
                    case '3':
                        if rid := view.get_id_input("Reminder", context="Редагування"):
                            if rows := db.find_reminder_by_id(rid):
                                if new_data := view.get_edit_reminder_input(rows[0]):
                                    view.show_message(db.update_reminder(rid, *new_data))
                            else:
                                view.show_message("Нагадування не знайдено.")

                    case _:
                        view.show_message("Невірний вибір.")

            # --- 3. ВИДАЛЕННЯ ---
            case '3':
                entity_choice = view.show_entity_selection("Видалення даних")
                if entity_choice == '0': continue

                match entity_choice:
                    # Видалення користувача
                    case '1':
                        del_option = view.show_delete_options("User")
                        match del_option:
                            case '1':  # ID
                                if uid := view.get_id_input("User"):
                                    msg = db.delete_user(uid)
                                    view.show_message(msg)
                                    if "Неможливо видалити" in msg:
                                        if view.confirm_cascade_delete("Користувач має залежні дані."):
                                            view.show_message(db.delete_user_cascade(uid))
                            case '2':  # Username
                                if name := view.get_delete_criteria("Введіть Username"):
                                    msg = db.delete_user_by_attr("username", name)
                                    view.show_message(msg)
                                    if "Неможливо видалити" in msg:
                                        if view.confirm_cascade_delete(f"Користувач '{name}' має записи."):
                                            view.show_message(db.delete_user_cascade_by_attr("username", name))
                            case '3':  # Email
                                if mail := view.get_delete_criteria("Введіть Email"):
                                    msg = db.delete_user_by_attr("email", mail)
                                    view.show_message(msg)
                                    if "Неможливо видалити" in msg:
                                        if view.confirm_cascade_delete(f"Email '{mail}' має записи."):
                                            view.show_message(db.delete_user_cascade_by_attr("email", mail))

                            # 4. Видалити всіх
                            case '4':
                                if view.confirm_table_clear("User"):
                                    view.show_message(db.clear_table_users())

                            case _:
                                pass

                    # Видалення запису
                    case '2':
                        del_option = view.show_delete_options("Entry")
                        match del_option:
                            case '1':  # ID
                                if eid := view.get_id_input("Entry"):
                                    msg = db.delete_entry(eid)
                                    view.show_message(msg)
                                    if "Неможливо видалити" in msg:
                                        if view.confirm_cascade_delete("Запис має нагадування."):
                                            view.show_message(db.delete_entry_cascade(eid))
                            case '2':  # Author
                                if author := view.get_delete_criteria("Введіть Username автора"):
                                    msg = db.delete_entries_by_author(author)
                                    view.show_message(msg)
                                    if "Неможливо видалити" in msg:
                                        if view.confirm_cascade_delete(f"Записи автора '{author}' мають нагадування."):
                                            view.show_message(db.delete_entries_cascade_by_author(author))

                            # 3. Видалити всі записи
                            case '3':
                                if view.confirm_table_clear("Entry"):
                                    view.show_message(db.clear_table_entries())

                            case _:
                                pass

                    # === Видалення нагадувальника ===
                    case '3':
                        del_option = view.show_delete_options("Reminder")
                        match del_option:
                            case '1':
                                if rid := view.get_id_input("Reminder"): view.show_message(db.delete_reminder(rid))
                            case '2':
                                if date_str := view.get_delete_criteria("Введіть дату (YYYY-MM-DD)"):
                                    view.show_message(db.delete_reminders_by_date(date_str))
                            case '3':
                                status = view.get_status_input_simple()
                                if status is not None:
                                    view.show_message(db.delete_reminders_by_status(status))

                            case '4':
                                if view.confirm_table_clear("Reminder"):
                                    view.show_message(db.clear_table_reminders())

                            case _:
                                pass

            # --- 2. ДОДАВАННЯ ---
            case '2':
                entity_choice = view.show_entity_selection("Додавання даних")
                if entity_choice == '0': continue
                match entity_choice:
                    case '1':
                        if d := view.get_user_input(): view.show_message(db.add_user(*d))
                    case '2':
                        if d := view.get_entry_input(): view.show_message(db.add_entry(*d))
                    case '3':
                        if d := view.get_reminder_input(): view.show_message(db.add_reminder(*d))
                    case _:
                        view.show_message("Невірний вибір.")

            # --- 1. ПЕРЕГЛЯД ---
            case '1':
                entity_choice = view.show_entity_selection("Перегляд таблиці")
                if entity_choice == '0': continue
                match entity_choice:
                    case '1':
                        view.print_table(["ID", "Username", "Email"], db.get_top_users())
                    case '2':
                        view.print_table(["ID", "Title", "Text", "User ID"], db.get_top_entries())
                    case '3':
                        view.print_table(["ID", "Entry ID", "Date", "Active"], db.get_top_reminders())
                    case _:
                        view.show_message("Невірний вибір.")

            # --- Помилка вводу головного меню ---
            case _:
                view.show_message("Невірний вибір меню. Спробуйте ще раз.")


if __name__ == "__main__":
    run()