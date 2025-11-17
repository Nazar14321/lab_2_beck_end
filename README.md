Група ІО-32

Lab4 

Доброго дня, для запуску проекту локально необхідно:

1)Склонувати проект.(git clone ,cd дерикторія проекту)

2)Зібрати та засіяти базу данних за допомогою докера  docker compose up --build.

3)Відкрити в браузері http://127.0.0.1:6060/ та http://127.0.0.1:6060/healthcheck для перевірки роботи.

Ендпоінти 

GET /                                      (не захищено)

GET /healthcheck ;                         (не захищено)

POST /login ;                              (не захищено)

POST /user ;                               (не захищено)

GET /users ;                               (захищено)

GET/DELETE /user/{id};                     (захищено)

POST /category ;                           (захищено)  

GET /category?user_id= ;                   (захищено)  

DELETE /category ;                         (захищено)  

POST /record ;                             (захищено)  

GET /record?user_id=&category_id=          (захищено)  

GET /record/{id}                           (захищено)  

GET /DELETE /record/{id}                   (захищено)  

