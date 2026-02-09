"""
演示两个节点并行执行，且对同一个状态键有更改时，更改是无序的
"""

from typing import TypedDict,List,Annotated
from operator import add
from langgraph.graph import StateGraph
from langgraph.constants import START
class MyAgentState(TypedDict):
    messages:Annotated[List[str],add]


def node_1(state:MyAgentState):
    import time
    time.sleep(10)
    return {"messages":["你好,node_1"]}

def node_2(state:MyAgentState):
    import time
    time.sleep(5)
    return {"messages":["你好,node_2"]}

builder = StateGraph(MyAgentState)
builder.add_node(node_2)
builder.add_node(node_1)
builder.add_edge(START,"node_2")
builder.add_edge(START,"node_1")
graph = builder.compile()
res = graph.invoke({"messages":[]})
print(res)

