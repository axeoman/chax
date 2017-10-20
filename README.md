# Задание

Разработать бэкенд чата с поддержкой регистрации пользователей.

Функционал:
* Регистрация пользователей.
* Авторизация по логину и паролю, метод авторизации должен возвращать токен авторизации.
* Клиенты подключаются к чату с авторизационным токеном, при подключении должна происходить 
проверка валидности токена. 
* Получение списка активных пользователей.
* Протокол взаимодействия клиента и сервера, должен поддерживать отправку сообщения всем и 
конкретному пользователю.

Приложение запаковать в docker контейнер.

# API

### REST
#### Регистрация

* POST /register/: 
```
{
"username" : "axeoman",
"password" : "123j1kh21",
"Full Name": "Atavin Alexey"
}
```
* 200 OK
```
{
"code": 0, 
"note": Success"
}
```
#### Авторизация
* POST /auth/  
```
{
"username" : "axeoman",
"password" : "123j1kh21",
}
```
* 200 OK 
```
{
"code": 0, 
"note": Success", 
"token": "asda12321321dq1221"
}
```
### WebSocket
#### Подключение

* Request:  
```
{
"action": "login"
"token" : "asda12321321dq1221",
 }
```
* Response: 
```
{
"code": 0, 
"note": "Success"
}
 ```
#### Список пользователей

* Request:  
```
{
"action": "get_user_list"
}
```
* Response: 
 ```
{
"users": []
}
```
#### Отправка сообщения

* Request:  
```
{
"action": "broadcast",
"message": "Привет Всем!"
}  
```
or
```
{
"action": "unicast",
"user" : "Andrey777",
"message": "Привет Андрей!"
}
```

* Response:  
```
{
"code": 0, 
"note": "Success"
}
```