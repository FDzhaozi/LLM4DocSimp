import json
import os
import re


# def extract_json_from_string(input_string):
#     # 首先尝试查找 ```json 和 ``` 之间的内容
#     json_block_pattern = r'```json\s*([\s\S]*?)\s*```'
#     match = re.search(json_block_pattern, input_string)
#
#     if match:
#         json_str = match.group(1)
#     else:
#         # 如果没有找到 ```json 标记，则使用花括号模式
#         # 这种方法可能不能处理所有嵌套情况，但对于大多数情况应该足够了
#         json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
#         match = re.search(json_pattern, input_string)
#         if match:
#             json_str = match.group()
#         else:
#             print("未找到有效的JSON结构")
#             return None
#
#     try:
#         # 尝试解析JSON
#         json_data = json.loads(json_str, strict=False)
#         return json_data
#     except json.JSONDecodeError as e:
#         print(f"JSON解析错误: {e}")
#         return None

def replace_chinese_quotes(text):
    # 定义正则表达式
    colon_pattern = r':\s*(“)'
    brace_pattern = r'(”)\s*}'

    # 替换冒号后面的中文引号为英文引号
    text = re.sub(colon_pattern, r': "', text)

    # 替换大括号前面的中文引号为英文引号
    text = re.sub(brace_pattern, r'"}', text)

    return text
def extract_json_from_string(input_string):
    """
    提取出目标字符串中的json数据。

    Args:
        input_string (str): 包含json数据的字符串。

    Returns:
        dict: 提取出的json数据。
    """
    input_string = replace_chinese_quotes(input_string)
    try:
        # 尝试解析整个字符串为json
        json_data = json.loads(input_string)
        return json_data
    except ValueError:
        # 如果整个字符串不是json，尝试找到字符串中的json数据
        start_idx = input_string.find('{')
        end_idx = input_string.rfind('}')
        if start_idx != -1 and end_idx != -1:
            # 提取出json数据
            json_str = input_string[start_idx:end_idx + 1]
            try:
                # 尝试解析提取出的json数据
                json_data = json.loads(json_str, strict=False)
                return json_data
            except ValueError as e:
                print(e)
                # 如果提取出的json数据不是有效的json，返回None
                return None
        else:
            # 如果找不到json数据，返回None
            return None


def write_to_json(output_json_path, data):
    # 检查文件是否存在
    if not os.path.exists(output_json_path):
        # 如果文件不存在，则创建新文件并写入数据
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump([data], f, ensure_ascii=False, indent=4)
    else:
        # 如果文件存在，则打开文件并加载现有的数据
        with open(output_json_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)

        # 将新数据添加到现有数据中
        existing_data.append(data)

        # 再次打开文件，这次是以写入模式，并将更新后的数据写回
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
    print(f"数据已写入到 {output_json_path}")




def remove_square_brackets(s):
    # 使用正则表达式匹配开头是“[”或“{”的字符串
    match = re.match(r'^(\[|\{)(.*?)(\]|\})$', s)

    # 如果匹配成功，返回中间的内容
    if match:
        return match.group(2)
    # 如果没有匹配，返回原始字符串
    else:
        return s




# 测试函数
if __name__ == "__main__":
    # 示例数据
    # data = {
    #     "simp_type": ["拆分", "调整语序"],
    #     "simplified_text": "虽然天气预报说今天会下雨，早上起来却发现阳光明媚。因此，他决定去公园散步，但仍带上了雨伞以防万一。"
    # }
    #
    # # 输出文件路径
    # output_json_path = 'output.json'
    #
    # # 调用函数
    # write_to_json(output_json_path, data)
    # 示例使用
    input_str = "[这是测试字符串}"
    output_str = remove_square_brackets(input_str)
    print(output_str)  # 输出: 测试字符串
