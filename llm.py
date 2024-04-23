import json
import time
from typing import Any, Dict, Literal, Tuple, Union

import openai
import yaml
from openai.types.chat import ChatCompletionMessage, ChatCompletionToolParam

from configs import configs
from level_functions import *

openai.api_key = configs.openai_api_key


def run_prompt(messages: List[Union[ChatCompletionMessage, Dict[str, str]]], level: Level, tools: List[ChatCompletionToolParam]) -> Tuple[str, str]:
    output = ChatCompletionMessage(content=None, role='assistant')
    additional_info = ''
    
    while output.content is None:
        output = openai.chat.completions.create(model=configs.model_name,
                                                temperature=configs.temperature,
                                                top_p=0.,
                                                messages=messages,
                                                tools=tools,
                                                seed=time.time_ns()  # enforce different RNG seeding
                                                ).choices[0].message
        if output.tool_calls:
            for tool_call in output.tool_calls:
                function_to_call = eval(tool_call.function.name)
                additional_info += f"\t-> calling {tool_call.function.name}({tool_call.function.arguments})\n"
                next_ai_msg = function_to_call(level=level, **json.loads(tool_call.function.arguments))
                additional_info += f"\t\t-> {next_ai_msg}\n"
                # print(additional_info)
                messages.append(output)
                messages.append({"tool_call_id": tool_call.id,
                                 "role": "tool",
                                 "name": tool_call.function.name,
                                 "content": next_ai_msg})
    return output.content, additional_info
