"""
写一个create_agent函数：接收tools,middleware_list,system_prompt等参数。使用langgraph去构建一个图
"""
from langchain_openai import ChatOpenAI
from typing import TypedDict,Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage,AnyMessage
from operator import add
from langgraph.graph import StateGraph
from tool_node import ToolNode
from langgraph.checkpoint.base import BaseCheckpointSaver
def create_agent(
        model:ChatOpenAI,
        tools:list,
        system_prompt:str,
        middleware_list:list,
        checkpointer:BaseCheckpointSaver,
):
    # 1、定义状态
    class MyAgentState(TypedDict):
        messages:Annotated[list[AnyMessage],add]

    model = model.bind_tools(tools)
    def model_node(state:MyAgentState):
        messages = state["messages"]
        ai_message = model.invoke(messages)
        return {"messages":[ai_message]} # 因为reducer使用的是add，所以这里返回的是一个list
    
    tool_node = ToolNode(tools=tools)

    def _merge_middleware_update(update:dict,mw_update_state:dict):
        if mw_update_state is None:
            return
        for k, v in mw_update_state.items():
            if k not in update:
                update[k] = v
            else:
                update[k] += v

    if middleware_list:
        def before_agent_node(state:MyAgentState):
            update:dict = {}
            for mw in middleware_list:
                # 每一个中间件，都会产出增量状态变更，我们需要合并这些变更
                mw_update_state = mw.before_agent(state)
                # 合并中间件的变更的方法
                _merge_middleware_update(update,mw_update_state)
            return update
        
        def before_model_node(state:MyAgentState):
            update:dict = {}
            for mw in middleware_list:
                # 每一个中间件，都会产出增量状态变更，我们需要合并这些变更
                mw_update_state = mw.before_model(state)
                # 合并中间件的变更的方法
                _merge_middleware_update(update,mw_update_state)
            return update
    
    def conditional_edge_func(state:MyAgentState):
        messages = state["messages"]
        if messages and type(messages[-1]) == AIMessage and messages[-1].tool_calls:
            return "tool_node"
        else:
            return "__end__"
    
    # 添加节点和边的操作
    builder = StateGraph(MyAgentState)
    builder.add_node(model_node)
    builder.add_node("tool_node",tool_node)
    if middleware_list:
        builder.add_node(before_agent_node)
        builder.add_node(before_model_node)
        builder.add_edge("__start__","before_agent_node")
        builder.add_edge("before_agent_node","before_model_node")
        builder.add_edge("before_model_node","model_node")
        builder.add_conditional_edges("model_node",conditional_edge_func)
        builder.add_edge("tool_node","before_model_node")
    else:
        builder.add_edge("__start__","model_node")
        builder.add_conditional_edges("model_node",conditional_edge_func)
        builder.add_edge("tool_node","model_node")
    
    graph = builder.compile(
        checkpointer=checkpointer,
    )

    return graph


    
    
if __name__ == "__main__":
    llm = ChatOpenAI(model="gpt-4o-mini")
    from langchain_core.tools import tool
    from middleware import CurrentDateMiddleware
    from langgraph.checkpoint.memory import InMemorySaver
    middleware_list = [CurrentDateMiddleware()]
    @tool
    def get_weather(city:str):
        """获取城市的天气"""
        return f"{city}的天气是晴朗的"

    agent = create_agent(model=llm,tools=[get_weather],
                         system_prompt="你是一个天气助手",
                         middleware_list=middleware_list,
                         checkpointer=InMemorySaver(),
                         )
    
    res = agent.invoke({"messages":[HumanMessage(content="北京的天气")]},config={"configurable":{"thread_id":"1"}})
    print(res)



    