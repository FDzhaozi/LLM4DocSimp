from openai import OpenAI
from Utiles.configs import load_config

config_path = r"../Utiles/config.yml"
config = load_config(config_path)
closeai_api_key = config['closeai_api_key']
closeai_base_url = config['closeai_base_url']


def gpt_api(system_content, user_content):
    client = OpenAI(
        base_url=closeai_base_url,
        api_key=closeai_api_key,
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": user_content
            },
            {
                "role": "system",
                "content": system_content
            }
        ],
        model="chatgpt-4o-latest",
    )
    # print(f"chat_completion: {chat_completion}")

    return chat_completion.choices[0].message.content


if __name__ == '__main__':
    print(gpt_api("你好。", "你是谁？"))
