from typing import Any, Sequence
from langchain.tools import BaseTool
from concurrent.futures import ThreadPoolExecutor
from langchain.messages import ToolMessage
class ToolNode:

    def __init__(
            self,
            tools: Sequence[BaseTool] | None = None,
            max_workers: int =3
    ):
        
        self.tools = tools
        self.max_workers = max_workers
        self.name_to_tool = {tool.name:tool for tool in self.tools}

    def __call__(self,state,runtime) -> Any:
        message_list = state["messages"]
        last_message = message_list[-1] # 最后一个message 就是一个ai_message tool_calls
        tool_calls = last_message.tool_calls
        print('当前的tool_calls为',tool_calls)
        # 将tool_call提交到线程池执行
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # executor.map(): 第一个参数，传递的线程需要执行的函数，第二个参数，以list形式传递函数执行参数
            result_generator = executor.map(lambda tool_call:self.execute_single_tool(tool_call) ,tool_calls)

            results: list[ToolMessage] = list(result_generator)
        
        # tool节点对messages状态做增量更新
        return {"messages":results}


    def execute_single_tool(self,tool_call:dict)->ToolMessage:
        """
        执行单个tool_call
        """
        tool_name:str = tool_call["name"]
        tool_args:dict = tool_call["args"]
        tool_call_id:str = tool_call["id"]
        tool:BaseTool = self.name_to_tool[tool_name]

        try:
            result = tool.invoke(tool_args)
            return ToolMessage(
                content=result,
                tool_call_id = tool_call_id
            )
        except Exception as e:
            # 这里可以写一个handler函数，处理异常情况，对不同的异常情况，封装不同的content
            return ToolMessage(
                content=f"调用工具{tool_name}时发生异常：{e}",
                tool_call_id = tool_call_id
            )



