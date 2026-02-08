from typing import TypedDict
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langgraph.constants import START
class ResumeDemoState(TypedDict):

    key_1:str
    key_2:str
    key_3:str

def node_1(state:ResumeDemoState):

    print(state)
    print("node_1被调用了")
    return {"key_1":"value_1"}

def node_2(state:ResumeDemoState):

    print("node_2被调用了")
    raise Exception("模拟node_2节点报错了")
    return {"key_2":"value_2"}


def node_3(state:ResumeDemoState):

    print("node_3被调用了")
    return {"key_3":"value_3"}

builder = StateGraph(ResumeDemoState)

builder.add_node(node_1)

builder.add_node(node_2)
builder.add_node(node_3)

builder.add_edge(START,"node_1")
builder.add_edge("node_1","node_2")
builder.add_edge("node_2","node_3")

# 构建一个基于数据库的checkpointer
checkpointer = SqliteSaver(conn=sqlite3.connect("./resume_demo.db",check_same_thread=False))
graph = builder.compile(checkpointer=checkpointer)


# 加一个try catch 块，让node_2报错之后，进程不会退出
try:
    res =graph.invoke({},config={"configurable":{"thread_id":"1"}})
    print(res)
except Exception as e:
    print("执行报错之后，从graph当中获取到的状态信息：")
    state_snapshot = graph.get_state(config={"configurable":{"thread_id":"1"}})
    print(state_snapshot)