import time
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, func, text, select
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# --- ОГОЛОШЕННЯ БАЗОВИХ КЛАСІВ ORM ---
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True)  # Autoincrement за замовчуванням
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)

    # Зв'язок 1:M (User -> Entries)
    entries = relationship("Entry", back_populates="user", cascade="all, delete-orphan")


class Entry(Base):
    __tablename__ = 'entry'
    __table_args__ = {'schema': 'public'}

    entry_id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    text = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('public.user.id'), nullable=False)

    # Зв'язки
    user = relationship("User", back_populates="entries")
    reminders = relationship("Reminder", back_populates="entry", cascade="all, delete-orphan")


class Reminder(Base):
    __tablename__ = 'reminder'
    __table_args__ = {'schema': 'public'}

    reminder_id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey('public.entry.entry_id'), nullable=False)
    remind_at = Column(DateTime, nullable=False)
    active = Column(Boolean, default=True)

    # Зв'язки
    entry = relationship("Entry", back_populates="reminders")


# --- ГОЛОВНИЙ КЛАС МОДЕЛІ ---
class Model:
    def __init__(self, db_name, user, password, host, port):
        # Формування URL підключення для SQLAlchemy
        self.db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"
        self.engine = None
        self.Session = None
        self.session = None

    def connect(self):
        try:
            self.engine = create_engine(self.db_url, echo=False)  # echo=True для налагодження SQL

            # Створення таблиць, якщо їх немає (автоматична генерація схеми)
            Base.metadata.create_all(self.engine)

            self.Session = sessionmaker(bind=self.engine)
            self.session = self.Session()
            return True
        except Exception as e:
            print(f"Помилка підключення: {e}")
            return False

    def disconnect(self):
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()

    # --- ВИВЕДЕННЯ ТОП-10 ---
    # Примітка: View очікує список кортежів (tuples), тому ми конвертуємо об'єкти.

    def get_top_users(self, limit=10):
        try:
            users = self.session.query(User).order_by(User.id).limit(limit).all()
            return [(u.id, u.username, u.email) for u in users]
        except Exception as e:
            return str(e)

    def get_top_entries(self, limit=10):
        try:
            entries = self.session.query(Entry).order_by(Entry.entry_id).limit(limit).all()
            return [(e.entry_id, e.title, e.text, e.user_id) for e in entries]
        except Exception as e:
            return str(e)

    def get_top_reminders(self, limit=10):
        try:
            rems = self.session.query(Reminder).order_by(Reminder.reminder_id).limit(limit).all()
            return [(r.reminder_id, r.entry_id, r.remind_at, r.active) for r in rems]
        except Exception as e:
            return str(e)

    # --- ДОДАВАННЯ (CREATE) ---
    def add_user(self, user_id, username, email, password):
        try:
            # Якщо user_id передано явно, використовуємо його, інакше автоінкремент
            new_user = User(username=username, email=email, password=password)
            if user_id is not None:
                new_user.id = user_id

            self.session.add(new_user)
            self.session.commit()
            return "Користувача успішно додано."
        except IntegrityError:
            self.session.rollback()
            return "Помилка: Такий ID, email або username вже існує."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    def add_entry(self, entry_id, title, text, user_id):
        try:
            new_entry = Entry(title=title, text=text, user_id=user_id)
            if entry_id is not None:
                new_entry.entry_id = entry_id

            self.session.add(new_entry)
            self.session.commit()
            return "Запис успішно додано."
        except IntegrityError:
            self.session.rollback()
            return f"Помилка: User ID {user_id} не існує або дублювання ID."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    def add_reminder(self, reminder_id, entry_id, remind_at, active):
        try:
            # Перетворення рядка дати у об'єкт datetime (якщо це рядок), хоча SQLAlchemy може сама це зробити
            new_rem = Reminder(entry_id=entry_id, remind_at=remind_at, active=active)
            if reminder_id is not None:
                new_rem.reminder_id = reminder_id

            self.session.add(new_rem)
            self.session.commit()
            return "Нагадування успішно додано."
        except IntegrityError:
            self.session.rollback()
            return f"Помилка: Entry ID {entry_id} не існує."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    # --- ВИДАЛЕННЯ (DELETE) ---
    def delete_user(self, user_id):
        try:
            user = self.session.get(User, user_id)
            if not user:
                return "ID не знайдено."

            self.session.delete(user)
            self.session.commit()
            return f"Користувача {user_id} видалено."
        except IntegrityError:
            self.session.rollback()
            return "Неможливо видалити: є пов'язані записи (спробуйте каскадне видалення)."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    def delete_entry(self, entry_id):
        try:
            entry = self.session.get(Entry, entry_id)
            if not entry:
                return "ID не знайдено."

            self.session.delete(entry)
            self.session.commit()
            return f"Запис {entry_id} видалено."
        except IntegrityError:
            self.session.rollback()
            return "Неможливо видалити: є пов'язані нагадування."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    def delete_reminder(self, reminder_id):
        try:
            rem = self.session.get(Reminder, reminder_id)
            if not rem:
                return "ID не знайдено."

            self.session.delete(rem)
            self.session.commit()
            return f"Нагадування {reminder_id} видалено."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    def delete_user_by_attr(self, attr_name, value):
        try:
            # Динамічний фільтр
            query = self.session.query(User).filter(getattr(User, attr_name) == value)
            count = query.count()

            if count == 0:
                return f"Користувача з {attr_name}='{value}' не знайдено."

            # Важливо: delete(synchronize_session=False) для масового видалення
            query.delete(synchronize_session=False)
            self.session.commit()
            return f"Видалено користувачів: {count}."
        except IntegrityError:
            self.session.rollback()
            return "Неможливо видалити: є пов'язані записи."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    def delete_entries_by_author(self, username):
        try:
            # Знаходимо ID юзера
            user = self.session.query(User).filter_by(username=username).first()
            if not user:
                return f"Автора '{username}' не знайдено."

            count = self.session.query(Entry).filter_by(user_id=user.id).delete()
            self.session.commit()

            if count > 0:
                return f"Видалено записів автора '{username}': {count}."
            return f"Записів автора '{username}' не знайдено."
        except IntegrityError:
            self.session.rollback()
            return "Неможливо видалити: є пов'язані нагадування."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    def delete_reminders_by_date(self, date_str):
        try:
            # Порівняння дати (cast до DATE)
            count = self.session.query(Reminder).filter(func.date(Reminder.remind_at) == date_str).delete(
                synchronize_session=False)
            self.session.commit()

            if count > 0:
                return f"Видалено нагадувань за {date_str}: {count}."
            return "Нагадувань за цю дату не знайдено."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    # --- КАСКАДНЕ ВИДАЛЕННЯ ---
    # В ORM це простіше, якщо в моделі вказано cascade="all, delete-orphan".
    # Але для надійності тут реалізовано явно, як вимагала логіка.

    def delete_user_cascade(self, user_id):
        try:
            user = self.session.get(User, user_id)
            if not user:
                return "Користувача не знайдено."

            # Завдяки cascade="all, delete-orphan" у моделі User, видалення юзера
            # автоматично видалить його entries, а ті - reminders.
            self.session.delete(user)
            self.session.commit()
            return f"Успішно видалено користувача {user_id} та всі його дані (через ORM cascade)."
        except Exception as e:
            self.session.rollback()
            return f"Помилка каскадного видалення: {e}"

    def delete_user_cascade_by_attr(self, attr_name, value):
        try:
            users = self.session.query(User).filter(getattr(User, attr_name) == value).all()
            if not users:
                return f"Користувача з {attr_name}='{value}' не знайдено."

            for u in users:
                self.session.delete(u)

            self.session.commit()
            return f"Успішно видалено користувачів ({len(users)}) та їх дані."
        except Exception as e:
            self.session.rollback()
            return f"Помилка каскаду: {e}"

    def delete_entry_cascade(self, entry_id):
        try:
            entry = self.session.get(Entry, entry_id)
            if not entry:
                return "Запис не знайдено."

            self.session.delete(entry)
            self.session.commit()
            return f"Успішно видалено запис {entry_id} та його нагадування."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    def delete_entries_cascade_by_author(self, username):
        try:
            user = self.session.query(User).filter_by(username=username).first()
            if not user:
                return "Автора не знайдено."

            # Видаляємо всі записи цього юзера. Каскад ORM підтягне нагадування.
            count = 0
            for entry in user.entries:
                self.session.delete(entry)
                count += 1

            self.session.commit()
            return f"Успішно видалено всі записи ({count}) та нагадування автора '{username}'."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    def delete_reminders_by_status(self, is_active):
        try:
            count = self.session.query(Reminder).filter_by(active=is_active).delete(synchronize_session=False)
            self.session.commit()
            status_str = "активних" if is_active else "неактивних"
            return f"Успішно видалено {count} {status_str} нагадувань."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    # --- ОЧИЩЕННЯ ТАБЛИЦЬ (TRUNCATE) ---
    # ORM не має прямого методу TRUNCATE, використовуємо execute(text(...))

    def clear_table_users(self):
        try:
            self.session.execute(text('TRUNCATE TABLE public."user" RESTART IDENTITY CASCADE'))
            self.session.commit()
            return "Таблицю Users (та всі залежні дані) очищено."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    def clear_table_entries(self):
        try:
            self.session.execute(text('TRUNCATE TABLE public.entry RESTART IDENTITY CASCADE'))
            self.session.commit()
            return "Таблицю Entries очищено."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    def clear_table_reminders(self):
        try:
            self.session.execute(text('TRUNCATE TABLE public.reminder RESTART IDENTITY CASCADE'))
            self.session.commit()
            return "Таблицю Reminders очищено."
        except Exception as e:
            self.session.rollback()
            return f"Помилка: {e}"

    # --- ПОШУК ЗА ID ---
    def find_user_by_id(self, user_id):
        try:
            u = self.session.get(User, user_id)
            return [(u.id, u.username, u.email, u.password)] if u else []
        except Exception as e:
            return str(e)

    def find_entry_by_id(self, entry_id):
        try:
            e = self.session.get(Entry, entry_id)
            return [(e.entry_id, e.title, e.text, e.user_id)] if e else []
        except Exception as e:
            return str(e)

    def find_reminder_by_id(self, reminder_id):
        try:
            r = self.session.get(Reminder, reminder_id)
            return [(r.reminder_id, r.entry_id, r.remind_at, r.active)] if r else []
        except Exception as e:
            return str(e)

    # --- ГНУЧКИЙ ПОШУК ---
    def search_flexible(self, filters):
        start_time = time.time()
        try:
            query = self.session.query(
                User.id,
                User.username,
                User.email,
                func.count(func.distinct(Entry.entry_id)),
                func.count(func.distinct(Reminder.reminder_id))
            ).outerjoin(Entry, User.id == Entry.user_id) \
                .outerjoin(Reminder, Entry.entry_id == Reminder.entry_id)

            # Застосування фільтрів
            if filters.get('username'):
                query = query.filter(User.username.ilike(f"%{filters['username']}%"))
            if filters.get('email'):
                query = query.filter(User.email.ilike(f"%{filters['email']}%"))
            if filters.get('title'):
                query = query.filter(Entry.title.ilike(f"%{filters['title']}%"))
            if filters.get('text'):
                query = query.filter(Entry.text.ilike(f"%{filters['text']}%"))
            if filters.get('is_active') is not None:
                query = query.filter(Reminder.active == filters['is_active'])
            if filters.get('date_from') and filters.get('date_to'):
                query = query.filter(Reminder.remind_at.between(filters['date_from'], filters['date_to']))

            # Групування
            query = query.group_by(User.id, User.username, User.email).order_by(User.id)

            results = query.all()
            # Результат вже є списком кортежів (tuple), конвертація не потрібна

            exec_time = (time.time() - start_time) * 1000
            return results, exec_time
        except Exception as e:
            return str(e), 0

    def get_user_entries_details(self, user_id):
        try:
            user = self.session.get(User, user_id)
            if not user:
                return "Користувача з таким ID не знайдено."

            # ORM lazy loading (або explicit join)
            res = [(e.entry_id, e.title, e.text) for e in user.entries]
            return user.username, res
        except Exception as e:
            return str(e), []

    def get_user_reminders_details(self, user_id):
        try:
            user = self.session.get(User, user_id)
            if not user:
                return "Користувача з таким ID не знайдено."

            # Складний запит через join, бо Reminders не напряму в User
            # Але ми можемо піти через entries в Python або зробити Join query
            query = self.session.query(Reminder.reminder_id, Entry.title, Reminder.remind_at, Reminder.active) \
                .join(Entry) \
                .filter(Entry.user_id == user_id) \
                .order_by(Reminder.remind_at)

            results = query.all()
            return user.username, results
        except Exception as e:
            return str(e), []

    # --- ГЕНЕРАЦІЯ ДАНИХ ---
    # Використання raw SQL тут виправдано продуктивністю, але ми обгорнемо в text()
    # Або можна переписати на ORM Bulk Inserts (session.bulk_save_objects),
    # але для збереження швидкості генерації тисяч записів краще залишити insert...select.

    def generate_users(self, count):
        start_time = time.time()
        try:
            # Визначаємо start_id
            max_id = self.session.query(func.max(User.id)).scalar() or 0
            start_id = max_id + 1

            sql = text("""
                INSERT INTO public."user" (id, username, email, password)
                SELECT 
                    i, 
                    'User_' || i || '_' || substr(md5(random()::text), 1, 5),
                    'user' || i || '@gen.com',
                    substr(md5(random()::text), 1, 10)
                FROM generate_series(:start, :end) AS i
                ON CONFLICT DO NOTHING
            """)
            self.session.execute(sql, {'start': start_id, 'end': start_id + count - 1})
            self.session.commit()

            exec_time = (time.time() - start_time) * 1000
            return f"Успішно згенеровано {count} користувачів за {exec_time:.2f} мс."
        except Exception as e:
            self.session.rollback()
            return f"Помилка генерації User: {e}"

    def generate_entries(self, count):
        if self.session.query(User).count() == 0:
            return "Помилка: Немає користувачів!"

        start_time = time.time()
        try:
            max_id = self.session.query(func.max(Entry.entry_id)).scalar() or 0
            start_id = max_id + 1

            sql = text("""
                INSERT INTO public.entry (entry_id, title, text, user_id)
                SELECT 
                    i,
                    'Title_' || substr(md5(random()::text), 1, 8),
                    'Text content ' || i,
                    (SELECT id FROM public."user" ORDER BY random() LIMIT 1)
                FROM generate_series(:start, :end) AS i
            """)
            self.session.execute(sql, {'start': start_id, 'end': start_id + count - 1})
            self.session.commit()

            exec_time = (time.time() - start_time) * 1000
            return f"Успішно згенеровано {count} записів за {exec_time:.2f} мс."
        except Exception as e:
            self.session.rollback()
            return f"Помилка генерації Entry: {e}"

    def generate_reminders(self, count):
        if self.session.query(Entry).count() == 0:
            return "Помилка: Немає записів!"

        start_time = time.time()
        try:
            max_id = self.session.query(func.max(Reminder.reminder_id)).scalar() or 0
            start_id = max_id + 1

            sql = text("""
                INSERT INTO public.reminder (reminder_id, entry_id, remind_at, active)
                SELECT 
                    i,
                    (SELECT entry_id FROM public.entry ORDER BY random() LIMIT 1),
                    NOW() + (random() * (INTERVAL '1 year')),
                    (random() > 0.5)
                FROM generate_series(:start, :end) AS i
            """)
            self.session.execute(sql, {'start': start_id, 'end': start_id + count - 1})
            self.session.commit()

            exec_time = (time.time() - start_time) * 1000
            return f"Успішно згенеровано {count} нагадувань за {exec_time:.2f} мс."
        except Exception as e:
            self.session.rollback()
            return f"Помилка генерації Reminder: {e}"

    # --- РЕДАГУВАННЯ (UPDATE) ---
    def update_user(self, current_id, new_id, new_username, new_email, new_password):
        try:
            user = self.session.get(User, current_id)
            if not user:
                return "Користувача не знайдено."

            # Оновлюємо поля
            user.id = new_id
            user.username = new_username
            user.email = new_email
            user.password = new_password

            self.session.commit()
            return "Користувача успішно оновлено."
        except IntegrityError:
            self.session.rollback()
            return "Помилка: Такий ID, Username або Email вже зайняті, або ID використовується в FK."
        except Exception as e:
            self.session.rollback()
            return f"Помилка оновлення: {e}"

    def update_entry(self, current_id, new_id, new_title, new_text, new_user_id):
        try:
            entry = self.session.get(Entry, current_id)
            if not entry:
                return "Запис не знайдено."

            entry.entry_id = new_id
            entry.title = new_title
            entry.text = new_text
            entry.user_id = new_user_id

            self.session.commit()
            return "Запис успішно оновлено."
        except IntegrityError:
            self.session.rollback()
            return f"Помилка: User ID {new_user_id} не існує."
        except Exception as e:
            self.session.rollback()
            return f"Помилка оновлення: {e}"

    def update_reminder(self, current_id, new_id, new_entry_id, new_date, new_active):
        try:
            rem = self.session.get(Reminder, current_id)
            if not rem:
                return "Нагадування не знайдено."

            rem.reminder_id = new_id
            rem.entry_id = new_entry_id
            rem.remind_at = new_date
            rem.active = new_active

            self.session.commit()
            return "Нагадування успішно оновлено."
        except IntegrityError:
            self.session.rollback()
            return f"Помилка: Entry ID {new_entry_id} не існує."
        except Exception as e:
            self.session.rollback()
            return f"Помилка оновлення: {e}"

    # --- ПОВНЕ ОЧИЩЕННЯ БАЗИ ---
    def delete_all_data(self):
        try:
            # Очищення всіх таблиць з каскадом
            self.session.execute(
                text('TRUNCATE TABLE public."user", public.entry, public.reminder RESTART IDENTITY CASCADE'))
            self.session.commit()
            return "Всі таблиці успішно очищено. База даних порожня."
        except Exception as e:
            self.session.rollback()
            return f"Критична помилка очищення: {e}"