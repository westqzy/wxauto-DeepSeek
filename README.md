

# 基于 wxauto 的 DeepSeek 机器人实现

该文档展示了如何使用 `wxauto` 库和 DeepSeek 的 OpenAI SDK 实现一个简单的微信机器人，能够监听微信群中的消息并进行自动回复。

## 环境要求

- Python 3.x
- `wxauto` 库：用于操作微信
- `openai` 库：用于访问 DeepSeek API
- DeepSeek API Key：获取 DeepSeek 提供的 API 密钥
- wxauto地址：https://github.com/cluic/wxauto

## 安装依赖

首先，确保安装所需的库：

```bash
pip install wxauto openai
```

## 代码实现

```python
import time
import openai
from wxauto import WeChat

# 初始化微信
wx = WeChat()
print("微信登录账号:", wx.nickname)

# 监听的群聊名称
GROUP_NAMES = ["group1", "group2", "group3"]

# DeepSeek API 配置 (使用 DeepSeek 的 OpenAI SDK)
DEEPSEEK_API_KEY = "your-key"  # 替换为你的 DeepSeek API Key
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
```

## 代码说明

### 1. 初始化微信

```python
wx = WeChat()
print("微信登录账号:", wx.nickname)
```

这段代码初始化了 `wxauto` 并打印出当前登录微信账号的昵称。

### 2. 配置 DeepSeek API

```python
DEEPSEEK_API_KEY = "your-key"  # 替换为你的 DeepSeek API Key
openai.api_key = DEEPSEEK_API_KEY  # 设置 API 密钥
openai.api_base = "https://api.deepseek.com"  # DeepSeek API 的基础 URL
```

这里需要配置您的 DeepSeek API 密钥。

### 3. 调用 DeepSeek API 获取 AI 回复

```python
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
        ...
```

该函数接收用户消息并调用 DeepSeek API 生成 AI 回复。

### 4. 监听微信群消息

```python
for i in GROUP_NAMES:
    wx.AddListenChat(who=i, savepic=False)
    print(f"已开始监听微信群: {i}")
```

使用 `wxauto` 的 `AddListenChat` 函数监听多个微信群，并且打印监听的群聊名称。

### 5. 处理并回复消息

```python
while True:
    msgs = wx.GetListenMessage()
    for chat in msgs:
        ...
        if last_msg.content.lower().startswith("bot"):
            ...
            ai_response = call_deepseek_api(user_query)
            ...
            wx.SendMsg(ai_response, groupName)
            print(f"已发送 AI 回复到群: {groupName}")
```

该部分代码在群聊中监听消息，并且当消息内容以 `bot` 开头时，调用 DeepSeek API 获取回复并发送到微信群。
