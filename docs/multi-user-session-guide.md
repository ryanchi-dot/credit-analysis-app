# 多用户会话隔离使用指南

## 功能说明

Agent 现在支持多用户会话隔离，可以区分不同的用户，并记住每个用户的上下文历史记录。

## 核心机制

### Thread ID 生成策略

Agent 使用 `thread_id` 来隔离不同用户的会话历史。`thread_id` 的生成优先级如下：

1. **user_id**（优先级最高）：如果提供了 `user_id`，则使用 `user_{user_id}` 作为 `thread_id`，同一用户的所有请求共享对话历史。
2. **session_id**（优先级中等）：如果提供了 `session_id`，则使用 `session_{session_id}` 作为 `thread_id`，同一会话的所有请求共享对话历史。
3. **run_id**（优先级最低）：兜底方案，使用 `run_{run_id}` 作为 `thread_id`，每次请求都是新会话。

## 使用方式

### 1. 提供用户标识

在请求的 `payload` 中添加 `user_id` 字段：

```json
{
  "messages": [
    {
      "role": "user",
      "content": "分析阿里巴巴集团的授信情况"
    }
  ],
  "user_id": "user_123"
}
```

### 2. 使用会话标识

如果同一个用户想要多个独立的会话，可以使用 `session_id`：

```json
{
  "messages": [
    {
      "role": "user",
      "content": "分析阿里巴巴集团的授信情况"
    }
  ],
  "user_id": "user_123",
  "session_id": "session_001"
}
```

### 3. 兜底模式

如果不提供 `user_id` 或 `session_id`，每次请求都是新会话：

```json
{
  "messages": [
    {
      "role": "user",
      "content": "分析阿里巴巴集团的授信情况"
    }
  ]
}
```

## 使用场景

### 场景1：同一用户多次请求

**用户A（user_123）**：
```
请求1：分析阿里巴巴
→ 生成报告
请求2：再分析腾讯
→ Agent 记得之前的上下文，可以直接分析，无需重复确认
```

**代码示例**：
```python
# 请求1
payload1 = {
  "messages": [{"role": "user", "content": "分析阿里巴巴"}],
  "user_id": "user_123"
}
response1 = await service.run(payload1)

# 请求2
payload2 = {
  "messages": [{"role": "user", "content": "再分析腾讯"}],
  "user_id": "user_123"
}
response2 = await service.run(payload2)
```

### 场景2：不同用户隔离

**用户A（user_123）**：
```
请求：分析阿里巴巴
→ 生成报告
```

**用户B（user_456）**：
```
请求：分析百度
→ Agent 不记得用户A的对话，全新开始
```

**代码示例**：
```python
# 用户A
payload_a = {
  "messages": [{"role": "user", "content": "分析阿里巴巴"}],
  "user_id": "user_123"
}
response_a = await service.run(payload_a)

# 用户B（不会看到用户A的对话历史）
payload_b = {
  "messages": [{"role": "user", "content": "分析百度"}],
  "user_id": "user_456"
}
response_b = await service.run(payload_b)
```

### 场景3：同一用户多会话

**用户A的会话1（session_001）**：
```
请求：分析阿里巴巴
→ 生成报告
```

**用户A的会话2（session_002）**：
```
请求：分析腾讯
→ Agent 不记得会话1的对话，全新开始
```

**代码示例**：
```python
# 会话1
payload1 = {
  "messages": [{"role": "user", "content": "分析阿里巴巴"}],
  "user_id": "user_123",
  "session_id": "session_001"
}
response1 = await service.run(payload1)

# 会话2（不会看到会话1的对话历史）
payload2 = {
  "messages": [{"role": "user", "content": "分析腾讯"}],
  "user_id": "user_123",
  "session_id": "session_002"
}
response2 = await service.run(payload2)
```

## 技术实现

### Thread ID 生成逻辑

```python
def _get_thread_id(self, payload: Dict[str, Any], ctx: Context) -> str:
    user_id = payload.get("user_id")
    session_id = payload.get("session_id")
    
    if user_id:
        return f"user_{user_id}"
    elif session_id:
        return f"session_{session_id}"
    else:
        return f"run_{ctx.run_id}"
```

### 使用 Checkpoint

LangGraph 的 Checkpointer 根据 `thread_id` 保存和恢复对话历史：

```python
run_config["configurable"] = {"thread_id": thread_id}
```

## 注意事项

1. **user_id 必须唯一**：确保每个用户的 `user_id` 是唯一的，避免会话冲突。
2. **会话隔离**：不同的 `user_id` 或 `session_id` 会完全隔离对话历史。
3. **滑动窗口**：默认保留最近 20 轮对话（40 条消息），超过的消息会被丢弃。
4. **数据持久化**：使用 PostgresSaver 时，对话历史会持久化到数据库，重启后不会丢失。

## 测试

### 测试多用户隔离

```python
import asyncio
from src.main import GraphService
from coze_coding_utils.runtime_ctx.context import new_context

async def test_multi_user():
    service = GraphService()
    
    # 用户A
    payload_a = {
        "messages": [{"role": "user", "content": "分析阿里巴巴"}],
        "user_id": "user_123"
    }
    response_a = await service.run(payload_a)
    print(f"用户A：{response_a}")
    
    # 用户B
    payload_b = {
        "messages": [{"role": "user", "content": "分析百度"}],
        "user_id": "user_456"
    }
    response_b = await service.run(payload_b)
    print(f"用户B：{response_b}")
    
    # 用户A继续对话
    payload_a2 = {
        "messages": [{"role": "user", "content": "再分析腾讯"}],
        "user_id": "user_123"
    }
    response_a2 = await service.run(payload_a2)
    print(f"用户A（继续）：{response_a2}")

if __name__ == "__main__":
    asyncio.run(test_multi_user())
```

## 总结

| 功能 | 支持 |
|------|------|
| 能区分每个人吗？ | ✅ 是（通过 user_id） |
| 能识别上下文历史吗？ | ✅ 是（通过 thread_id + checkpointer） |
| 多用户并发安全吗？ | ✅ 是（不同 user_id 隔离） |
| 同一用户多会话吗？ | ✅ 是（通过 session_id） |
