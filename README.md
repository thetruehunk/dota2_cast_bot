#infobot_dota2
___
<h3>Описание</h3>
Это telegram бот для отслеживания турниров и игр DOTA2<br/>
Основной функционал - получение списка текущих турниров и игр, возможность<br/>
включить уведомления о начале игры и получить ссылку на трансляцию.<br/>

<h4>Создание БД</h4>
При запуске bot.py выполняется подключение к БД<br/>
В случае отсутствия файла - создается новая БД и ее структура<br/>
Выполняется синхронизация актуальны турниров и игр<br/>
Нужно сделать автоматическую синронизацию <br/>
Мы используем данные предоставляемые [liquipedia](https://liquipedia.net)<br/>
Описание API находится на странице [проекта](https://github.com/c00kie17/liquipediapy)<br/>

from data_model import *
вызываем metadata.create_all(engine)

https://liquipedia.net/dota2/api.php?action=parse&format=json&page=Major_Tournaments%27
https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#module-sqlalchemy.dialects.sqlite.pysqlite
https://ru.wikibooks.org/wiki/SQLAlchemy
sqlite:///:memory: (or, sqlite://)
sqlite:///relative/path/to/file.db
sqlite:////absolute/path/to/file.db

https://liquipedia.net/unblock страница с блокировкой