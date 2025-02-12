import time
import openai
from wxauto import WeChat

# 初始化微信
wx = WeChat()
print("微信登录账号:", wx.nickname)

# 监听的群聊名称
GROUP_NAMES = ["group1", "group2", "group3"]

# DeepSeek API 配置 (使用 DeepSeek 的 OpenAI SDK)
DEEPSEEK_API_KEY = "your - key"  # 替换为你的 DeepSeek API Key
openai.api_key = DEEPSEEK_API_KEY  # 设置 API 密钥
openai.api_base = "https://api.deepseek.com"  # DeepSeek API 的基础 URL

def call_deepseek_api(user_message):
    """ 调用 DeepSeek API 获取 AI 回复 """
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",  # 使用 DeepSeek 的模型
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": user_message},
            ],
            stream=False
        )

        # 打印返回的响应
        print("DeepSeek AI 回复:", response)

        # 获取 AI 回复内容
        if response.choices:
            ai_reply = response.choices[0].message['content'].strip()  # 获取 AI 的文本回复
            return ai_reply
        else:
            return "AI 没有返回有效结果，请稍后再试"
    except Exception as e:
        return f"DeepSeek API 调用失败: {str(e)}"

# 监听目标群聊
for i in GROUP_NAMES:
    wx.AddListenChat(who=i, savepic=False)
    print(f"已开始监听微信群: {i}")

# 持续监听最新消息
wait = 3  # 每3秒检查一次新消息
while True:
    msgs = wx.GetListenMessage()
    for chat in msgs:
        one_msgs = msgs.get(chat)  # 获取该群最新的消息
        for last_msg in one_msgs:
            print(last_msg.__dict__)

            # 如果发送者是 'Self'，跳过该消息
           # if last_msg.sender == 'Self':
             #   continue  # 跳过当前循环，处理下一个消息

            # 仅处理以 'bot' 开头的消息
            if last_msg.content.lower().startswith("bot"):
                user_query = last_msg.content[len("bot"):].strip()  # 去掉 'bot' 前缀，提取用户输入
                print(f"检测到 'bot' 触发词，用户输入: {user_query}")

                # 调用 DeepSeek API 获取 AI 回复
                ai_response = call_deepseek_api(user_query)

                # 确保 AI 回复不为空
                if not ai_response or ai_response == "AI 没有返回有效结果，请稍后再试":
                    print("AI 回复为空，跳过发送")
                    continue

                print(f"AI 回复: {ai_response}")

                # 确保 GROUP_NAME 是字符串类型
                groupName = next((group for group in GROUP_NAMES if group in str(chat)), 'Unknown')
                # 发送 AI 回复到群
                wx.SendMsg(ai_response, groupName)
                print(f"已发送 AI 回复到群: {groupName}")

    time.sleep(wait)  # 休眠3秒，防止高频请求
