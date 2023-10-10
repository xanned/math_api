import asyncio
import datetime
import random
import uuid

from fastapi import FastAPI
from pydantic import BaseModel
from starlette import status
from starlette.responses import Response
from tortoise.contrib.fastapi import register_tortoise

from models import TaskDb

ACCEPTED_OPERATORS = '+-/*'
app = FastAPI()


class Data(BaseModel):
    x: int
    y: int
    operator: str


@app.post("/calculate", status_code=201)
async def calculate(data: Data, response: Response):
    uuid_id = uuid.uuid4()
    x = data.x
    y = data.y
    operator = data.operator
    if len(operator) > 1 or operator not in ACCEPTED_OPERATORS:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"detail": 'invalid operator'}
    if y == 0 and operator == "/":
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"detail": 'invalid data (divide by zero)'}
    task_id = await TaskDb.create(uuid=uuid_id, status='in progress')
    asyncio.ensure_future(start_task(x, y, operator, task_id.id))

    return {"id": task_id.id}


@app.get("/getresult", status_code=200)
async def getresult(task_id: int, response: Response):
    result = await TaskDb.get_or_none(id=task_id)
    if not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "id not found"}
    if result.status == 'in progress':
        return {"await": "task in progress"}
    return {"result": result.result}


@app.get("/task")
async def gettask():
    tasks = [task async for task in TaskDb.all()]
    return {"tasks": tasks}


async def start_task(x: int, y: int, operator: str, task_id: int):
    await asyncio.sleep(random.choice(range(1, 2)))
    result = eval(f'{x}{operator}{y}')
    await TaskDb.filter(id=task_id).update(result=result, status='Done', finished_at=datetime.datetime.now())


register_tortoise(
    app,
    db_url="sqlite://:memory:",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
