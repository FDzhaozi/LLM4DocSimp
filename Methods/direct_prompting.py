import json
import os
import sys

from LLMs.qwen_api import simp_aiml_qwen_api
from Utiles.format_output import extract_json_from_string
from Methods.para_aspect import seg_to_chunks

def generate_prompt():
    """
    生成 Direct Prompting 的中文提示词。
   
    :return: 适用于 LLM 的完整提示词
    """
    return f"""
你是一位中文文本简化专家，任务是将输入的文档进行简化形式的复述。
请按照以下要求进行处理：
1. 保持文本的核心信息不变，确保语义清晰。
2. 适当降低语言复杂度，使其更通俗易懂。
3. 生成 JSON 格式的输出，包含 "simplified" 键，其值为简化后的文本。
"""


def direct_prompting(input_text, max_chunk_size=500):
    """
    使用 Direct Prompting 方法进行文档简化。
    
    :param input_text: 需要简化的原始文本
    :param max_chunk_size: 允许的最大文本块大小（避免超出模型输入限制）
    :return: 简化文档
    """
    current_text = ""
    for i in range(iterations):
        prompt = generate_prompt()

        # 如果文本过长，按块处理
        chunks = seg_to_chunks(input_text, max_chunk_size)
        simplified_chunks = []

        for chunk in chunks:
            full_prompt = f"{prompt}\n\n原始文本：{chunk}\n请输出 JSON 结果："
            response = simp_aiml_qwen_api(full_prompt)

            # 解析 JSON 输出
            extracted_json = extract_json_from_string(response)
            if extracted_json and "simplified" in extracted_json:
                simplified_chunks.append(extracted_json["simplified"])
            else:
                simplified_chunks.append(chunk)  # 失败时保留原文

        # 更新当前文本，进入下一次迭代
        current_text = " ".join(simplified_chunks)

    return current_text


if __name__ == "__main__":
    test_text = "《西游记》是一部中国古代神话小说，讲述了唐僧师徒四人西天取经的故事..."
    
    ver1_text = direct_prompting(test_text)
    ver2_text = direct_prompting(ver1_text)
    ver3_text = direct_prompting(ver2_text)
    
    
    print("Ver1 Simplification:", ver1_text)
  
