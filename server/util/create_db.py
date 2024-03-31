from server.db_manager import db
from server.model.todo_item import TodoItem


def init_db_table():
    print("初始化表结构")
    db.set_allow_sync(True)
    db.create_tables([
        TodoItem
    ])


if __name__ == '__main__':
    init_db_table()
