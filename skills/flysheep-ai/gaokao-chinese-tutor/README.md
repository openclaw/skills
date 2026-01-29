# 高考语文导师 (Gaokao Chinese Tutor)

一个用于 Claude Code 的 Agent Skill，模拟经验丰富的高三语文辅导老师，培养学生的语文素养、阅读理解能力和写作表达能力。

## 功能特点

- 📖 **全面覆盖**：现代文阅读、古诗词鉴赏、文言文、作文写作
- 🎨 **重文本解读**：引导学生回归文本，培养文本感知能力
- 📝 **规范表达**：教授语文术语和答题规范
- ✍️ **写作指导**：从审题立意到语言表达的全方位指导
- 💭 **语文思维**：培养"写了什么、怎么写、为何写"的思维模式

## 适用场景

当学生：
- 提出语文阅读理解问题
- 请求分析古诗词、文言文
- 需要作文审题、立意、修改指导
- 说"不知道怎么答"、"答不到点上"
- 需要语文答题方法和技巧

## 安装方法

从教育 Skills 集合安装：

```bash
# 克隆教育 Skills 集合仓库
git clone https://github.com/flysheep-ai/education-skills.git

# 安装本 Skill 到个人配置
cp -r education-skills/gaokao-chinese-tutor ~/.claude/skills/

# 或安装到项目配置（团队共享）
cp -r education-skills/gaokao-chinese-tutor .claude/skills/
```

## 使用方法

安装后，当你向 Claude 提出语文学习问题时，Skill 会自动激活：

```
# 示例提问
老师，这段话的赏析怎么写？

这首诗表达了什么情感？

这个文言文句子怎么翻译？

我的作文立意对不对？

这道阅读理解题我答不到点上...
```

## 教学特色

### 现代文阅读
- 引导整体感知 → 细读文本 → 分析手法 → 理解作用
- 提供概括题、赏析题、作用题、含义题的答题方法
- 强调文本依据，避免过度解读

### 古诗词鉴赏
- 形象分析、情感主旨、表现手法的系统指导
- 引导结合注释、背景、意象理解诗歌
- 规范"手法+内容+情感"的答题模式

### 文言文
- 实词推断、句子翻译、内容理解的方法
- 强调"信、达、雅"的翻译原则
- 关注特殊句式和关键词

### 作文写作
- 审题立意、结构布局、论据选择、语言表达全流程指导
- 提供议论文和记叙文的写作框架
- 强调语言规范和表达生动性

## 示例对话

**学生**：老师，这句话的含义我不太理解

**老师**：
```
好，咱们一起来看这句话。

你先完整地读一遍这段话，然后告诉我：
1. 这句话字面上说了什么？
2. 联系上下文，它可能暗示了什么？

不用想太多，说说你的第一感受。
```

## 贡献

欢迎贡献改进建议！

1. Fork [教育 Skills 集合仓库](https://github.com/flysheep-ai/education-skills)
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request

## 许可证

本 Skill 采用 MIT 许可证，详见仓库根目录的 [LICENSE](../LICENSE) 文件。

## 作者

[@flysheep-ai](https://github.com/flysheep-ai)

## 反馈

如果你在使用过程中遇到问题或有改进建议：
- [提交 Issue](https://github.com/flysheep-ai/education-skills/issues)
- [发起 Pull Request](https://github.com/flysheep-ai/education-skills/pulls)
- 在 [Discussions](https://github.com/flysheep-ai/education-skills/discussions) 讨论

---

**注意**：本 Skill 是教学辅助工具，不能替代系统的学习和练习。建议配合课本、笔记和老师指导使用。
