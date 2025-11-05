Група ІО-32

Варіант 2

Для користувацьких категорій витрат - повинні бути загальні
категорії витрат, які видно всім користувачам, та користувацькі, які
можуть вказати тільки користувачі, які їх визначили.(відповідно до варіанту були модифіковані POST /category, GET /category,DELETE /category (body: {"id": <int>}),GET /record/)

Доброго дня, для запуску проекту локально необхідно:

1)Склонувати проект.(git clone ,cd дерикторія проекту)

2)Зібрати та засіяти базу данних за допомогою докера  docker compose up --build.

3)Зібрати та запустити докер (docker compose up -d --build).

4)Відкрити в браузері http://127.0.0.1:6060/ та http://127.0.0.1:6060/healthcheck для перевірки роботи.

Ендпоінти 

GET /

GET /healthcheck ;

POST /user ;

GET /users ;

GET/DELETE /user/{id};

POST /category ;

GET /category ;

DELETE /category (body: {"id": <int>})

POST /record ;

GET /record?user_id=&category_id= 

GET /record/{id}

GET/DELETE /record/{id}


Або також можна відвідати вже розгорнутий варіант:

 https://lab-2-beck-end-2.onrender.com
