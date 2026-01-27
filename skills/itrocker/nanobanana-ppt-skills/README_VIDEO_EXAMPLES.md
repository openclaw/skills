# README 视频演示添加方案

## 方案选择建议

### 🎯 推荐方案对比

| 方案 | 文件大小限制 | 国内访问 | 国外访问 | 自动播放 | 维护成本 |
|------|------------|----------|----------|----------|---------|
| **GIF 动图** | 建议 < 10MB | ✅ 快 | ✅ 快 | ✅ 是 | ⭐ 低 |
| **GitHub 仓库视频** | < 100MB | ⚠️ 慢 | ✅ 快 | ❌ 否 | ⭐ 低 |
| **Bilibili** | 无限制 | ✅ 快 | ⚠️ 慢 | ❌ 否 | ⭐⭐ 中 |
| **GitHub + Bilibili** | - | ✅ 快 | ✅ 快 | ❌ 否 | ⭐⭐ 中 |
| **Cloudinary** | 25GB 免费 | ✅ 快 | ✅ 快 | ❌ 否 | ⭐⭐⭐ 高 |

### 💡 具体建议

**对于你的项目（NanoBanana PPT Skills）**，我推荐：

1. **首选：GIF 动图** - 如果能压缩到 5-10MB 以内
   - 最佳用户体验，自动播放
   - 适合展示 10-20 秒核心功能演示

2. **备选：GitHub 仓库 + Bilibili 双链接**
   - GitHub 放短视频（< 50MB）展示核心功能
   - Bilibili 放完整演示（带讲解）
   - 照顾国内外用户

---

## Markdown 代码示例

### 方案 1: GIF 动图（推荐）

在 README.md 第 15 行（`</div>` 之后）添加：

```markdown
</div>

---

## 🎬 效果演示

<div align="center">

![NanoBanana PPT Skills Demo](demo.gif)

*AI 自动生成 PPT 并添加流畅转场动画*

</div>

---
```

**或者使用 HTML 标签控制大小：**

```markdown
<div align="center">
  <img src="demo.gif" alt="NanoBanana PPT Skills Demo" width="800">
  <p><em>AI 自动生成 PPT 并添加流畅转场动画</em></p>
</div>
```

---

### 方案 2: GitHub 仓库视频（< 100MB）

```markdown
## 🎬 效果演示

<div align="center">

https://github.com/op7418/NanoBanana-PPT-Skills/assets/YOUR_USER_ID/demo.mp4

*点击播放查看完整演示*

</div>
```

**或使用 HTML5 video 标签（更多控制）：**

```markdown
<div align="center">
  <video src="https://github.com/op7418/NanoBanana-PPT-Skills/assets/YOUR_USER_ID/demo.mp4"
         width="800"
         controls
         loop
         muted>
    您的浏览器不支持视频播放
  </video>
  <p><em>AI 自动生成 PPT 并添加流畅转场动画</em></p>
</div>
```

---

### 方案 3: Bilibili 嵌入

```markdown
## 🎬 效果演示

<div align="center">

[![Watch Demo on Bilibili](https://i0.hdslb.com/bfs/archive/VIDEO_COVER.jpg)](https://www.bilibili.com/video/BVXXXXXXX)

**🎥 [点击观看完整演示视频（Bilibili）](https://www.bilibili.com/video/BVXXXXXXX)**

*包含详细功能讲解和使用教程*

</div>
```

---

### 方案 4: GitHub + Bilibili 双托管（推荐给你的最佳方案）

```markdown
## 🎬 效果演示

<div align="center">

### 快速预览（30秒）

https://github.com/op7418/NanoBanana-PPT-Skills/assets/YOUR_USER_ID/demo-short.mp4

### 完整教程

**🎥 [观看完整演示视频（Bilibili 5分钟）](https://www.bilibili.com/video/BVXXXXXXX)** - 包含详细功能讲解

**🌍 [Watch Full Demo (YouTube 5min)](https://youtube.com/watch?v=XXXXXXXXX)** - English subtitles available

</div>

---
```

---

### 方案 5: Cloudinary 托管

```markdown
## 🎬 效果演示

<div align="center">

<video
  src="https://res.cloudinary.com/YOUR_CLOUD_NAME/video/upload/v1234567890/demo.mp4"
  width="800"
  controls
  loop
  muted
  poster="https://res.cloudinary.com/YOUR_CLOUD_NAME/image/upload/v1234567890/demo-poster.jpg">
</video>

*AI 自动生成 PPT 并添加流畅转场动画*

</div>
```

---

### 方案 6: 多种演示方式组合（完整版）

