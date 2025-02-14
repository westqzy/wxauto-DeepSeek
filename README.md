# 微信聊天机器人

## 项目简介
本项目是一个基于 **WeChat wxauto** 和 **DeepSeek AI API** 的微信聊天机器人，能够监听指定微信群，并根据关键词 `bot` 触发 AI 对话。

## 功能特点
- **监听微信群消息**：实时监听指定群聊的消息。
- **智能 AI 回复**：调用 DeepSeek AI 进行智能聊天。
- **记忆功能**：支持对话上下文，能进行连续对话。
- **自动清理历史**：最多存储 10 条上下文记录，防止无限增长。

## 依赖环境
- Python 3.8 及以上
- `wxauto`（用于微信自动化）
- `openai`（用于调用 DeepSeek API）

## 安装依赖
```bash
pip install wxauto openai
```

## 配置 API Key
在 `Python` 代码中找到以下代码，并替换为你的 DeepSeek API Key：
```python
DEEPSEEK_API_KEY = "your-deepseek-api-key-here"
openai.api_key = DEEPSEEK_API_KEY
openai.api_base = "https://api.deepseek.com"
```

## 代码结构
```python
import time
import openai
from wxauto import WeChat

# 初始化微信
wx = WeChat()
print("微信登录账号:", wx.nickname)

# 监听的微信群聊
GROUP_NAMES = ["群聊名1"]

# 存储每个群聊的对话历史
chat_histories = {group: [] for group in GROUP_NAMES}

def call_deepseek_api(group_name, user_message):
    """ 调用 DeepSeek API 并保持对话记忆 """
    history = chat_histories.get(group_name, [])
    history.append({"role": "user", "content": user_message})
    history = history[-10:]
    messages = [{"role": "system", "content": "You are a helpful assistant"}] + history
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=messages,
            temperature=1.3,
            stream=False
        )
        if response.choices:
            ai_reply = response.choices[0].message['content'].strip()
            history.append({"role": "assistant", "content": ai_reply})
            chat_histories[group_name] = history
            return ai_reply
    except Exception as e:
        return f"DeepSeek API 调用失败: {str(e)}"

# 监听群聊
for group in GROUP_NAMES:
    wx.AddListenChat(who=group, savepic=False)
    print(f"已开始监听微信群: {group}")

# 持续监听消息
wait = 3
while True:
    msgs = wx.GetListenMessage()
    for chat in msgs:
        one_msgs = msgs.get(chat, [])
        for last_msg in one_msgs:
            if last_msg.content.lower().startswith("bot"):
                user_query = last_msg.content[len("bot"):].strip()
                group_name = next((group for group in GROUP_NAMES if group in str(chat)), 'Unknown')
                ai_response = call_deepseek_api(group_name, user_query)
                if ai_response:
                    wx.SendMsg(ai_response, group_name)
                    print(f"已发送 AI 回复到群: {group_name}")
    time.sleep(wait)
```

## 使用方式
1. **登录微信**
   - 运行代码后，确保微信已登录。
2. **设置监听群聊**
   - 在 `GROUP_NAMES` 变量中添加需要监听的微信群名称。
3. **发送消息触发 AI 回复**
   - 发送 `bot` 开头的消息，即可触发 AI 回复。

## 示例对话
**用户在微信群中发送：**
```
bot 你好！
```
**AI 回复：**
```
你好！我是智能助手，有什么可以帮助你的吗？
```


