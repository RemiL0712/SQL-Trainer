"""Additional exercises and advanced modules for the SQL course."""


def exercise(row, mode="read", target=None, required=None):
    title, prompt, sql, hint1, hint2, explanation = row
    meta = {"mode": mode}
    if target:
        meta["target"] = target
    if required:
        meta["required"] = required
    return (title, prompt, sql, hint1, hint2, sql.rstrip(";") + ";", explanation, meta)


EXTRA = [
    [
        ("Все данные", "Выведи все столбцы таблицы users.", "SELECT * FROM users", "Звёздочка означает все столбцы.", "После FROM укажи users.", "SELECT * показывает полные строки таблицы."),
        ("Адреса почты", "Выведи id и email всех пользователей.", "SELECT id, email FROM users", "Перечисли два столбца после SELECT.", "Между столбцами поставь запятую.", "Список после SELECT определяет форму результата."),
        ("Каталог", "Выведи id, name и category всех товаров.", "SELECT id, name, category FROM products", "Товары лежат в products.", "Выбери три указанных столбца.", "FROM products направляет запрос к каталогу товаров."),
        ("Псевдоним", "Покажи name товара под названием product_name.", "SELECT name AS product_name FROM products", "Для переименования есть AS.", "Псевдоним пишется после имени столбца.", "AS меняет имя столбца в результате, не меняя таблицу."),
        ("Вычисляемый столбец", "Покажи name и double_price, равный price * 2, для каждого товара.", "SELECT name, price * 2 AS double_price FROM products", "Выражения можно писать после SELECT.", "Умножь price на 2 и добавь AS double_price.", "SQL умеет вычислять новые столбцы прямо в запросе."),
    ],
    [
        ("Возрастной порог", "Покажи name и age пользователей от 18 лет включительно.", "SELECT name, age FROM users WHERE age >= 18", "Добавь WHERE по age.", "Включительно означает >=.", "WHERE проверяет условие отдельно для каждой строки."),
        ("Два условия", "Выведи имена пользователей из Москвы старше 25 лет.", "SELECT name FROM users WHERE city = 'Москва' AND age > 25", "Нужны два условия.", "Соедини их оператором AND.", "AND требует выполнения обоих условий."),
        ("Два города", "Выведи имена пользователей из Москвы или Казани.", "SELECT name FROM users WHERE city IN ('Москва','Казань')", "Можно использовать IN.", "Передай два города в скобках.", "IN проверяет принадлежность значению из списка."),
        ("Диапазон цен", "Покажи имена товаров с ценой от 500 до 4000 включительно.", "SELECT name FROM products WHERE price BETWEEN 500 AND 4000", "Используй BETWEEN.", "BETWEEN включает обе границы.", "BETWEEN удобен для замкнутого диапазона."),
        ("Поиск в имени", "Покажи имена пользователей, начинающиеся с буквы А.", "SELECT name FROM users WHERE name LIKE 'А%'", "LIKE принимает шаблон.", "Процент означает любое продолжение строки.", "LIKE 'А%' находит строки с заданным началом."),
    ],
    [
        ("Возраст по убыванию", "Покажи name и age от старших к младшим.", "SELECT name, age FROM users ORDER BY age DESC", "Используй ORDER BY age.", "Убывание обозначается DESC.", "ORDER BY меняет порядок строк результата."),
        ("Цена по возрастанию", "Покажи name и price от дешёвых к дорогим.", "SELECT name, price FROM products ORDER BY price ASC", "Сортируй по price.", "ASC означает возрастание.", "ASC задаёт возрастающий порядок."),
        ("Дорогая пара", "Покажи name и price двух самых дорогих товаров.", "SELECT name, price FROM products ORDER BY price DESC LIMIT 2", "Сначала отсортируй цены.", "Затем оставь две строки через LIMIT.", "LIMIT применяется к уже отсортированному результату."),
        ("Страница каталога", "Покажи name второго и третьего товаров по id.", "SELECT name FROM products ORDER BY id LIMIT 2 OFFSET 1", "Сначала зафиксируй порядок по id.", "OFFSET 1 пропускает первую строку.", "LIMIT и OFFSET позволяют получать страницы результата."),
        ("Два ключа сортировки", "Покажи city, name пользователей: сначала по городу, затем по имени.", "SELECT city, name FROM users ORDER BY city, name", "ORDER BY принимает несколько столбцов.", "Перечисли city, затем name.", "Второй ключ сортирует строки с одинаковым первым ключом."),
    ],
    [
        ("Средняя цена", "Вычисли среднюю цену товаров как avg_price.", "SELECT AVG(price) AS avg_price FROM products", "Используй AVG(price).", "Дай результату имя avg_price.", "AVG считает среднее по непустым значениям."),
        ("Сумма заказов", "Посчитай сумму всех заказов как revenue.", "SELECT SUM(total) AS revenue FROM orders", "Нужна функция SUM.", "Передай ей столбец total.", "SUM складывает значения выбранного столбца."),
        ("Границы цен", "Покажи min_price и max_price для товаров.", "SELECT MIN(price) AS min_price, MAX(price) AS max_price FROM products", "Нужны MIN и MAX.", "Назови два результирующих столбца.", "MIN и MAX находят границы набора значений."),
        ("Средняя цена категории", "Покажи category и avg_price для каждой категории.", "SELECT category, AVG(price) AS avg_price FROM products GROUP BY category", "Группируй по category.", "Считай AVG(price) внутри каждой группы.", "GROUP BY делает отдельный расчёт для каждой категории."),
        ("Заказы покупателей", "Покажи user_id и orders_count — число заказов каждого покупателя.", "SELECT user_id, COUNT(*) AS orders_count FROM orders GROUP BY user_id", "Группируй по user_id.", "Для числа заказов используй COUNT(*).", "COUNT(*) считает заказы внутри каждой группы покупателя."),
    ],
    [
        ("Крупные заказы", "Покажи user_id и orders_count только для покупателей с двумя и более заказами.", "SELECT user_id, COUNT(*) AS orders_count FROM orders GROUP BY user_id HAVING COUNT(*) >= 2", "Сначала группируй по user_id.", "Количество групп проверь через HAVING.", "HAVING отбирает покупателей после группировки заказов."),
        ("Дорогие категории", "Покажи category и avg_price для категорий со средней ценой выше 1000.", "SELECT category, AVG(price) AS avg_price FROM products GROUP BY category HAVING AVG(price) > 1000", "Посчитай AVG(price) по category.", "Порог относится к группе, поэтому нужен HAVING.", "HAVING может сравнивать результат агрегатной функции."),
        ("Возраст городов", "Покажи city и avg_age для городов со средним возрастом выше 25.", "SELECT city, AVG(age) AS avg_age FROM users GROUP BY city HAVING AVG(age) > 25", "Группируй по city.", "Условие по AVG(age) помести в HAVING.", "Группы фильтруются по своему среднему возрасту."),
        ("Сумма по покупателю", "Покажи user_id и revenue для покупателей с суммой заказов более 4000.", "SELECT user_id, SUM(total) AS revenue FROM orders GROUP BY user_id HAVING SUM(total) > 4000", "Нужны SUM и GROUP BY.", "Отбирай группы через HAVING SUM(total) > 4000.", "Сумма заказов вычисляется отдельно по каждому user_id."),
        ("Категории с низкой ценой", "Покажи category и min_price там, где минимальная цена ниже 500.", "SELECT category, MIN(price) AS min_price FROM products GROUP BY category HAVING MIN(price) < 500", "Посчитай MIN(price) в группе.", "Проверь минимум через HAVING.", "HAVING работает с минимальным значением каждой категории."),
    ],
    [
        ("ID заказа и имя", "Покажи orders.id как order_id и users.name для каждого заказа.", "SELECT orders.id AS order_id, users.name FROM orders JOIN users ON orders.user_id = users.id", "Свяжи orders с users.", "Используй orders.user_id = users.id.", "JOIN добавляет к заказу данные его владельца."),
        ("Количество заказов для всех", "Покажи users.name и orders_count для всех пользователей, включая тех без заказов.", "SELECT users.name, COUNT(orders.id) AS orders_count FROM users LEFT JOIN orders ON users.id = orders.user_id GROUP BY users.id", "Начни с users LEFT JOIN orders.", "Считай orders.id, чтобы отсутствующий заказ дал 0.", "LEFT JOIN сохраняет пользователей без заказа; COUNT(orders.id) даёт для них ноль."),
        ("Товары заказов", "Покажи orders.id как order_id и products.name как product_name для позиций заказов.", "SELECT orders.id AS order_id, products.name AS product_name FROM orders JOIN order_items ON orders.id = order_items.order_id JOIN products ON order_items.product_id = products.id", "Нужны три таблицы.", "Свяжи orders → order_items → products.", "Два JOIN проходят через таблицу позиций заказа."),
        ("Сотрудник и отдел", "Покажи employees.name как employee и departments.name как department.", "SELECT employees.name AS employee, departments.name AS department FROM employees JOIN departments ON employees.department_id = departments.id", "Соедини employees и departments.", "Ключ: department_id = departments.id.", "JOIN связывает внешний ключ сотрудника с отделом."),
        ("Сотрудник и руководитель", "Покажи имя сотрудника как employee и имя его руководителя как manager, включая руководителей без начальника.", "SELECT e.name AS employee, m.name AS manager FROM employees e LEFT JOIN employees m ON e.manager_id = m.id", "Это соединение таблицы с самой собой.", "Используй псевдонимы e и m и LEFT JOIN.", "Самосоединение показывает иерархию сотрудников."),
    ],
    [
        ("Старше среднего", "Выведи имена пользователей старше среднего возраста.", "SELECT name FROM users WHERE age > (SELECT AVG(age) FROM users)", "Сначала вычисли AVG(age).", "Помести вычисление в подзапрос в WHERE.", "Скалярный подзапрос возвращает порог для сравнения."),
        ("Покупатели без заказов", "Выведи имена пользователей, для которых нет заказов, через NOT EXISTS.", "SELECT name FROM users u WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id)", "Нужен коррелированный подзапрос.", "Проверь o.user_id = u.id внутри NOT EXISTS.", "NOT EXISTS истинно, когда подзапрос не нашёл ни одной строки."),
        ("Товары в заказах", "Через IN выведи имена товаров, которые встречаются в order_items.", "SELECT name FROM products WHERE id IN (SELECT product_id FROM order_items)", "Подзапрос должен вернуть product_id.", "Сравни products.id с результатом через IN.", "IN проверяет товар по набору идентификаторов из позиций заказов."),
        ("Заказы выше среднего", "Покажи id заказов с суммой выше средней суммы заказа.", "SELECT id FROM orders WHERE total > (SELECT AVG(total) FROM orders)", "Используй AVG(total) в подзапросе.", "Сравни внешний total с этим значением.", "Подзапрос вычисляет среднюю сумму один раз для сравнения."),
        ("Есть дорогой заказ", "Выведи имена пользователей, у которых есть заказ с total > 5000, через EXISTS.", "SELECT name FROM users u WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id AND o.total > 5000)", "Подзапрос зависит от внешнего пользователя.", "Свяжи o.user_id = u.id и проверь total.", "EXISTS проверяет наличие подходящего заказа для каждой строки users."),
    ],
    [
        ("Метка города", "Покажи name и region: 'capital' для Москвы, иначе 'other'.", "SELECT name, CASE WHEN city = 'Москва' THEN 'capital' ELSE 'other' END AS region FROM users", "Условие относится к city.", "Используй CASE WHEN ... THEN ... ELSE ... END.", "CASE создаёт текстовую метку по условию."),
        ("Бесплатная доставка", "Покажи id заказа и shipping: 'free' при total >= 5000, иначе 'paid'.", "SELECT id, CASE WHEN total >= 5000 THEN 'free' ELSE 'paid' END AS shipping FROM orders", "Проверяй total >= 5000.", "Назови результат shipping.", "CASE формирует категорию для каждого заказа."),
        ("Три категории цены", "Покажи name и tier: 'low' при price < 1000, 'mid' при price < 5000, иначе 'high'.", "SELECT name, CASE WHEN price < 1000 THEN 'low' WHEN price < 5000 THEN 'mid' ELSE 'high' END AS tier FROM products", "CASE может содержать несколько WHEN.", "Условия проверяются сверху вниз.", "Первое подходящее WHEN определяет значение tier."),
        ("Активный остаток", "Покажи id и availability: 'out' при quantity = 0, иначе 'in'.", "SELECT id, CASE WHEN quantity = 0 THEN 'out' ELSE 'in' END AS availability FROM inventory", "Проверь quantity = 0.", "Заверши выражение END AS availability.", "CASE переводит числовой остаток в понятный статус."),
        ("Условный подсчёт", "Посчитай взрослых пользователей как adults через SUM(CASE ...).", "SELECT SUM(CASE WHEN age >= 18 THEN 1 ELSE 0 END) AS adults FROM users", "CASE вернёт 1 для взрослого.", "Сложи значения через SUM.", "SUM(CASE ...) считает строки, удовлетворяющие условию."),
    ],
    [
        ("Нижний регистр", "Покажи name и city_lower — город в нижнем регистре.", "SELECT name, LOWER(city) AS city_lower FROM users", "Используй LOWER(city).", "Псевдоним результата — city_lower.", "LOWER преобразует текст, не меняя исходные данные."),
        ("Длина имени", "Покажи name и name_length — количество символов в имени.", "SELECT name, LENGTH(name) AS name_length FROM users", "Нужна функция LENGTH.", "Передай ей name и добавь псевдоним.", "LENGTH считает символы строки."),
        ("Почтовый домен", "Покажи email и domain — часть email после знака @.", "SELECT email, SUBSTR(email, INSTR(email, '@') + 1) AS domain FROM users", "Найди позицию @ через INSTR.", "SUBSTR начни со следующего символа.", "INSTR находит позицию, SUBSTR извлекает хвост строки."),
        ("Месяц заказа", "Покажи id и month в формате YYYY-MM из created_at.", "SELECT id, STRFTIME('%Y-%m', created_at) AS month FROM orders", "Используй STRFTIME.", "Формат для года и месяца: %Y-%m.", "STRFTIME форматирует дату по заданному шаблону."),
        ("Заказы после февраля", "Выведи id заказов с датой created_at не раньше 1 марта 2026 года.", "SELECT id FROM orders WHERE date(created_at) >= '2026-03-01'", "Сравни только календарную дату.", "Применяй date(created_at) в WHERE.", "date() отбрасывает время перед сравнением дат."),
    ],
    [
        ("CTE городов", "Через CTE city_counts покажи city и total пользователей по городам.", "WITH city_counts AS (SELECT city, COUNT(*) AS total FROM users GROUP BY city) SELECT city, total FROM city_counts", "Сначала создай city_counts через WITH.", "Во внешнем запросе выбери city и total из CTE.", "CTE именует промежуточный результат группировки."),
        ("Ранг цены", "Покажи name и price_rank через RANK по убыванию price.", "SELECT name, RANK() OVER (ORDER BY price DESC) AS price_rank FROM products", "Нужна оконная функция RANK().", "Сортировка находится внутри OVER.", "RANK присваивает одинаковый ранг равным значениям."),
        ("Сумма по категории", "Покажи name и category_total — сумму цен в категории товара.", "SELECT name, SUM(price) OVER (PARTITION BY category) AS category_total FROM products", "Используй SUM(price) OVER (...).", "PARTITION BY category задаёт группы окна.", "Оконная SUM сохраняет каждую строку и добавляет итог её категории."),
        ("Накопительный итог", "Покажи id заказа и running_total — сумму заказов по возрастанию id.", "SELECT id, SUM(total) OVER (ORDER BY id) AS running_total FROM orders", "Нужна оконная SUM.", "В OVER укажи ORDER BY id.", "Оконная сумма с порядком даёт накопительный итог."),
        ("Номер в отделе", "Покажи name и position — номер сотрудника по убыванию зарплаты внутри отдела.", "SELECT name, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS position FROM employees", "Нужны PARTITION BY и ORDER BY в окне.", "Раздели по department_id, отсортируй по salary DESC.", "ROW_NUMBER перезапускает нумерацию в каждом отделе."),
    ],
]


