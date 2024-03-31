import peewee_async

DB_HOST="127.0.0.1"
DB_PORT=3306
DB_DATABASE="demo"
DB_USERNAME="root"
DB_PASSWORD="mysql_fdMcPm"

# 创建数据库模型类
db = peewee_async.MySQLDatabase(DB_DATABASE, host=DB_HOST,
                                port=DB_PORT, user=DB_USERNAME, password=DB_PASSWORD)
db.set_allow_sync(False)

db_manager = peewee_async.Manager(database=db)
