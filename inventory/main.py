import redis  # type: ignore
from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from redis_om import HashModel, get_redis_connection  # type: ignore
from pydantic import BaseModel # type: ignore

app = FastAPI()

# hello from remote

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a Redis connection using get_redis_connection
redis= get_redis_connection(  # noqa: F811
    host="127.0.0.1",
    port=6379,
    decode_responses=True  # Automatically decode the Redis responses
)

# Pydantic model for Product creation and updates
class ProductSchema(BaseModel):
    name: str
    price: float
    quantity: int

# Redis-OM model for Product
class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

# Get all products
@app.get("/products")
async def get_all_products():
    product_keys = Product.all_pks()
    return [format_product(pk) for pk in product_keys]

# Create a new product
@app.post("/products", response_model=ProductSchema)
async def create_product(product: ProductSchema):
    product_instance = Product(**product.dict())
    product_instance.save()
    return product_instance

# Get a product by its primary key (pk)
@app.get("/products/{pk}", response_model=ProductSchema)
async def get_product(pk: str):
    try:
        product = Product.get(pk)
        return product
    except KeyError:
        raise HTTPException(status_code=404, detail="Product not found")

# Update a product by its primary key (pk)
@app.put("/products/{pk}", response_model=ProductSchema)
async def update_product(pk: str, updated_product: ProductSchema):
    try:
        product = Product.get(pk)
        product.name = updated_product.name
        product.price = updated_product.price
        product.quantity = updated_product.quantity
        product.save()
        return product
    except KeyError:
        raise HTTPException(status_code=404, detail="Product not found")

# Delete a product by its primary key (pk)
@app.delete("/products/{pk}")
async def delete_product(pk: str):
    try:
        Product.delete(pk)
        return {"message": "Product deleted successfully"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Product not found")

# Helper function to format product output
def format_product(pk: str):
    product = Product.get(pk)
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity,
    }

@app.get("/")
async def root():
    return {"message": "Product CRUD API"}
