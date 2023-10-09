import asyncio
import datetime
import random
import uuid

from fastapi import FastAPI
from pydantic import BaseModel
from tortoise.contrib.fastapi import register_tortoise

from models import Task

app = FastAPI()


class Data(BaseModel):
    x: int
    y: int
    operator: str


@app.post("/calculate")
async def calculate(data: Data):
    uuid_id = uuid.uuid4()
    x = data.x
    y = data.y
    operator = data.operator
    if len(operator) > 1 or operator not in '+-/*':
        return {"detail": 'invalid operator'}
    if y == 0 and operator == "/":
        return {"detail": 'invalid data (divide by zero)'}
    asyncio.ensure_future(start_task(x, y, operator, uuid_id))
    user_obj = await Task.create(id=uuid_id, status='in progress')
    return {"id": uuid_id}


@app.get("/getresult")
async def getresult(uuid_id: str):
    result = await Task.get_or_none(id=uuid_id)
    return {"result": result}


@app.get("/gettask")
async def gettask():
    tasks = []
    async for task in Task.all():
        tasks.append(task)
    return {"tasks": tasks}


async def start_task(x: int, y: int, operator: str, uuid_id: uuid):
    await asyncio.sleep(random.choice(range(1, 16)))
    result = eval(f'{x}{operator}{y}')
    await Task.filter(id=uuid_id).update(result=result, status='Done', finished_at=datetime.datetime.now())


register_tortoise(
    app,
    db_url="sqlite://:memory:",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
