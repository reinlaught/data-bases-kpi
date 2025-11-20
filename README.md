# Розрахунково-графічна робота

**Проектування бази даних та ознайомлення з базовими операціями СУБД
PostgreSQL та Створення додатку бази даних, орієнтованого на 
взаємодію з СУБД PostgreSQL**

## Мета роботи

Здобуття навичок проєктування реляційних баз даних та практичного
використання PostgreSQL.

## Варіант

**Електронний журнал для ведення особистого щоденника**

## Структура бази даних

### Сутності

#### 1. user

-   id (integer, PK, UNIQUE, NOT NULL)
-   username (varchar, UNIQUE, NOT NULL)
-   email (varchar, UNIQUE, NOT NULL)
-   password (varchar, NOT NULL)

#### 2. entry

-   entry_id (integer, PK, UNIQUE, NOT NULL)
-   title (varchar)
-   text (varchar)
-   user_id (integer, FK, NOT NULL)

#### 3. reminder

-   reminder_id (integer, PK, UNIQUE, NOT NULL)
-   entry_id (integer, FK, NOT NULL)
-   remind_at (timestamp with time zone)
-   active (boolean, NOT NULL)

### Зв'язки

-   User → Entry (1:N)
-   Entry → Reminder (1:N)

### Нормалізація

Базу даних приведено до 3НФ: - атрибути атомарні\
- немає часткових залежностей\
- немає транзитивних залежностей
### Технології
-   Мова програмування: Python
-   Платформа: Python 3.10+
-   База даних: PostgreSQL
-   Бібліотека для роботи з БД: psycopg (psycopg3)
