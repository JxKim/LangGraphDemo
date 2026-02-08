from typing import TypedDict,Annotated,List
from langchain.messages import AnyMessage,AIMessage,ToolMessage,HumanMessage
from langgraph.constants import START
# 自定义Reducer函数：my_add_message_reducer


def my_add_message_reducer(message_list_left:List[AnyMessage],message_list_right:List[AnyMessage])->List[AnyMessage]:
    """
    将节点产出的消息列表和全局的消息列表做一个合并，再返回一个合并后的结果，作为新的全局消息列表
    """
    print("my_add_message_reducer函数的调用：")
    print("message_list_left:",message_list_left)
    print("message_list_right:",message_list_right)

    new_message_list = message_list_left + message_list_right

    return new_message_list

def mock_llm_invoke(message_list:List[AnyMessage])->AIMessage:
    print("正在调用llm_invoke")
    return AIMessage(content="xxxx")

def mock_tool_invoke(message:AIMessage)->ToolMessage:
    print("正在调用tool_invoke")
    return ToolMessage(content="xxxx",tool_call_id='xx') # 构造ToolMessage时，必须传入tool_call_id

class MyAgentState(TypedDict):

    messages:Annotated[List[AnyMessage],my_add_message_reducer]


def llm_node(state:MyAgentState):

    message_list = state["messages"]

    # 模拟调用llm.invoke,传入当前的整个消息列表
    ai_message = mock_llm_invoke(message_list=message_list)

    # 将结果输出，让自定义的Reducer函数，将这个增量的结果和当前的全局消息列表做一个合并

    return {"messages":[ai_message]}

def tool_node(state:MyAgentState):
    message_list = state["messages"]

    last_ai_message = message_list[-1]

    tool_message = mock_tool_invoke(last_ai_message)
    return {"messages":[tool_message]}


from langgraph.graph import StateGraph

builder = StateGraph(MyAgentState)

builder.add_node(llm_node)
builder.add_node(tool_node)

builder.add_edge(START,'llm_node')
# 此处只是演示reducer，所以直接把llm_node和tool_node连接起来，但是实际在langchain的create_agent里面的结构不是这样的 
builder.add_edge('llm_node','tool_node')

graph = builder.compile()

res = graph.invoke({"messages":[HumanMessage(content = "你好")]})
print(res)