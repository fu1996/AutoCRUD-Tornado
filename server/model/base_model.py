from peewee import Model, datetime, DateTimeField, IntegerField
from pydantic import BaseModel, Field
from server.db_manager import db


class BasePydanticModel(BaseModel):
    id: int
    created_at: datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime = Field(default_factory=datetime.datetime.now)
    is_deleted: int = Field(default=0)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }


class BaseDBModel(Model):
    created_at = DateTimeField(default=datetime.datetime.now, formats="%Y-%m-%d %H:%M:%S", verbose_name="创建时间")
    updated_at = DateTimeField(default=datetime.datetime.now, formats="%Y-%m-%d %H:%M:%S", verbose_name="更新时间")
    # 软删除字段，默认为0
    is_deleted = IntegerField(default=0)

    class Meta:
        database = db  # 设置数据库连接

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"

    @classmethod
    def update(cls, *args, **kwargs):
        final_kwargs = {
            **kwargs,
            "updated_at": datetime.datetime.now()
        }
        return super().update(*args, **final_kwargs)

    @classmethod
    def soft_delete(cls):
        final_kwargs = {
            "is_deleted": 1
        }
        return super().update(**final_kwargs)
