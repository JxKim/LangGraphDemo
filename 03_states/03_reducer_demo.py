from typing import TypedDict,Annotated,List
from langgraph.graph import StateGraph
from langgraph.constants import START,END
from operator import add
from langchain.agents import create_agent,AgentState


# 1、定义状态
class MyAgentState(TypedDict):

    # query,rag_search等状态，没有定义Reducer函数，是会使用一个默认的Reducer函数：覆盖函数
    # overide(new_value,old_value) -> new_value
    query:str
    rag_search:str
    web_search:str
    llm_answer:str
    # operator.add: 接收两个值，返回一个结果 operator.add(2,3)=5 operator.add(['key1'],['key2'])=['key1','key2']
    # operator.add(a,b)  = a+b -> 要想使用operator.add, a和b的Class必须要实现__add__方法

    # 这个add函数，在langgraph里面，就称之为Reducer函数
    test_key:Annotated[List[str],add]


# 2、定义节点
def rag_node(state:MyAgentState):

    # 1、从state中获取query
    query = state["query"]

    # 2、模拟rag检索
    rag_search = f"根据用户的问题{query}，从知识库中检索到的想关内容"

    # 3、将rag_search写入到状态当中
    return {"rag_search":rag_search,"test_key":["test_key_rag_value"],'llm_answer':"testxxx"}

def web_search_node(state:MyAgentState):

    # 1、从state中获取query
    query = state["query"]

    # 2、模拟web搜索
    web_search = f"根据用户的问题{query}，从互联网中检索到的想关内容"

    # # 不能直接对state进行状态赋值，然后直接return state
    # state["web_search"] = web_search
    # return state

    # 3、将web_search写入到状态当中
    return {"web_search":web_search,"test_key":["test_key_web_value"]}


def llm_node(state:MyAgentState):

    # 1、从state中读取rag_search和web_search
    rag_search = state["rag_search"]
    web_search = state["web_search"]
    query = state["query"]
    # 2、模拟llM调用，基于两路检索，生成最终的答案
    
    llm_answer = f"根据用户的问题{query}，以及rag_search{rag_search}和web_search{web_search}，llm生成的最终答案"

    return {"llm_answer":llm_answer}

# 3、构建builder，将节点和边添加到builder中，
builder = StateGraph(state_schema = MyAgentState)
# 3.1 添加节点
builder.add_node(rag_node) # add_node底层会将节点名称设置为函数名
builder.add_node(web_search_node)
builder.add_node(llm_node)

# 3.2 添加边
builder.add_edge(START,'rag_node') # 此处添加边时，需要传入节点名称
builder.add_edge(START,'web_search_node')
builder.add_edge('rag_node','llm_node')
builder.add_edge('web_search_node','llm_node')

# 最后END节点的连接可选
builder.add_edge('llm_node',END)

# 4、编译图
graph = builder.compile()

# 5、调用图: 使用invoke，因为graph的class实现了langchain当中的Runnable接口
res = graph.invoke({"query":"什么是langgraph"}) # 得到的res，就是状态的最终结果
print(res)
