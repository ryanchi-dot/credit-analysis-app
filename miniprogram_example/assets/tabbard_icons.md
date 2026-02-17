# TabBar 图标说明

## 需要的图标文件

小程序的 TabBar 需要 4 个图标文件（每个 40x40 像素）：

1. **analyze.png** - 分析图标（未选中）
2. **analyze-active.png** - 分析图标（选中）
3. **chat.png** - 对话图标（未选中）
4. **chat-active.png** - 对话图标（选中）

## 临时方案（不使用 TabBar）

如果暂时没有图标文件，可以暂时移除 TabBar 配置：

修改 `app.json`，删除 `"tabBar"` 部分：

```json
{
  "pages": [
    "pages/index/index",
    "pages/chat/chat",
    "pages/progress/progress",
    "pages/report/report"
  ],
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#1890ff",
    "navigationBarTitleText": "银行信贷分析助手",
    "navigationBarTextStyle": "white"
  },
  "style": "v2",
  "sitemapLocation": "sitemap.json"
}
```

## 如何获取图标

### 方案1：使用在线图标
从 Iconfont 或其他图标库下载图标：
- 推荐网站：https://www.iconfont.cn/
- 搜索关键词：分析、对话、聊天
- 下载 40x40 像素的 PNG 图片
- 放置到 assets 目录

### 方案2：使用图片生成工具
使用在线工具生成图标：
- https://favicon.io/
- https://www.flaticon.com/

### 方案3：暂时移除 TabBar
使用上面的"临时方案"，暂时不使用 TabBar，通过导航栏标题区分页面。

## 推荐方案

建议使用方案3（暂时移除 TabBar），快速测试功能。
