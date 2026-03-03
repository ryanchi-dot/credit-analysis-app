# 工作流调用示例

## 方式1：调用已部署的Coze Bot

### 创建工作流

1. 进入Coze平台 → 工作流 → 创建工作流
2. 添加"调用Bot"节点
3. 配置节点：

```
节点名称：生成授信分析报告
Bot名称：银行信贷分析助手
输入参数：
  - company_name: {{input_company_name}}
  - analysis_focus: {{input_analysis_focus}}
输出参数：
  - report_part1_url
  - report_part2_url
  - report_part3_url
  - report_part4_url
  - report_summary
```

4. 添加"结束"节点，返回报告链接

### 工作流输入配置

```json
{
  "input_company_name": {
    "type": "string",
    "label": "企业名称",
    "required": true,
    "placeholder": "请输入企业名称"
  },
  "input_analysis_focus": {
    "type": "select",
    "label": "分析重点",
    "required": false,
    "options": [
      "全面分析（推荐）",
      "财务分析",
      "行业研究",
      "风险评估"
    ],
    "default": "全面分析（推荐）"
  }
}
```

### 工作流输出配置

```json
{
  "report_links": {
    "type": "array",
    "label": "报告下载链接"
  },
  "report_summary": {
    "type": "string",
    "label": "报告摘要"
  }
}
```

---

## 方式2：HTTP请求调用外部API

### 创建工作流

1. 进入Coze平台 → 工作流 → 创建工作流
2. 添加"HTTP请求"节点
3. 配置节点：

```
节点名称：调用授信分析API
URL: https://your-agent-url/stream_run
Method: POST
Headers:
  Content-Type: application/json
Body:
  {
    "type": "query",
    "content": {
      "query": {
        "prompt": [
          {
            "type": "text",
            "content": {
              "text": "请分析{{input_company_name}}的授信情况，分析重点为{{input_analysis_focus}}"
            }
          }
        ]
      }
    }
  }
```

4. 添加"代码节点"解析返回结果：

```python
# 解析HTTP响应
response = workflow_node["调用授信分析API"]["response"]

# 提取报告链接（假设返回格式包含下载链接）
report_links = []
for part in ["part1", "part2", "part3", "part4"]:
    if f"report_{part}_url" in response:
        report_links.append(response[f"report_{part}_url"])

# 返回结果
return {
    "report_links": report_links,
    "report_summary": response.get("report_summary", "")
}
```

---

## 方式3：在Bot中直接调用

### 在Bot的对话中使用插件

```
用户：帮我分析一下腾讯的授信情况

Bot回复：
好的，我将为您生成腾讯的授信分析报告。
正在分析中，预计需要5-8分钟时间...

[调用插件]
插件：银行信贷分析助手
参数：
  - company_name: "腾讯控股有限公司"
  - analysis_focus: "全面分析"

[返回结果]
报告已生成完成！下载链接如下：
1. 第一部分：申报方案分析与客户分析
   [下载链接]
2. 第二部分：财务分析
   [下载链接]
3. 第三部分：行业分析及同业比较
   [下载链接]
4. 第四部分：结论
   [下载链接]

报告摘要：本报告对腾讯控股有限公司进行了全面的授信分析...
```

---

## 完整工作流示例

### 场景：批量生成多个企业的授信分析报告

```
工作流：批量授信分析
┌─────────────────────────────────┐
│  开始                           │
│  输入：企业列表                │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  循环：遍历企业列表             │
│  当前企业：{{current_company}}   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  调用Bot：银行信贷分析助手      │
│  参数：                         │
│    company_name: {{current_company}}│
│    analysis_focus: "全面分析"   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  代码节点：保存报告链接          │
│  将结果添加到结果列表           │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  循环结束                       │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  结束                           │
│  输出：所有报告的下载链接        │
└─────────────────────────────────┘
```

### 工作流输入

```json
{
  "companies": [
    "腾讯控股有限公司",
    "京东集团股份有限公司",
    "阿里巴巴集团控股有限公司"
  ]
}
```

### 工作流输出

```json
{
  "results": [
    {
      "company": "腾讯控股有限公司",
      "report_links": [
        "https://example.com/tencent_part1.docx",
        "https://example.com/tencent_part2.docx",
        "https://example.com/tencent_part3.docx",
        "https://example.com/tencent_part4.docx"
      ]
    },
    {
      "company": "京东集团股份有限公司",
      "report_links": [
        "https://example.com/jd_part1.docx",
        "https://example.com/jd_part2.docx",
        "https://example.com/jd_part3.docx",
        "https://example.com/jd_part4.docx"
      ]
    },
    {
      "company": "阿里巴巴集团控股有限公司",
      "report_links": [
        "https://example.com/alibaba_part1.docx",
        "https://example.com/alibaba_part2.docx",
        "https://example.com/alibaba_part3.docx",
        "https://example.com/alibaba_part4.docx"
      ]
    }
  ]
}
```

---

## 错误处理

### 添加错误处理节点

```python
try:
    # 尝试调用插件
    result = call_plugin("银行信贷分析助手", params)

    # 检查返回结果
    if not result.get("report_part1_url"):
        raise Exception("报告生成失败：缺少第一部分链接")

    # 返回成功结果
    return {
        "success": True,
        "report_links": [
            result["report_part1_url"],
            result["report_part2_url"],
            result["report_part3_url"],
            result["report_part4_url"]
        ]
    }

except Exception as e:
    # 返回错误信息
    return {
        "success": False,
        "error_message": str(e),
        "suggestion": "请检查企业名称是否正确，或稍后重试"
    }
```

### 重试机制

```python
max_retries = 3
retry_count = 0

while retry_count < max_retries:
    try:
        result = call_plugin("银行信贷分析助手", params)
        return result
    except Exception as e:
        retry_count += 1
        if retry_count >= max_retries:
            raise Exception(f"调用失败，已重试{max_retries}次：{str(e)}")
        # 等待5秒后重试
        time.sleep(5)
```

---

## 总结

- ✅ **插件调用**：适合单一Bot使用，简单直接
- ✅ **工作流调用**：适合复杂的业务流程，可以组合多个节点
- ✅ **HTTP请求**：适合集成外部系统，灵活性高

选择哪种方式取决于你的具体需求：
- 如果只是在一个Bot中使用 → 插件调用最简单
- 如果需要与其他功能组合 → 工作流调用最灵活
- 如果需要跨平台集成 → HTTP请求最通用
