from main import redis,Product
import time

key ='order_completed'
group='inventory-group'

try:
  redis.xgroup_create(key,group) # type: ignore  # noqa: F821

except:  # noqa: E722
  print('Group already exist !')

while True:
  try:
    results=redis.xreadgroup(group,key,{key:'>'},None) # type: ignore  # noqa: F821

    if results!=[]:
      for result in results:
        obj=result[1][0][1]
        product=Product.get(obj['product_id'])
        print(product)
        product.quantity=product.quantity - int(obj['quantity'])
        product.save()
  except Exception as e:
    print(str(e))
  time.sleep(1)