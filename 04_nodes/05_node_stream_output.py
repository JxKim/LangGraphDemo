from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from typing import TypedDict
def stream_mode_messages_demo():
    llm = ChatOpenAI(model="gpt-4o-mini")
    # 单独的ChatModel的实例，要流式输出需要调用： llm.stream()
    class MyAgentState(TypedDict):
        query:str
        llm_message:str

    def llm_node(state:MyAgentState):
        """
        用来调用llm的节点
        """
        query = state["query"]
        # 这里调用ChatModel，虽然是通过invoke方式调用，但是只要调用graph.stream，并且传入stream_mode为messages，此处的调用也能转换成流式调用
        res = llm.invoke(query)

        return {"llm_message":res.content}


    builder = StateGraph(MyAgentState)
    builder.add_node(llm_node)
    builder.add_edge("__start__",'llm_node')
    graph = builder.compile()

    # stream_mode = messages时，会流式输出一个元组，其中的metadata包含llm调用元数据，可以用来去针对不同的场景做过滤处理
    # 例如在包含了多个LLM调用节点图当中，仅对某些LLM做流式输出。
    for ai_message_chunk,metadata in graph.stream({"query":"什么是langgraph"},stream_mode="messages"):
        print(ai_message_chunk.content,end="")

def stream_mode_values_update_demo():

    class MyAgentState(TypedDict):
        query:str
        llm_message:str
        rag_search_result:str

    def llm_node(state:MyAgentState):
        """
        用来调用llm的节点
        """
        query = state["query"]
        # 这里调用ChatModel，虽然是通过invoke方式调用，但是只要调用graph.stream，并且传入stream_mode为messages，此处的调用也能转换成流式调用
        res = "LLM调用的结果"

        return {"llm_message":res}
        # return None
    
    def rag_node(state:MyAgentState):

        query = state["query"]
        rag_search = f"关于{query}RAG搜索的结果"

        return {"rag_search_result":rag_search}
        # return None
    
    builder = StateGraph(MyAgentState)
    builder.add_node(llm_node)
    builder.add_node(rag_node)
    builder.add_edge("__start__",'llm_node')
    builder.add_edge("llm_node","rag_node")
    graph = builder.compile()

    for state in graph.stream({"query":"什么是langgraph"},stream_mode="values"):
        print(state)

    # for state in graph.stream({"query":"什么是langgraph"},stream_mode="updates"):
    #     print(state)

def stream_mode_custom_data_demo():
    """
    可以在节点内部，将某些函数，方法所产出的数据，传递到节点外部去： 
    """
    from langgraph.runtime import Runtime
    class MyAgentState(TypedDict):
        query:str
        llm_message:str
        rag_search_result:str

    def llm_node(state:MyAgentState,runtime:Runtime):
        """
        用来调用llm的节点
        """
        stream_writer = runtime.stream_writer
        # 通过stream_writer，可以将自定义数据传递到节点外部去
        stream_writer({"event":"llm_call_start"})
        query = state["query"]
        # 这里调用ChatModel，虽然是通过invoke方式调用，但是只要调用graph.stream，并且传入stream_mode为messages，此处的调用也能转换成流式调用
        res = "LLM调用的结果"
        stream_writer({"event":"llm_call_end"})
        return {"llm_message":res}
        # return None
    
    def rag_node(state:MyAgentState):

        query = state["query"]
        rag_search = f"关于{query}RAG搜索的结果"

        return {"rag_search_result":rag_search}
        # return None
    
    builder = StateGraph(MyAgentState)
    builder.add_node(llm_node)
    builder.add_node(rag_node)
    builder.add_edge("__start__",'llm_node')
    builder.add_edge("llm_node","rag_node")
    graph = builder.compile()

    for custom_event in graph.stream({"query":"什么是langgraph"},stream_mode="custom"):
        print(custom_event)
        # 可以在节点外部，定义一个函数，用来处理节点内部传递过来的自定义数据
        #handler_event(custom_event)
        
def stream_mode_mixed_demo():
    """
    可以在节点内部，将某些函数，方法所产出的数据，传递到节点外部去： 
    """
    from langgraph.runtime import Runtime
    class MyAgentState(TypedDict):
        query:str
        llm_message:str
        rag_search_result:str

    def llm_node(state:MyAgentState,runtime:Runtime):
        """
        用来调用llm的节点
        """
        stream_writer = runtime.stream_writer
        # 通过stream_writer，可以将自定义数据传递到节点外部去
        stream_writer({"event":"llm_call_start"})
        query = state["query"]
        # 这里调用ChatModel，虽然是通过invoke方式调用，但是只要调用graph.stream，并且传入stream_mode为messages，此处的调用也能转换成流式调用
        res = "LLM调用的结果"
        stream_writer({"event":"llm_call_end"})
        return {"llm_message":res}
        # return None
    
    def rag_node(state:MyAgentState):

        query = state["query"]
        rag_search = f"关于{query}RAG搜索的结果"

        return {"rag_search_result":rag_search}
        # return None
    
    builder = StateGraph(MyAgentState)
    builder.add_node(llm_node)
    builder.add_node(rag_node)
    builder.add_edge("__start__",'llm_node')
    builder.add_edge("llm_node","rag_node")
    graph = builder.compile()

    for custom_event in graph.stream({"query":"什么是langgraph"},stream_mode=["custom","values"]):
        print(custom_event)
        # 可以在节点外部，定义一个函数，用来处理节点内部传递过来的自定义数据
        #handler_event(custom_event)


stream_mode_mixed_demo()

    

    
    