ADVANCED = [
    dict(title="NULL и уникальные значения", topic="IS NULL · COALESCE · DISTINCT", theory="NULL означает отсутствие значения. Сравнивать его через = нельзя: используй IS NULL или IS NOT NULL. COALESCE подставляет запасное значение, DISTINCT убирает повторы.", example="SELECT id, COALESCE(rating, 0) AS rating\nFROM reviews;", tasks=[
        ("Уникальные города", "Выведи каждый city из users только один раз.", "SELECT DISTINCT city FROM users", "Используй DISTINCT после SELECT.", "Выбери только city.", "DISTINCT убирает повторяющиеся города."),
        ("Отзывы без оценки", "Выведи id отзывов, в которых rating отсутствует.", "SELECT id FROM reviews WHERE rating IS NULL", "NULL проверяется особым оператором.", "Используй IS NULL, а не = NULL.", "IS NULL выбирает строки с отсутствующей оценкой."),
        ("Отзывы с оценкой", "Покажи id и rating отзывов, где оценка указана.", "SELECT id, rating FROM reviews WHERE rating IS NOT NULL", "Проверь наличие значения.", "Используй IS NOT NULL.", "IS NOT NULL исключает отзывы без оценки."),
        ("Запасная оценка", "Покажи id и score, подставив 0 вместо пустого rating.", "SELECT id, COALESCE(rating, 0) AS score FROM reviews", "Используй COALESCE.", "Первый аргумент — rating, второй — 0.", "COALESCE возвращает первое непустое значение."),
        ("Подсчёт оценок", "Покажи total_reviews и rated_reviews: число всех отзывов и число отзывов с оценкой.", "SELECT COUNT(*) AS total_reviews, COUNT(rating) AS rated_reviews FROM reviews", "Сравни COUNT(*) и COUNT(rating).", "COUNT(rating) игнорирует NULL.", "COUNT(*) учитывает строки, COUNT(rating) — непустые оценки."),
        ("Средняя оценка · финал", "Покажи avg_rating — среднее только по указанным оценкам.", "SELECT AVG(rating) AS avg_rating FROM reviews", "Используй AVG(rating).", "AVG автоматически пропускает NULL.", "Отсутствующая оценка не превращается в ноль при расчёте среднего."),
    ]),
    dict(title="Объединение результатов", topic="UNION · UNION ALL · INTERSECT · EXCEPT", theory="Операторы множеств соединяют результаты запросов с одинаковым числом столбцов. UNION убирает повторы, UNION ALL сохраняет их, INTERSECT оставляет общие строки, EXCEPT — строки только слева.", example="SELECT city FROM users\nUNION\nSELECT city FROM departments;", tasks=[
        ("Все города", "Покажи единый список городов пользователей и отделов без повторов.", "SELECT city FROM users UNION SELECT city FROM departments", "Оба SELECT должны возвращать city.", "Для удаления повторов используй UNION.", "UNION объединяет две выборки как множество."),
        ("Все записи городов", "Объедини города пользователей и отделов, сохранив повторы.", "SELECT city FROM users UNION ALL SELECT city FROM departments", "Нужны два SELECT city.", "Повторы сохраняет UNION ALL.", "UNION ALL складывает результаты без удаления повторов."),
        ("Города в обеих таблицах", "Покажи города, которые есть и у пользователей, и у отделов.", "SELECT city FROM users INTERSECT SELECT city FROM departments", "Ищи пересечение двух выборок.", "Используй INTERSECT.", "INTERSECT оставляет значения, найденные с обеих сторон."),
        ("Города без пользователей", "Покажи города отделов, в которых нет пользователей.", "SELECT city FROM departments EXCEPT SELECT city FROM users", "Вычитай города пользователей из городов отделов.", "Слева должны стоять departments.", "EXCEPT оставляет строки левого запроса, отсутствующие справа."),
        ("Города без отделов", "Покажи города пользователей, где нет отделов.", "SELECT city FROM users EXCEPT SELECT city FROM departments", "Порядок сторон важен.", "Слева должны стоять users.", "EXCEPT несимметричен: смена сторон меняет ответ."),
        ("Общий справочник · финал", "Покажи уникальные значения из users.city и products.category в одном столбце label.", "SELECT city AS label FROM users UNION SELECT category AS label FROM products", "Оба SELECT должны иметь один столбец.", "Назови результирующий столбец label.", "UNION позволяет собрать общий список значений из разных источников."),
    ], required="UNION"),
    dict(title="Изменение данных", topic="INSERT · UPDATE · DELETE", theory="INSERT добавляет строки, UPDATE меняет существующие, DELETE удаляет. В этом модуле каждая попытка выполняется в отдельной копии учебной базы. Ни аккаунт, ни другие упражнения не меняются.", example="UPDATE inventory\nSET quantity = 5\nWHERE id = 3;", tasks=[
        ("Новая позиция", "Добавь в inventory строку id=5, product_id=5, quantity=8, status='active'.", "INSERT INTO inventory(id,product_id,quantity,status) VALUES(5,5,8,'active')", "Используй INSERT INTO inventory.", "Перечисли столбцы и значения в одном порядке.", "INSERT добавляет новую строку в учебную копию inventory."),
        ("Две позиции", "Добавь строки (5,5,8,'active') и (6,5,3,'active') в inventory одним запросом.", "INSERT INTO inventory(id,product_id,quantity,status) VALUES(5,5,8,'active'),(6,5,3,'active')", "VALUES может содержать несколько наборов.", "Раздели две группы значений запятой.", "Один INSERT может добавить несколько строк."),
        ("Пополнение", "Измени quantity на 10 у строки inventory с id=3.", "UPDATE inventory SET quantity = 10 WHERE id = 3", "Используй UPDATE ... SET.", "Обязательно ограничь строку через WHERE id = 3.", "UPDATE меняет выбранную строку, а WHERE защищает остальные."),
        ("Скидка остатков", "Увеличь quantity на 5 у всех позиций, где quantity меньше 5.", "UPDATE inventory SET quantity = quantity + 5 WHERE quantity < 5", "В SET можно использовать прежнее значение.", "Условие quantity < 5 помести в WHERE.", "UPDATE поддерживает вычисления на основе текущих значений."),
        ("Удаление пустого", "Удали из inventory строки с quantity = 0.", "DELETE FROM inventory WHERE quantity = 0", "Нужен DELETE FROM.", "Укажи WHERE quantity = 0.", "DELETE удаляет только строки, прошедшие условие."),
        ("Смена статуса · финал", "Установи status='empty' для всех позиций с quantity = 0.", "UPDATE inventory SET status = 'empty' WHERE quantity = 0", "Используй UPDATE inventory.", "Ограничь изменение условием по quantity.", "UPDATE помогает синхронизировать статус с остатком."),
    ]),
    dict(title="Структура таблиц", topic="CREATE TABLE · PRIMARY KEY · NOT NULL · DEFAULT", theory="CREATE TABLE описывает столбцы и ограничения. PRIMARY KEY идентифицирует строку, NOT NULL требует значение, DEFAULT задаёт значение по умолчанию. Каждое задание создаёт таблицу заново в отдельной памяти.", example="CREATE TABLE sandbox_table (id INTEGER PRIMARY KEY, name TEXT);", tasks=[
        ("Первая таблица", "Создай sandbox_table со столбцами id INTEGER PRIMARY KEY и name TEXT.", "CREATE TABLE sandbox_table(id INTEGER PRIMARY KEY, name TEXT)", "Начни с CREATE TABLE sandbox_table.", "Описание столбцов помести в круглые скобки.", "CREATE TABLE определяет структуру новой таблицы."),
        ("Обязательное имя", "Создай sandbox_table: id INTEGER PRIMARY KEY, name TEXT NOT NULL.", "CREATE TABLE sandbox_table(id INTEGER PRIMARY KEY, name TEXT NOT NULL)", "Добавь NOT NULL после TEXT.", "Ограничение относится только к name.", "NOT NULL запрещает отсутствие имени в новых строках."),
        ("Остаток по умолчанию", "Создай sandbox_table: id INTEGER PRIMARY KEY, quantity INTEGER NOT NULL DEFAULT 0.", "CREATE TABLE sandbox_table(id INTEGER PRIMARY KEY, quantity INTEGER NOT NULL DEFAULT 0)", "После типа quantity добавь NOT NULL.", "Для начального значения используй DEFAULT 0.", "DEFAULT заполняет столбец, если значение не передано."),
        ("Составной ключ", "Создай sandbox_table со столбцами order_id INTEGER, product_id INTEGER и составным PRIMARY KEY(order_id, product_id).", "CREATE TABLE sandbox_table(order_id INTEGER, product_id INTEGER, PRIMARY KEY(order_id, product_id))", "Ключ задаётся после обоих столбцов.", "Используй PRIMARY KEY(order_id, product_id).", "Составной ключ идентифицирует строку парой значений."),
        ("Несколько типов", "Создай sandbox_table: id INTEGER PRIMARY KEY, price REAL, category TEXT.", "CREATE TABLE sandbox_table(id INTEGER PRIMARY KEY, price REAL, category TEXT)", "Выбери тип REAL для price.", "Укажи три столбца через запятую.", "Схема задаёт тип каждого столбца."),
        ("Статус по умолчанию · финал", "Создай sandbox_table: id INTEGER PRIMARY KEY, status TEXT NOT NULL DEFAULT 'new', created_at TEXT.", "CREATE TABLE sandbox_table(id INTEGER PRIMARY KEY, status TEXT NOT NULL DEFAULT 'new', created_at TEXT)", "Столбец status обязателен.", "Для него задай DEFAULT 'new'.", "Сочетание NOT NULL и DEFAULT гарантирует непустой исходный статус."),
    ], required="CREATE"),
    dict(title="Аналитические задачи", topic="Несколько таблиц · CTE · окна", theory="В реальной работе запросы связывают таблицы, агрегируют данные и сравнивают результат между группами. Сначала определяй зерно результата: одна строка на заказ, пользователя или категорию.", example="SELECT u.name, SUM(o.total) AS revenue\nFROM users u JOIN orders o ON u.id=o.user_id\nGROUP BY u.id;", tasks=[
        ("Выручка по покупателю", "Покажи name и revenue — сумму заказов каждого покупателя с заказами.", "SELECT u.name, SUM(o.total) AS revenue FROM users u JOIN orders o ON u.id=o.user_id GROUP BY u.id", "Свяжи users с orders.", "Группируй по пользователю и суммируй total.", "Одна строка результата соответствует покупателю."),
        ("Все покупатели и выручка", "Покажи name и revenue для всех пользователей; без заказов revenue должен быть 0.", "SELECT u.name, COALESCE(SUM(o.total),0) AS revenue FROM users u LEFT JOIN orders o ON u.id=o.user_id GROUP BY u.id", "Используй LEFT JOIN.", "Подставь 0 через COALESCE(SUM(...),0).", "LEFT JOIN сохраняет всех пользователей, COALESCE заменяет отсутствующую сумму."),
        ("Категория заказанного товара", "Покажи order_id и category для каждого товара в заказах.", "SELECT oi.order_id, p.category FROM order_items oi JOIN products p ON oi.product_id=p.id", "Начни с order_items.", "Свяжи её с products по product_id.", "JOIN добавляет категорию товара к каждой позиции заказа."),
        ("Доля дорогих товаров", "Покажи category и expensive_count — число товаров дороже 1000 в каждой категории.", "SELECT category, SUM(CASE WHEN price > 1000 THEN 1 ELSE 0 END) AS expensive_count FROM products GROUP BY category", "Группируй по category.", "Для условного подсчёта используй SUM(CASE ...).", "Условная агрегация считает только дорогие товары внутри каждой категории."),
        ("Последний заказ", "Покажи user_id и last_order — дату последнего заказа каждого покупателя.", "SELECT user_id, MAX(date(created_at)) AS last_order FROM orders GROUP BY user_id", "Группируй по user_id.", "Последнюю дату найдёт MAX(date(created_at)).", "MAX выбирает самую позднюю дату внутри группы."),
        ("Топ по выручке · финал", "Покажи name и revenue покупателей с заказами по убыванию выручки.", "SELECT u.name, SUM(o.total) AS revenue FROM users u JOIN orders o ON u.id=o.user_id GROUP BY u.id ORDER BY revenue DESC", "Сначала посчитай выручку по пользователю.", "Отсортируй итог по revenue DESC.", "Итоговый запрос объединяет JOIN, GROUP BY, SUM и ORDER BY."),
    ]),
]


def enrich_course(levels):
    for level, rows in zip(levels, EXTRA):
        final = level["tasks"].pop()
        # Existing users keep their original exercise IDs and progress.
        level["tasks"].append((final[0].replace(" · финал", ""),) + final[1:])
        level["tasks"].extend(exercise(row) for row in rows)
        last = level["tasks"][-1]
        level["tasks"][-1] = (last[0] + " · финал",) + last[1:]
    for level in ADVANCED:
        mode = "write" if level["title"] == "Изменение данных" else "schema" if level["title"] == "Структура таблиц" else "read"
        target = "inventory" if mode == "write" else "sandbox_table" if mode == "schema" else None
        level["tasks"] = [exercise(row, mode, target, required=(row[2].split()[0] if mode in ("write", "schema") else None)) for row in level["tasks"]]
        levels.append(level)
