"""

"""
from typing import TypedDict,Annotated,List
from operator import add
from langgraph.checkpoint.memory import InMemorySaver

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

graph = builder.compile(checkpointer=InMemorySaver())


res = graph.invoke({},config={"configurable":{"thread_id":"1"}})

# 1、获取到当前的状态
state = graph.get_state(config={"configurable":{"thread_id":"1"}})
print('当前的状态为：',state)

# 2、获取到历史的所有状态
print('历史的所有状态为：\n')
history_states = graph.get_state_history(config={"configurable":{"thread_id":"1"}})
for state in history_states:
    print(state)
    print("="*50)
