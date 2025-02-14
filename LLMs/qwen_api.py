import json
import os

import openai
from openai import OpenAI

from LLMs.gpt_api import gpt_api
from LLMs.zhipu_api import zhipu_api
from Utiles.configs import load_config
from http import HTTPStatus

config_path = r"../Utiles/config.yml"
config = load_config(config_path)
aiml_qwen_key = config['aiml_qwen_api_key']
aiml_qwen_base_url = config['aiml_qwen_base_url']
ali_qwen_key = config['ali_api_key']
ali_qwen_base = config['ali_base_url']


def aiml_qwen_api(system_content, user_content):
    client = openai.OpenAI(
        api_key=aiml_qwen_key,
        base_url=aiml_qwen_base_url
    )

    chat_completion = client.chat.completions.create(
        model="Qwen/Qwen1.5-72B-Chat",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        temperature=0.7,
        max_tokens=512,
    )
    print(f"chat_completion: {chat_completion}")

    response = chat_completion.choices[0].message.content
    if response is None:
        return None
    return response




def ali_qwen_api(system_content, user_content):
    client = OpenAI(
        api_key=ali_qwen_key,
        base_url=ali_qwen_base,
    )
    messages = [
        {'role': 'system', 'content': system_content},
        {'role': 'user', 'content': user_content}]
    print(messages)
    try:
        # completion = client.chat.completions.create(model="qwen-max", messages=messages)
        # completion_json = json.loads(completion.model_dump_json())
        # result = completion_json["choices"][0]["message"]["content"]
        result = zhipu_api(system_content, user_content)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("QWEN API 出错，正在调用 AIML QWEN API")
        try:
            result = aiml_qwen_api(system_content, user_content)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("AIML QWEN API 出错，正在调用 Zhipu API")
            try:
                completion = client.chat.completions.create(model="qwen-max", messages=messages)
                completion_json = json.loads(completion.model_dump_json())
                result = completion_json["choices"][0]["message"]["content"]

            except Exception as e:
                print(f"An error occurred: {e}")
                print("Zhipu API 出错，正在调用 GPT API")
                try:
                    result = gpt_api(system_content, user_content)
                except Exception as e:
                    print(f"An error occurred: {e}")
                    print("GPT API 出错，返回空值")
                    result =  None

        # return None

    return result


def simp_aiml_qwen_api(user_content):
    system_content = "你是一位中文语言的文本简化专家，请你按照下面的要求完成任务。"
    response = ali_qwen_api(system_content, user_content)

    return response


if __name__ == '__main__':
    # result = ali_qwen_api("你好", "你是谁")
    # print(result)
    pass




