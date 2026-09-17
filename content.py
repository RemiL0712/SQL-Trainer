"""Course content. Add a level here without changing application logic."""

LEVELS = [
    dict(title="Основы SQL", topic="SELECT · FROM · LIMIT", theory="SQL помогает задавать вопросы таблицам. SELECT выбирает столбцы, FROM указывает таблицу, LIMIT ограничивает число строк.", example="SELECT name, city\nFROM users\nLIMIT 3;", tasks=[
        ("Имена пользователей", "Выведи имена всех пользователей.", "SELECT name FROM users", "Начни с SELECT name.", "Таблица называется users.", "SELECT name FROM users;", "SELECT выбирает только столбец name."),
        ("Первые три товара · финал", "Покажи название и цену первых трёх товаров.", "SELECT name, price FROM products LIMIT 3", "Нужны два столбца.", "Используй LIMIT 3 после FROM products.", "SELECT name, price FROM products LIMIT 3;", "LIMIT оставляет три первые строки в исходном порядке."),
    ]),
    dict(title="Фильтрация", topic="WHERE · AND · OR · IN · LIKE", theory="WHERE оставляет строки, которые удовлетворяют условию. Условия можно соединять через AND и OR; LIKE ищет по шаблону, IN проверяет набор значений.", example="SELECT name\nFROM users\nWHERE age >= 18;", tasks=[
        ("Совершеннолетние", "Выведи имена пользователей старше 25 лет.", "SELECT name FROM users WHERE age > 25", "Добавь условие WHERE.", "Возраст должен быть строго больше 25.", "SELECT name FROM users WHERE age > 25;", "WHERE фильтрует строки до вывода результата."),
        ("Жители Берлина · финал", "Покажи имена и возраст пользователей из Берлина.", "SELECT name, age FROM users WHERE city = 'Берлин'", "Сравни столбец city.", "Строковое значение заключи в одинарные кавычки.", "SELECT name, age FROM users WHERE city = 'Берлин';", "Условие по городу оставило только подходящих пользователей."),
    ]),
    dict(title="Сортировка", topic="ORDER BY · ASC · DESC · OFFSET", theory="ORDER BY задаёт порядок строк. DESC сортирует по убыванию, ASC — по возрастанию. LIMIT и OFFSET помогают получать части результата.", example="SELECT name, price\nFROM products\nORDER BY price DESC\nLIMIT 3;", tasks=[
        ("По цене", "Покажи названия и цены товаров от самых дорогих к дешёвым.", "SELECT name, price FROM products ORDER BY price DESC", "Отсортируй по price.", "Для убывания добавь DESC.", "SELECT name, price FROM products ORDER BY price DESC;", "ORDER BY price DESC ставит высокие цены первыми."),
        ("Два самых молодых · финал", "Выведи имена и возраст двух самых молодых пользователей.", "SELECT name, age FROM users ORDER BY age ASC LIMIT 2", "Сортируй по age.", "Возьми первые две строки через LIMIT 2.", "SELECT name, age FROM users ORDER BY age LIMIT 2;", "По умолчанию сортировка идёт по возрастанию."),
    ]),
    dict(title="Агрегация", topic="COUNT · SUM · AVG · GROUP BY", theory="Агрегатные функции сводят множество строк к числу. GROUP BY создаёт группы, для каждой из которых можно вычислить COUNT, SUM или AVG.", example="SELECT city, COUNT(*) AS total\nFROM users\nGROUP BY city;", tasks=[
        ("Сколько пользователей", "Посчитай всех пользователей. Назови столбец total.", "SELECT COUNT(*) AS total FROM users", "Используй COUNT(*).", "Добавь псевдоним AS total.", "SELECT COUNT(*) AS total FROM users;", "COUNT(*) считает строки, включая строки с пустыми значениями."),
        ("По городам · финал", "Посчитай пользователей в каждом городе. Выведи city и total.", "SELECT city, COUNT(*) AS total FROM users GROUP BY city", "Нужно сгруппировать строки.", "Добавь GROUP BY city.", "SELECT city, COUNT(*) AS total FROM users GROUP BY city;", "GROUP BY city создаёт отдельную группу для каждого города."),
    ], required="GROUP BY"),
    dict(title="Фильтрация групп", topic="HAVING", theory="WHERE фильтрует исходные строки, а HAVING — уже посчитанные группы. Обычно HAVING стоит после GROUP BY.", example="SELECT city, COUNT(*) AS total\nFROM users\nGROUP BY city\nHAVING COUNT(*) > 1;", tasks=[
        ("Города с несколькими жителями", "Покажи city и total только для городов, где более одного пользователя.", "SELECT city, COUNT(*) AS total FROM users GROUP BY city HAVING COUNT(*) > 1", "Сначала сгруппируй по городу.", "Отфильтруй группы через HAVING COUNT(*) > 1.", "SELECT city, COUNT(*) AS total FROM users GROUP BY city HAVING COUNT(*) > 1;", "HAVING проверяет размер уже сформированной группы."),
        ("Популярные категории · финал", "Покажи category и total для категорий, где больше одного товара.", "SELECT category, COUNT(*) AS total FROM products GROUP BY category HAVING COUNT(*) > 1", "Группируй по category.", "Для проверки количества групп используй HAVING.", "SELECT category, COUNT(*) AS total FROM products GROUP BY category HAVING COUNT(*) > 1;", "HAVING оставляет группы после подсчёта товаров."),
    ], required="HAVING"),
    dict(title="Соединения", topic="INNER JOIN · LEFT JOIN", theory="JOIN объединяет строки двух таблиц по общему ключу. INNER JOIN оставляет совпадения, LEFT JOIN сохраняет и строки слева без пары.", example="SELECT users.name, orders.total\nFROM users\nJOIN orders ON users.id = orders.user_id;", tasks=[
        ("Покупатели и заказы", "Покажи имя пользователя и сумму каждого заказа: name, total.", "SELECT users.name, orders.total FROM users JOIN orders ON users.id = orders.user_id", "Свяжи users и orders.", "Ключ связи: users.id = orders.user_id.", "SELECT users.name, orders.total FROM users JOIN orders ON users.id = orders.user_id;", "JOIN сопоставил каждый заказ с его пользователем."),
        ("Все пользователи · финал", "Покажи имя каждого пользователя и сумму заказа, если он есть: name, total. Сохрани пользователей без заказов.", "SELECT users.name, orders.total FROM users LEFT JOIN orders ON users.id = orders.user_id", "Нужен LEFT JOIN.", "Таблица users должна стоять слева.", "SELECT users.name, orders.total FROM users LEFT JOIN orders ON users.id = orders.user_id;", "LEFT JOIN сохраняет пользователей без заказов, показывая NULL в total."),
    ], required="JOIN"),
    dict(title="Подзапросы", topic="IN · EXISTS · вложенный SELECT", theory="Подзапрос — запрос внутри другого запроса. Его результат можно использовать в IN, EXISTS или сравнении со значением.", example="SELECT name\nFROM users\nWHERE id IN (SELECT user_id FROM orders);", tasks=[
        ("Пользователи с заказами", "Через подзапрос выведи имена пользователей, у которых есть заказы.", "SELECT name FROM users WHERE id IN (SELECT user_id FROM orders)", "Подзапрос должен вернуть user_id.", "Используй WHERE id IN (...).", "SELECT name FROM users WHERE id IN (SELECT user_id FROM orders);", "IN сверяет id пользователя со списком id из заказов."),
        ("Товары дороже среднего · финал", "Выведи названия товаров с ценой выше средней по всем товарам.", "SELECT name FROM products WHERE price > (SELECT AVG(price) FROM products)", "Найди среднюю цену через AVG.", "Помести SELECT AVG(price) в скобки.", "SELECT name FROM products WHERE price > (SELECT AVG(price) FROM products);", "Скалярный подзапрос вычислил порог для сравнения."),
    ], required="SELECT"),
    dict(title="Условная логика", topic="CASE WHEN", theory="CASE WHEN создаёт значение в зависимости от условия. Заканчивается ключевым словом END; псевдоним задаётся через AS.", example="SELECT name, CASE WHEN age >= 18 THEN 'adult' ELSE 'minor' END AS status\nFROM users;", tasks=[
        ("Возрастная группа", "Покажи name и status: 'adult' при age >= 18, иначе 'minor'.", "SELECT name, CASE WHEN age >= 18 THEN 'adult' ELSE 'minor' END AS status FROM users", "Начни с CASE WHEN age >= 18.", "После ELSE добавь END AS status.", "SELECT name, CASE WHEN age >= 18 THEN 'adult' ELSE 'minor' END AS status FROM users;", "CASE вычисляет значение отдельно для каждой строки."),
        ("Ценовой сегмент · финал", "Покажи name и segment: 'premium' при price >= 1000, иначе 'basic'.", "SELECT name, CASE WHEN price >= 1000 THEN 'premium' ELSE 'basic' END AS segment FROM products", "Проверяй price >= 1000.", "Заверши выражение END AS segment.", "SELECT name, CASE WHEN price >= 1000 THEN 'premium' ELSE 'basic' END AS segment FROM products;", "CASE помогает классифицировать товары в запросе."),
    ], required="CASE"),
    dict(title="Даты и строки", topic="date · UPPER · LENGTH", theory="Функции SQL помогают преобразовывать даты и строки. В SQLite date() извлекает дату, UPPER() переводит текст в верхний регистр, LENGTH() считает символы.", example="SELECT name, UPPER(city) AS city_upper\nFROM users;", tasks=[
        ("Город заглавными", "Покажи name и city_upper — город в верхнем регистре.", "SELECT name, UPPER(city) AS city_upper FROM users", "Используй UPPER(city).", "Назови столбец city_upper.", "SELECT name, UPPER(city) AS city_upper FROM users;", "UPPER преобразует текст каждого значения city."),
        ("Дата заказа · финал", "Покажи id и order_date — только дату без времени из created_at таблицы orders.", "SELECT id, date(created_at) AS order_date FROM orders", "Используй date(created_at).", "Назови столбец order_date.", "SELECT id, date(created_at) AS order_date FROM orders;", "date() извлекает календарную дату из времени заказа."),
    ]),
    dict(title="Продвинутый SQL", topic="CTE · ROW_NUMBER · оконные функции", theory="CTE через WITH делает сложный запрос читаемее. Оконные функции вычисляют значение для строки с учётом соседних строк, не сворачивая результат.", example="SELECT name, price, ROW_NUMBER() OVER (ORDER BY price DESC) AS position\nFROM products;", tasks=[
        ("Рейтинг товаров", "Покажи name, price и position — номер товара в порядке убывания цены.", "SELECT name, price, ROW_NUMBER() OVER (ORDER BY price DESC) AS position FROM products", "Используй ROW_NUMBER() OVER (...).", "В окне сортируй по price DESC.", "SELECT name, price, ROW_NUMBER() OVER (ORDER BY price DESC) AS position FROM products;", "ROW_NUMBER нумерует строки в заданном порядке."),
        ("CTE дорогих товаров · финал", "Через CTE expensive выведи имена товаров с price >= 1000.", "WITH expensive AS (SELECT name FROM products WHERE price >= 1000) SELECT name FROM expensive", "Начни с WITH expensive AS (...).", "Затем SELECT name FROM expensive.", "WITH expensive AS (SELECT name FROM products WHERE price >= 1000) SELECT name FROM expensive;", "CTE даёт имя промежуточному результату запроса."),
    ], required="WITH"),
]

