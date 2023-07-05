# Чат на TCP-сокетах

## Примечания:

* Запуск сервера: __`python3 server.py`__
* Запуск клиентского приложения: __`python3 main.py`__
* Для работы требуется python версии не ниже 3.9 ввиду использования
составных type hints.
* Для работы клиентского приложения требуется установленный модуль _tkinter_ для интерпретатора (`sudo apt-get install python3-tk` в debian или `sudo pacman -S tk` в arch)

## Структура:

* Модуль общих для сервера и клиента констант и функций:
	* common.py
* Приложение сервера:
	* server.py
* Приложение клиента:
	* main.py &mdash; точка запуска
	* client.py &mdash; модуль 
	* 
Сервер однопоточный, конкурентность достигается до счёт подхода с использованием сопрограмм (модуль _asyncio_).

Клиентское приложение двухпоточное: основной поток обслуживает жизненный цикл оконного интерфейса, дополнительный поток обслуживает жизненный цикл сетевого соединения в аналогичном серверу ключе (неблокирующие вызовы сопрограмм в одном потоке).

## Примеры работы:

![example_username](https://github.com/alexeycoder/pychat/assets/109767480/18ef98c4-ef9f-4732-8e3b-a2eb087df908)

![example_server](https://github.com/alexeycoder/pychat/assets/109767480/5659afcc-2464-44bb-b8a7-5e920737f177)

![example_chating](https://github.com/alexeycoder/pychat/assets/109767480/191efbdb-4e86-439d-8e37-3060fc11e25b)

![example_no_connection](https://github.com/alexeycoder/pychat/assets/109767480/2d3b0f83-8ab7-43b6-bd87-976ceca2efd6)
