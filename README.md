Доброго дня, для запуску проекту локально необхідно:

1)Склонувати проект.(git clone )

2)Зібрати та запустити за допомогою докера(docker compose up --build) .

3)Відкрити в браузері http://127.0.0.1:6060/ та http://127.0.0.1:6060/health для перевірки роботи.

Ендпоінти 

GET /health;

POST /user ;

GET /users ;

GET/DELETE /user/{id};

POST /category ;

GET /category ;

DELETE /category (body: {"id": <int>})

POST /record ;

GET /record?user_id=&category_id= 

GET/DELETE /record/{id}


Або також можна відвідати вже розгорнутий варіант:

https://lab-2-beck-end.onrender.com/
