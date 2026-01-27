# 快速使用指南

## 🚀 5分钟快速上手

### 步骤1: 设置API密钥

```bash
export GEMINI_API_KEY='your-google-ai-api-key'
```

**获取API密钥**: 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)

### 步骤2: 安装依赖

```bash
pip install google-genai pillow
```

### 步骤3: 准备文档

创建或准备一个markdown文档，例如 `my-document.md`：

```markdown
# 我的演示主题

## 第一部分：背景
这里是背景介绍...

## 第二部分：核心观点
- 观点1：...
- 观点2：...
- 观点3：...

## 第三部分：总结
关键发现和行动建议...
```

### 步骤4: 在Claude Code中使用

打开Claude Code，执行：

```
我想基于 my-document.md 生成一个5页的PPT，使用渐变毛玻璃卡片风格，2K分辨率。
```

Claude会自动：
1. 分析文档内容
2. 规划5页PPT的内容
3. 生成高质量图片
4. 创建HTML播放网页

### 步骤5: 查看结果

```bash
open outputs/TIMESTAMP/index.html
```

使用键盘操作：
- ← → : 切换页面
- ESC : 全屏模式
- 空格 : 自动播放

## 💡 使用技巧

### 技巧1: 选择合适的页数

- **5页**: 电梯演讲（5分钟）
- **5-10页**: 标准演示（10-15分钟）
- **10-15页**: 深入讲解（20-30分钟）
- **20-25页**: 完整培训（45-60分钟）

### 技巧2: 优化文档结构

**好的文档结构**:
```markdown
# 主标题

## 核心观点1
- 要点
- 要点
- 要点

## 核心观点2
[详细说明...]

## 总结
[关键结论...]
```

**不理想的结构**:
```markdown
# 标题
一大段没有分段的文字...
```

### 技巧3: 分辨率选择建议

| 用途 | 推荐分辨率 | 生成时间 | 文件大小 |
|------|------------|----------|----------|
| 日常演示 | 2K | ~30秒/页 | ~2MB/页 |
| 正式场合 | 2K | ~30秒/页 | ~2MB/页 |
| 打印输出 | 4K | ~60秒/页 | ~8MB/页 |
| 大屏展示 | 4K | ~60秒/页 | ~8MB/页 |

### 技巧4: 批量生成

如果需要生成多个版本：

```bash
# 5页精简版
python generate_ppt.py --plan plan_5.json --style styles/gradient-glass.md --resolution 2K --output outputs/v1-brief

# 15页详细版
python generate_ppt.py --plan plan_15.json --style styles/gradient-glass.md --resolution 2K --output outputs/v2-detailed
```

## 🎨 自定义风格

### 创建新风格

1. 复制现有风格文件：
```bash
cp styles/gradient-glass.md styles/my-style.md
```

2. 编辑风格定义：
```markdown
# 我的自定义风格

## 风格ID
my-custom-style

## 基础提示词模板
[修改为你的风格描述...]
```

3. 使用新风格：
```bash
python generate_ppt.py --plan plan.json --style styles/my-style.md
```

## 🔧 高级用法

### 手动调整提示词

1. 查看生成的提示词：
```bash
cat outputs/TIMESTAMP/prompts.json
```

2. 复制并修改想要调整的提示词

3. 创建新的规划文件并重新生成

### 混合页面类型

在JSON规划文件中自定义页面类型：

```json
{
  "slides": [
    {"page_type": "cover", "content": "..."},
    {"page_type": "content", "content": "..."},
    {"page_type": "data", "content": "..."},
    {"page_type": "content", "content": "..."}
  ]
}
```

### 并行生成

同时生成多个版本：

```bash
python generate_ppt.py --plan plan1.json --style styles/gradient-glass.md --output outputs/v1 &
python generate_ppt.py --plan plan2.json --style styles/gradient-glass.md --output outputs/v2 &
wait
echo "所有版本生成完成！"
```

## 📋 常见问题

### Q: 生成失败怎么办？

A: 检查以下几点：
1. API密钥是否正确设置
2. 网络连接是否正常
3. Python依赖是否完整安装
4. 查看详细错误信息

### Q: 可以生成中文内容吗？

A: 可以！Nano Banana Pro支持多语言，包括中文。

### Q: 生成需要多长时间？

A:
- 2K: 约30秒/页
- 4K: 约60秒/页
- 5页PPT大约需要2.5-5分钟

### Q: 如何导出为PDF？

A: 在浏览器中打开HTML播放器，使用"打印"功能：
1. 打开播放器
2. 按 Cmd+P (Mac) 或 Ctrl+P (Windows)
3. 选择"另存为PDF"

### Q: 可以修改已生成的PPT吗？

A: 可以通过以下方式：
1. 编辑JSON规划文件
2. 修改提示词
3. 重新运行生成脚本

### Q: 支持哪些文档格式？

A: 目前最佳支持Markdown格式，也可以使用纯文本。

## 📞 获取帮助

遇到问题？
1. 查看README.md
2. 查看ppt-generator.md详细文档
3. 在Claude Code中使用 `/help`

## 🎯 最佳实践清单

✅ 使用清晰的标题和分段
✅ 每页内容不超过3-5个要点
✅ 选择合适的页数范围
✅ 日常使用2K分辨率
✅ 保存原始JSON规划文件
✅ 定期检查API配额使用情况
✅ 测试播放器在不同浏览器的表现

---

**开始创作吧！** 🚀
