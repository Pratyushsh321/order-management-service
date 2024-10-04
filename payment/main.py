import redis # type: ignore
from fastapi import FastAPI,BackgroundTasks, Request  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from redis_om import HashModel, get_redis_connection  # type: ignore
import requests  # type: ignore
import time  # type: ignore

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Redis database connection
redis= get_redis_connection(  # noqa: F811
    host='127.0.0.1',
    port=6379,
    db=0,
    decode_responses=True  # Automatically decode the Redis responses
)

# Order model
class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # pending, completed, refunded

    class Meta:
        database = redis

# Create an order
@app.post('/orders')
async def create_order(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    #we are sending a request to inventory microservice
    req=requests.get('http://localhost:8000/products/%s'%body['id'])

    product=req.json()

    # Calculate order details
    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2 * product['price'],  # Fixed fee (20% of price)
        total=1.2 * product['price'],  # Total (price + fee)
        quantity=body['quantity'],
        status='pending'
    )

    order.save()

    # Run background task to simulate order completion
    background_tasks.add_task(order_completed, order)

    return order

# Background task to complete the order after 5 seconds
def order_completed(order: Order):
    time.sleep(5)  # Simulate processing time
    order.status = 'completed'
    order.save()
    redis.xadd('complete_order',order.dict(),'*')

@app.get('/orders/{order_id}')
def get_order_status(order_id: str):
    order = Order.get(order_id)  # Fetch the order by ID
    return {"status": order.status}