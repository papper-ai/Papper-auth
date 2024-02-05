# Сетап API для разработки
1. В api/auth нужно бросить certs (сертификаты, лежит в ТГ)
2. В корневой папке создать файл .env
3. Заполнить .env:
```env
DB_ASYNC_DRIVER=asyncpg
DB_DIALECT=postgresql
DB_HOST=db
DB_NAME=papperbd_test
DB_PASSWORD=123
DB_PORT=5432
DB_USER=postgres

DB_CONTAINER_PORT=5454

MAILGUN_API_KEY=_ # Ключ в ТГ чате

DOMAIN=localhost
HOST_PORT=7654
```
4. Запустить через ```docker compose up --build```
5. Доступен по адресу http://localhost:${HOST_PORT}/docs
6. Подключение к БД с той же машины с хостом localhost и портом DB_CONTAINER_PORT
