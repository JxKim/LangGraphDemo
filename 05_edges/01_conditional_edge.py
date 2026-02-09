from langgraph.graph import StateGraph
from typing import TypedDict
from langgraph.constants import END
class MyAgentState(TypedDict):
    query: str
    number:int
    node:str
    rag_message: str

def node_a(state:MyAgentState):

    number = state["number"]

    print("正在执行node_a")

    return {"node":"node_a","number":number}


def node_b(state:MyAgentState):

    number = state["number"]

    print("正在执行node_b")

    return {"node":"node_b","number":number+2}

def condtional_function(state:MyAgentState):
    """
    条件边函数，结合当前状态，判断下一个节点是什么
    """
    number = state["number"]

    if number % 2 == 0:
        return "node_b"
    else:
        return END 

builder = StateGraph(MyAgentState)

builder.add_node(node_a)
builder.add_node(node_b)
builder.add_edge("__start__","node_a")
# 引入条件边
builder.add_conditional_edges(
    source="node_a",
    path=condtional_function
)

graph = builder.compile()

graph.invoke({"number":2})
