from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator

class Todo(Model):
    id = fields.IntField(pk=True)
    todo = fields.CharField(max_length=225)
    due_date = fields.CharField(max_length=225)
    class PydanticMeta: 
        pass

Todo_pydantic = pydantic_model_creator(Todo, name="Todo")
TodoIn_pydantic = pydantic_model_creator(Todo, name="TodoIn", exclude_readonly=True)