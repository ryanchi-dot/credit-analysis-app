# 银行信贷分析助手 - Coze插件使用文档

## 插件简介

银行信贷分析助手是一个专业的企业授信分析工具，能够基于企业公开信息生成符合银行标准的授信分析报告。

### 功能特点

- ✅ **专业分析**：严格按照银行授信分析框架生成报告
- ✅ **全面覆盖**：包含申报方案、客户、财务、行业、结论五大核心部分
- ✅ **数据详实**：基于最新公开财务数据和行业研究报告
- ✅ **格式规范**：生成Word文档，便于编辑和保存
- ✅ **分段生成**：报告分成4个部分，避免内容截断
- ✅ **进度反馈**：实时告知用户生成进度

## 插件配置

### 基本信息

- **插件名称**：银行信贷分析助手
- **版本**：1.0.0
- **类别**：金融分析
- **价格**：免费

### API端点

- **URL**：`https://your-agent-url/stream_run`
- **Method**：`POST`
- **Content-Type**：`application/json`

## 输入参数

### 必填参数

| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| company_name | string | 企业名称 | "腾讯控股有限公司" |

### 可选参数

| 参数名 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| analysis_focus | select | 分析重点 | "全面分析（推荐）" |
| has_reference_materials | boolean | 是否有参考材料 | false |

## 输出参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| report_part1_url | string | 第一部分下载链接 |
| report_part2_url | string | 第二部分下载链接 |
| report_part3_url | string | 第三部分下载链接 |
| report_part4_url | string | 第四部分下载链接 |
| report_summary | string | 报告摘要 |

## 使用示例

### 示例1：全面分析

**输入**：
```json
{
  "company_name": "腾讯控股有限公司",
  "analysis_focus": "全面分析（推荐）",
  "has_reference_materials": false
}
```

**输出**：
```json
{
  "report_part1_url": "https://example.com/part1.docx",
  "report_part2_url": "https://example.com/part2.docx",
  "report_part3_url": "https://example.com/part3.docx",
  "report_part4_url": "https://example.com/part4.docx",
  "report_summary": "本报告对腾讯控股有限公司进行了全面的授信分析..."
}
```

### 示例2：重点分析财务

**输入**：
```json
{
  "company_name": "京东集团股份有限公司",
  "analysis_focus": "财务分析",
  "has_reference_materials": true
}
```

### 示例3：在Coze Bot中使用

```python
# 在Coze Bot的代码节点中调用插件
import coze

# 调用插件
result = coze.call_plugin(
    plugin_name="银行信贷分析助手",
    params={
        "company_name": "阿里巴巴集团控股有限公司",
        "analysis_focus": "全面分析（推荐）"
    }
)

# 获取报告链接
report_links = [
    result["report_part1_url"],
    result["report_part2_url"],
    result["report_part3_url"],
    result["report_part4_url"]
]

# 返回给用户
return {
    "message": "授信分析报告已生成完成！",
    "report_links": report_links
}
```

## 报告结构说明

生成的授信分析报告分为4个部分：

### 第一部分：申报方案分析与客户分析
- 多维度风险及缓释措施分析
- 同业授信情况分析
- 集团介绍
- 借款人经营分析

### 第二部分：财务分析
- 资产负债及偿债能力分析
- 盈利能力分析
- 流动性风险/历史现金流分析
- 现金流量预测

### 第三部分：行业分析及同业比较
- 行业现状分析
- 行业前景及风险分析
- 同业竞争对手比较

### 第四部分：结论
- 关键风险总结
- 缓释措施
- 授信建议

## 使用注意事项

1. **企业名称**：请提供准确的中文全称，确保分析准确
2. **分析时间**：生成完整报告需要5-8分钟时间
3. **报告下载**：点击下载链接即可保存Word文档
4. **数据时效性**：报告基于最新公开数据，数据来源包括企业年报、行业研究报告等
5. **仅供参考**：报告内容仅供参考，不构成投资建议

## 常见问题

### Q1：生成报告需要多长时间？

**A**：生成完整的授信分析报告通常需要5-8分钟时间，具体取决于企业规模和信息获取难度。

### Q2：报告可以编辑吗？

**A**：可以，生成的报告是Word文档格式，可以自由编辑和修改。

### Q3：支持哪些企业？

**A**：支持所有公开上市的企业（A股、港股、美股），以及部分非上市的知名企业。

### Q4：报告是否准确？

**A**：报告基于企业公开的财务数据和行业研究报告，数据来源可靠，分析过程严谨。

### Q5：可以分析国外企业吗？

**A**：当前版本主要支持中国企业，国外企业的支持正在开发中。

## 技术支持

如有问题或建议，请联系：
- 插件作者：Vibe Coding
- 技术支持：support@example.com

## 更新日志

### v1.0.0 (2026-03-02)
- ✅ 首次发布
- ✅ 支持企业授信分析
- ✅ 支持分段生成报告
- ✅ 支持进度反馈
