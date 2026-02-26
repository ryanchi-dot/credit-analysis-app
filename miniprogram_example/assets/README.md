# 资源文件说明

## 头像图片

本目录需要放置两个头像图片：

1. **user-avatar.png** - 用户头像（70x70 像素）
2. **assistant-avatar.png** - 助手头像（70x70 像素）

## 临时方案

如果暂时没有头像图片，可以使用以下方法：

### 方法1：使用在线图片
在 chat.wxml 中修改头像 src：

```xml
<!-- 用户头像（使用微信默认头像） -->
<image class="avatar user-avatar" src="https://thirdwx.qlogo.cn/mmopen/vi_32/POgEwh4mIHO4nibH0KlMECNjjGxQUq24ZEaGT4poC6icRiccVGKSyXwibcPq4BWmiaIGuG1icwxaQX6grC9VemZoJ8rg/132"></image>

<!-- 助手头像（使用在线图片） -->
<image class="avatar assistant-avatar" src="https://thirdwx.qlogo.cn/mmopen/vi_32/DYAIOgq83eqojf0CrSVuvx2ib6xvY6ip2iaQX6icF5aHYua/132"></image>
```

### 方法2：使用 CSS 颜色
在 chat.wxss 中使用背景色代替图片：

```css
.user-avatar {
  background-color: #1890ff;
  /* 删除 src 属性，使用纯色背景 */
}

.assistant-avatar {
  background-color: #52c41a;
  /* 删除 src 属性，使用纯色背景 */
}
```

然后修改 chat.wxml，删除 avatar 标签的 src 属性：

```xml
<view class="avatar user-avatar"></view>
<view class="avatar assistant-avatar"></view>
```

## 推荐方案

建议使用方法2（CSS颜色），简单且不需要额外文件。
