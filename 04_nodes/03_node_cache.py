from typing import TypedDict

class MyState(TypedDict):

    user_id:str
    order_id:str

def mock_get_order_id(user_id):

    import time

    time.sleep(5)

    return f"order_id_12312_{user_id}"

def get_order_id(state:MyState):
    print("调用了get_order_id节点")
    user_id = state["user_id"]
    order_id = mock_get_order_id(user_id=user_id)

    return {"order_id":order_id}

from langgraph.graph import StateGraph

builder = StateGraph(MyState)

# 想让哪个节点后面在调用的时候走缓存，就需要在add_node时，传入CachePolicy
# CachePolicy有两个属性，第一个属性是key_func，表示如何从节点的input来生成cache key，后面cache key相同的节点输入，就会走缓存
#
from langgraph.types import CachePolicy
builder.add_node(get_order_id,cache_policy=CachePolicy(ttl=3))
# __start__ 其实就是langgraph.constant.START
builder.add_edge("__start__","get_order_id")

# 引入一个cacher，用来去保存缓存数据
from langgraph.cache.memory import InMemoryCache
cacher = InMemoryCache()
# 在compile时，传入cacher
graph = builder.compile(cache=cacher) # 传入cache 保证了graph拥有缓存的能力

print("这是第一次调用")
res = graph.invoke({"user_id":"123"})
print(res)
print("="*50)

print("这是第二次调用")
res = graph.invoke({"user_id":"123"})
print(res)
print("="*50)
import time
time.sleep(5)

print("这是第三次调用")
res = graph.invoke({"user_id":"123"})
print(res)
print("="*50)