SCHEMA = """
CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, email TEXT, age INTEGER, city TEXT);
INSERT INTO users VALUES (1,'Амалия','amalia@example.com',25,'Берлин'),(2,'Лео','leo@example.com',17,'Вена'),(3,'Алиса','alice@example.com',31,'Берлин'),(4,'Эмма','emma@example.com',28,'Прага'),(5,'Ноа','noah@example.com',22,'Вена');
CREATE TABLE products(id INTEGER PRIMARY KEY, name TEXT, price INTEGER, category TEXT);
INSERT INTO products VALUES (1,'Ноутбук',75000,'Электроника'),(2,'Наушники',3500,'Электроника'),(3,'Книга',850,'Книги'),(4,'Тетрадь',200,'Книги'),(5,'Лампа',1800,'Дом');
CREATE TABLE orders(id INTEGER PRIMARY KEY, user_id INTEGER, total INTEGER, created_at TEXT);
INSERT INTO orders VALUES (1,1,3500,'2026-01-12 10:30:00'),(2,3,75000,'2026-02-03 14:20:00'),(3,1,850,'2026-03-18 09:15:00'),(4,4,1800,'2026-04-09 18:00:00');
"""

# Extra practice is kept separate from the initial course so each topic can grow
# without changing the renderer or progression logic.
SCHEMA += """
CREATE TABLE departments(id INTEGER PRIMARY KEY, name TEXT, city TEXT);
INSERT INTO departments VALUES (1,'Разработка','Берлин'),(2,'Продажи','Вена'),(3,'Поддержка','Братислава');
CREATE TABLE employees(id INTEGER PRIMARY KEY, name TEXT, department_id INTEGER, manager_id INTEGER, salary INTEGER);
INSERT INTO employees VALUES (1,'София',1,NULL,120000),(2,'Лукас',1,1,90000),(3,'Эмилия',2,NULL,95000),(4,'Даниэль',2,3,65000),(5,'Оливия',3,NULL,70000);
CREATE TABLE order_items(id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER);
INSERT INTO order_items VALUES (1,1,2,1),(2,2,1,1),(3,3,3,1),(4,4,5,1);
CREATE TABLE reviews(id INTEGER PRIMARY KEY, user_id INTEGER, product_id INTEGER, rating INTEGER, comment TEXT);
INSERT INTO reviews VALUES (1,1,2,5,'Удобно'),(2,3,1,4,NULL),(3,4,5,NULL,'Без оценки'),(4,2,3,3,NULL);
CREATE TABLE inventory(id INTEGER PRIMARY KEY, product_id INTEGER, quantity INTEGER, status TEXT);
INSERT INTO inventory VALUES (1,1,4,'active'),(2,2,12,'active'),(3,3,0,'empty'),(4,4,25,'active');
"""

from curriculum_extra import enrich_course
enrich_course(LEVELS)
