import time
from typing import TypedDict, Any, List
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
checkpointer = SqliteSaver(conn=sqlite3.connect("customer_support.db",check_same_thread=False))
llm = ChatOpenAI(model="gpt-4o-mini")
class MockLLM:
    def invoke(self, prompt: str):
        return f"AI Generated: Answer for '{prompt}'"

class MockDatabase:
    def get_user_info(self, user_id: str):
        return {"id": user_id, "role": "vip" if "vip" in user_id else "standard"}

class CustomerSupportState(TypedDict):
    query: str          # 用户问题
    response: str       # 客服回复
    log: List[str]      # 处理日志
    llm: MockLLM


# 客服系统当中的用户服务节点：state,config,runtime
def node_customer_service(state: CustomerSupportState, runtime: Runtime, config: RunnableConfig):
    
    print("客服系统当中的用户服务节点")
    print("传入的状态为，",state)
    print("传入的配置为，",config)
    user_id = config["configurable"]["user_id"]
    
    print("当前调用该系统的用户ID为：",user_id)
    print("传入的runtime为，",runtime)
    print("当前调用的运行时内的context对象",runtime.context)

    db = runtime.context["db"]
    llm = runtime.context["llm"]
    print("从runtime对象的context当中获取到数据库的连接对象：",db)
    print("从runtime对象的context当中获取到LLM的连接对象：",llm)
    res = db.get_user_info(user_id)
    print("从数据库当中查询到的用户信息为：",res)

    llm_res = llm.invoke(state["query"])

    print("从LLM当中查询到的回复为：",llm_res)

mock_llm = MockLLM()
builder = StateGraph(CustomerSupportState)
builder.add_node(node_customer_service)
builder.add_edge(START,"node_customer_service")

graph = builder.compile(checkpointer=checkpointer)

# 调用invoke时，可以传递相关的配置信息，和整个图执行过程当中的上下文/运行时数据
config = {"user_id":"vip_123","configurable":{"thread_id":"1234"}}
context= {
    "llm":MockLLM(),
    "db":MockDatabase(),
    
}
res = graph.invoke({"query":"你好","llm":mock_llm},config=config,context=context)
print(res)