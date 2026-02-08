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
    # raise Exception("模拟node_2节点报错了")
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

# 尝试调用graph对象
# res = graph.invoke({},config={"configurable":{"thread_id":"2"}})
# print(res)

# 从状态当中恢复执行
# 传入一个None，表示从状态中恢复继续往下执行，
# 如果传入是一个字典：会从图的START节点开始执行
res =graph.invoke(None,config={"configurable":{"thread_id":"3"}})
print(res)
