from zhipuai import ZhipuAI
from Utiles.configs import load_config

config_path = r"../Utiles/config.yml"
config = load_config(config_path)
zhipu_key = config['zhipu_api_key']


def zhipu_api(system_content, user_content):
    client = ZhipuAI(api_key=zhipu_key)

    response = client.chat.completions.create(
        # model="glm-4-flash",  # 填写需要调用的模型编码
        model="GLM-4-FlashX",  # 填写需要调用的模型编码
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user",
             "content": user_content}
        ],
    )

    return response.choices[0].message.content


if __name__ == '__main__':
    print(zhipu_api("你好。", "谁是中国的国家主席？"))
