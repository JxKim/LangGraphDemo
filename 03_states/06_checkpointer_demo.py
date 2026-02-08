"""

"""
from typing import TypedDict,Annotated,List
from operator import add

class MyState(TypedDict):
    aggregates:Annotated[List[str],add]


def node_a(state:MyState):

    return {"aggregates":["a"]}


def node_b(state:MyState):

    return {"aggregates":["b"]}


def node_c(state:MyState):

    return {"aggregates":["c"]}


def node_b_2(state:MyState):

    return {"aggregates":["b_2"]}

def node_d(state:MyState):

    return {"aggregates":["d"]}


from langgraph.graph import StateGraph
from langgraph.constants import START
builder = StateGraph(MyState)

builder.add_node(node_a)
builder.add_node(node_b)
builder.add_node(node_c)
builder.add_node(node_b_2)
builder.add_node(node_d)


builder.add_edge(START,"node_a")
builder.add_edge("node_a","node_b")
builder.add_edge("node_a","node_c")
builder.add_edge("node_b","node_b_2")
builder.add_edge("node_b_2","node_d")
builder.add_edge("node_c","node_d")





graph = builder.compile()

print('graph当中的nodes',graph.nodes)
print('graph当中的通道channels',graph.channels)
# 查看节点a的订阅和写入
print('节点a的订阅：',graph.nodes["node_a"].triggers)
print('节点a的写入',graph.nodes["node_a"].writers)

print("="*50)

# 查看节点d的订阅和写入
print('节点d的订阅：',graph.nodes["node_d"].triggers)
print('节点d的写入',graph.nodes["node_d"].writers)


res = graph.invoke({})
print(res)
# res:["a","b","c", "b_2","d"], ["a","b","b_2","c","d"]
