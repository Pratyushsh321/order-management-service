from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from redis_om import get_redis_connection,HashModel
from starlette.requests import Request

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)


#redis connection

class Order(HashModel):
  product_id:str
  price:int
  fee:float
  total:float
  quantity:int
  status:str #pending,completed,refunded
  #to make connection to database
  class Meta:
    database=redis


@app.post('/orders')
async def create(request:Request):