```markdown
## 🎬 效果演示

<div align="center">

### 🎨 渐变毛玻璃风格演示

![Gradient Glass Style Demo](demos/gradient-glass-demo.gif)

### 🎞️ 完整 PPT 生成流程

https://github.com/op7418/NanoBanana-PPT-Skills/assets/YOUR_USER_ID/full-demo.mp4

### 📺 详细教程视频

| 平台 | 链接 | 时长 | 说明 |
|------|------|------|------|
| 🎬 **Bilibili** | [观看教程](https://bilibili.com/video/BVXXXX) | 5:30 | 中文讲解，包含安装和使用 |
| 🌏 **YouTube** | [Watch Tutorial](https://youtube.com/watch?v=XXXX) | 5:30 | English subtitles |

</div>

---
```

---

## 具体操作步骤

### 如果选择 GIF 方案：

1. **生成 GIF**（推荐 10-20 秒精华片段）：

```bash
cd /Users/guohao/Documents/code/ppt/ppt-generator

# 方法1：完整视频转 GIF（会很大）
ffmpeg -i outputs/20260112_135018_video/full_ppt_video.mp4 \
  -vf "fps=10,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  -loop 0 \
  demo.gif

# 方法2：截取前 20 秒（推荐）
ffmpeg -i outputs/20260112_135018_video/full_ppt_video.mp4 \
  -t 20 \
  -vf "fps=10,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  -loop 0 \
  demo.gif

# 方法3：超压缩版（如果文件太大）
ffmpeg -i outputs/20260112_135018_video/full_ppt_video.mp4 \
  -t 15 \
  -vf "fps=8,scale=600:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer" \
  -loop 0 \
  demo-compressed.gif
```

2. **检查文件大小**：
```bash
ls -lh demo.gif
# 建议控制在 5-10MB 以内
```

3. **放到仓库根目录**：
```bash
# 将 GIF 移动到仓库根目录
mv demo.gif /Users/guohao/Documents/code/ppt/ppt-generator/

# 添加到 git
git add demo.gif
```

### 如果选择 GitHub 视频方案：

1. **压缩视频**（必须 < 100MB）：

```bash
# 压缩到 1080p, 5Mbps 码率
ffmpeg -i outputs/20260112_135018_video/full_ppt_video.mp4 \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease" \
  -c:v libx264 -b:v 5M -maxrate 5M -bufsize 10M \
  -c:a aac -b:a 128k \
  demo-compressed.mp4

# 检查大小
ls -lh demo-compressed.mp4
```

2. **上传到 GitHub**：
   - 直接在 GitHub 仓库的 Issue 或 Pull Request 中拖拽视频上传
   - 复制生成的 URL（类似 `https://github.com/user/repo/assets/12345/video.mp4`）
   - 在 README 中使用这个 URL

### 如果选择 Bilibili 方案：

1. 录制完整演示（带讲解）
2. 上传到 Bilibili，设置封面
3. 复制视频链接（BV号）
4. 在 README 中使用

---

## 推荐的完整布局

```markdown
# NanoBanana PPT Skills

> 基于 AI 自动生成高质量 PPT 图片和视频的强大工具，支持智能转场和交互式播放

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)

**创作者**: [歸藏](https://github.com/op7418)

[功能特性](#-功能特性) • [效果演示](#-效果演示) • [一键安装](#-一键安装) • [使用指南](#-使用指南)

</div>

---

## 🎬 效果演示

<div align="center">

### 🎨 自动生成渐变毛玻璃风格 PPT

![Demo](demo.gif)

*从文档分析到转场视频，一键完成*

### 📺 完整教程

**🎥 [观看详细教程（Bilibili 5分钟）](https://bilibili.com/video/BVXXXX)** - 包含安装和使用说明

</div>

---

## 📖 简介

...
```

---

## 我的最终建议

**对于你的项目，推荐这样做：**

1. **立即行动**：
   - 生成一个 15-20 秒的 GIF 动图（展示核心功能）
   - 放在 README 开头，给用户第一印象

2. **后续增强**：
   - 录制一个 3-5 分钟的完整演示视频
   - 上传到 Bilibili（中文讲解）
   - 在 README 中提供链接

3. **README 结构**：
```
标题 + Badges
    ↓
导航链接（添加"效果演示"）
    ↓
🎬 效果演示（GIF 自动播放）
    ↓
完整教程链接（Bilibili/YouTube）
    ↓
简介
    ↓
其他内容...
```

需要我帮你执行具体操作吗？比如：
1. 生成优化的 GIF
2. 压缩视频到 < 100MB
3. 修改 README 添加演示区域
