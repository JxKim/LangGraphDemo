from langgraph.graph import StateGraph
from typing import TypedDict
from langgraph.types import interrupt,Command
from langgraph.checkpoint.memory import InMemorySaver
class MyAgentState(TypedDict):
    query: str
    llm_message: str
    rag_message: str

def node_before_rag(state:MyAgentState):
    print("正在调用node_before_rag")
    query = state["query"]
    return {"query":query}



def rag_node(state:MyAgentState):
    print("正在调用rag_node")
    query = state["query"]
    # 注意：interrupt节点在后续恢复执行时，会从头开始重复执行，所以以下操作，也会重复执行，可能会产生脏数据等影响
    # 调用别人接口：
    # 往数据库插数据，更新数据：
    # 写文件：

    # 解决方案：
        # 1、在interrupt前面，不要有这些处理操作，可以在包含interrupt的节点的前面，单独封装成一个节点
        # 2、如果确实需要在interrupt前面有这些操作，保证多次操作，只带来一次影响，保证幂等性
    rag_message = ""
    try:
        # interrupt当中的数据，会被checkpoint保存起来，所以传递数据时，尽量传递基本数据类型的数据，
        user_review_result = interrupt(
            {
                "query":query,
                "msg":"请确认是否进行知识库的查询",
            }
        )

        # user_review_result：类型，也是不限制的，后面调用Command时，传递的是什么，这里就接收什么

        if user_review_result:
            # 知识库查询
            rag_message = "知识库查询结果"
        else:
            # 不查询知识库
            rag_message = "用户不允许查询知识库"
    except Exception as e:
        print("抓住异常，做相关处理")
    
    return {"rag_message":rag_message}

builder = StateGraph(MyAgentState)
builder.add_node(node_before_rag)
builder.add_node(rag_node)
builder.add_edge("__start__","node_before_rag")
builder.add_edge("node_before_rag","rag_node")

checkpointer = InMemorySaver()
# 使用interrupt，需要给graph，配置一个checkpoint
graph = builder.compile(checkpointer=checkpointer)

res = graph.invoke({"query":"什么是langgraph"},config={"configurable":{"thread_id":"1"}})
print(res)

# 解析当前的状态，获取到interrupt中断位置处的数据，做审核
to_review_data = res["__interrupt__"][0].value

# 审核通过，继续执行
res = graph.invoke(Command(resume=True),config={"configurable":{"thread_id":"1"}})
print(res)
