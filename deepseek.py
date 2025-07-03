import time
import re
# import openai
from wxauto import WeChat
from openai import OpenAI
# 初始化微信
wx = WeChat()
print("微信登录账号:", wx.nickname)

# 监听的群聊名称
GROUP_NAMES = ["决胜灌蛋之巅——7家军"]   # 替换为你的群名

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxxxxxx40"  # 替换为你的 DeepSeek API Key
# openai.api_key = DEEPSEEK_API_KEY
# openai.api_base = "https://api.deepseek.com"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")
# 存储每个群聊的对话上下文 (最多存储 10 条对话)
chat_histories = {group: [] for group in GROUP_NAMES}


def strip_markdown(text):
    # 去掉 Markdown 加粗、标题、代码块等常见格式
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)         # **加粗**
    text = re.sub(r'`([^`]*)`', r'\1', text)             # `行内代码`
    text = re.sub(r'```[\s\S]*?```', '', text)           # 多行代码块
    text = re.sub(r'^#+ ', '', text, flags=re.MULTILINE) # # 标题
    text = re.sub(r'^[-*] ', '', text, flags=re.MULTILINE) # - 列表项
    return text.strip()

def call_deepseek_api(group_name, user_message):
    """ 调用 DeepSeek API 并保持对话记忆 """

    # 获取该群的对话历史
    history = chat_histories.get(group_name, [])

    # 追加新的用户输入
    history.append({"role": "user", "content": user_message})

    # 仅保留最近 10 条对话，避免无限增长
    history = history[-10:]

    # 构造 API 调用的消息列表
    messages = [{"role": "system", "content": (
            "你是一个AI助手。如果用户发送的消息中包含“你是淮”等字眼，那就只需要回复："
            "我是DeepSeek-R1，一个AI助手，我的主人是QZY。"
            "此外，你的所有回答都必须是纯文本，**禁止使用任何 Markdown 语法**，"
            "包括但不限于：星号加粗（**...**）、代码块（```）、标题（#）、列表（-、1.）等。"
            "除非用户明确要求你使用或生成 Markdown，否则绝对不要输出 Markdown 格式。"
        )}] + history

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=1.0,
            stream=False
        )

        # 解析 AI 回复
        if response.choices:
            ai_reply = response.choices[0].message.content.strip()
            ai_reply = strip_markdown(ai_reply)

            # 追加 AI 回复到历史记录
            history.append({"role": "assistant", "content": ai_reply})
            chat_histories[group_name] = history  # 更新群聊历史

            return ai_reply
        else:
            return "AI 没有返回有效结果，请稍后再试"
    except Exception as e:
        return f"DeepSeek API 调用失败: {str(e)}"


botinit = "@喝酒小丸子"
def on_message(msgs, chat):
            print(f"收到来自 {chat} 的消息: {msgs.content}")
    # for chat1 in msgs:
    #     one_msgs = msgs.get(chat1, [])
    #     for last_msg in one_msgs:
            last_msg = msgs
            print(last_msg.__dict__)

            # 仅处理以 'bot' 开头的消息
            if last_msg.content.lower().startswith(botinit):
                user_query = last_msg.content[len(botinit):].strip()
                print(f"检测到 'bot' 触发词，用户输入: {user_query}")

                # 获取该消息所属的群聊
                group_name = next((group for group in GROUP_NAMES if group in str(chat)), 'Unknown')

                # 调用 AI 处理并记忆
                ai_response = call_deepseek_api(group_name, user_query)
                
                # 确保 AI 回复不为空
                if not ai_response or ai_response == "AI 没有返回有效结果，请稍后再试":
                    print("AI 回复为空，跳过发送")
                    return

                print(f"AI 回复: {ai_response}")

                # 发送 AI 回复到群
                wx.SendMsg(ai_response, group_name)
                print(f"已发送 AI 回复到群: {group_name}")
                
# 监听目标群聊
for group in GROUP_NAMES:
    wx.AddListenChat(nickname=group, callback=on_message)
    print(f"已开始监听微信群: {group}")



# 保持程序运行
wx.KeepRunning()
# # 持续监听最新消息
# wait = 3  # 每 3 秒检查一次新消息
# while True:
#     msgs = wx.()
#     print(msgs)


#     time.sleep(wait)  # 休眠3秒，防止高频请求
