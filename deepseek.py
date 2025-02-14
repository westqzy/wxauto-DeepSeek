import time
import openai
from wxauto import WeChat

# 初始化微信
wx = WeChat()
print("微信登录账号:", wx.nickname)

# 监听的群聊名称
GROUP_NAMES = ["群聊2","群聊1"]

# DeepSeek API 配置
DEEPSEEK_API_KEY = "your-key"  # 替换为你的 DeepSeek API Key
openai.api_key = DEEPSEEK_API_KEY
openai.api_base = "https://api.deepseek.com"

# 存储每个群聊的对话上下文 (最多存储 10 条对话)
chat_histories = {group: [] for group in GROUP_NAMES}


def call_deepseek_api(group_name, user_message):
    """ 调用 DeepSeek API 并保持对话记忆 """

    # 获取该群的对话历史
    history = chat_histories.get(group_name, [])

    # 追加新的用户输入
    history.append({"role": "user", "content": user_message})

    # 仅保留最近 10 条对话，避免无限增长
    history = history[-10:]

    # 构造 API 调用的消息列表
    messages = [{"role": "system", "content": "You are a helpful assistant"}] + history

    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=messages,
            temperature=1.3,
            stream=False
        )

        # 解析 AI 回复
        if response.choices:
            ai_reply = response.choices[0].message['content'].strip()

            # 追加 AI 回复到历史记录
            history.append({"role": "assistant", "content": ai_reply})
            chat_histories[group_name] = history  # 更新群聊历史

            return ai_reply
        else:
            return "AI 没有返回有效结果，请稍后再试"
    except Exception as e:
        return f"DeepSeek API 调用失败: {str(e)}"


# 监听目标群聊
for group in GROUP_NAMES:
    wx.AddListenChat(who=group, savepic=False)
    print(f"已开始监听微信群: {group}")

# 持续监听最新消息
wait = 3  # 每 3 秒检查一次新消息
while True:
    msgs = wx.GetListenMessage()
    for chat in msgs:
        one_msgs = msgs.get(chat, [])
        for last_msg in one_msgs:
            print(last_msg.__dict__)

            # 仅处理以 'bot' 开头的消息
            if last_msg.content.lower().startswith("bot"):
                user_query = last_msg.content[len("bot"):].strip()
                print(f"检测到 'bot' 触发词，用户输入: {user_query}")

                # 获取该消息所属的群聊
                group_name = next((group for group in GROUP_NAMES if group in str(chat)), 'Unknown')

                # 调用 AI 处理并记忆
                ai_response = call_deepseek_api(group_name, user_query)

                # 确保 AI 回复不为空
                if not ai_response or ai_response == "AI 没有返回有效结果，请稍后再试":
                    print("AI 回复为空，跳过发送")
                    continue

                print(f"AI 回复: {ai_response}")

                # 发送 AI 回复到群
                wx.SendMsg(ai_response, group_name)
                print(f"已发送 AI 回复到群: {group_name}")

    time.sleep(wait)  # 休眠3秒，防止高频请求
