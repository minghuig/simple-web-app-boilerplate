from peewee import *
from datetime import datetime
from database import BaseModel

class User(BaseModel):
    id = AutoField(primary_key=True)
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=100, unique=True)
    created_at = DateTimeField(default=datetime.now)
    is_active = BooleanField(default=True)

    class Meta:
        table_name = 'users'

class Task(BaseModel):
    id = AutoField(primary_key=True)
    title = CharField(max_length=200)
    description = TextField(null=True)
    completed = BooleanField(default=False)
    user = ForeignKeyField(User, backref='tasks', on_delete='CASCADE')
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'tasks'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)