# 微信聊天机器人


## 项目更新

在原有项目基础上进行更新维护，目前可以正常使用

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


