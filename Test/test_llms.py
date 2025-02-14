
def test_aiml_qwen_api():
    from LLMs.qwen_api import aiml_qwen_api
    system_content = "你是一位文本简化专家，请你帮我简化一下这段文字，要求是在尽量保留原意的情况下使得表达更加简洁和通俗易懂。"
    user_content = "原始文本：【第一次出国长住，就感觉好像要把整个家里的东西都一齐搬过去似的。所以吴嘉平认为打包这种事情，亲力亲为是个明智的选择。首先，到了澳大利亚之后，打开并整理行李的是你自己，如果自己需要拿的东西在哪里都不知道的话，怎么能够好好开始路漫漫其修远兮的留学生活呢？】"
    response = aiml_qwen_api(system_content, user_content)
    print(response)

















if __name__ == '__main__':
    test_aiml_qwen_api()
