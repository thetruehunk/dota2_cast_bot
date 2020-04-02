#infobot_dota2
https://liquipedia.net/dota2/api.php?action=parse&format=json&page=Major_Tournaments%27

<h2>Создание БД</h2>
Запускаем python
делаем импорт
from data_model import *
вызываем metadata.create_all(engine)

https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#module-sqlalchemy.dialects.sqlite.pysqlite
https://ru.wikibooks.org/wiki/SQLAlchemy
sqlite:///:memory: (or, sqlite://)
sqlite:///relative/path/to/file.db
sqlite:////absolute/path/to/file.db