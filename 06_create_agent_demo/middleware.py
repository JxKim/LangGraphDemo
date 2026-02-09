from langchain_core.messages import SystemMessage
from datetime import datetime

# Middleware，后面会传多个，所以我们在middleware内部，就不定义__call__方法
# 后面，我们通过一个函数，单独封装一个middleware的一个Node
class BaseMiddleware:

    def before_agent(self,state) -> dict:
        pass

    def before_model(self,state) -> dict:
        pass


class CurrentDateMiddleware(BaseMiddleware):

    def before_agent(self,state) -> dict:
        print('当前传入的state为',state)
        system_message = SystemMessage(
            content="当前时间是：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"，当前是周"+str((datetime.now().weekday()+1))
        )

        return {"messages":[system_message]}

