from typing import TypedDict,Annotated
from langgraph.graph import StateGraph
from langgraph.types import RetryPolicy
attempt = 0
class MyAgentState(TypedDict):

    llm_message:str


def llm_node(state:MyAgentState):
    """
    用来模拟一个不稳定的一个调用LLM的节点
    """
    global attempt
    attempt += 1
    
    if attempt<3:
        print(f"第{attempt}次调用LLM失败")
        # raise ConnectionError("调用LLM失败")
        raise ValueError("调用LLM失败")
    print("第3次调用LLM成功")
    return {"llm_message":"调用LLM成功"}

builder = StateGraph(MyAgentState)

# RetryPolicy:
    # 1、针对于什么类型的异常去进行一个重试
    # 2、重试的次数，
    # 3、重试的间隔：指数退避策略：1s, 2s, 4s, 8s
builder.add_node(llm_node,retry_policy=RetryPolicy())

builder.add_edge("__start__",'llm_node')

graph = builder.compile()

res = graph.invoke({})
    



    