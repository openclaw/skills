# 高考通用技术导师 (Gaokao General Technology Tutor)

一个用于 Claude Code 的 Agent Skill，模拟经验丰富的高三通用技术辅导老师，培养学生的技术素养、设计思维和实践能力。

## 功能特点

- 🔧 **全模块覆盖**：技术与设计、结构与设计、流程与设计、系统与设计、控制与设计
- 💡 **设计思维培养**：从发现问题到优化方案的完整思维链
- 🏗️ **理论联系实践**：强调技术的实用性和可行性
- 📐 **技术评价能力**：从人、物、环境三要素评价设计
- 🎨 **创新意识激发**：鼓励学生的创造性思维

## 适用场景

当学生：
- 提出技术设计、结构优化问题
- 请求讲解技术原理、设计流程
- 需要绘制流程图、结构图
- 分析算法、编写简单程序
- 说"不知道怎么设计"、"不理解这个原理"

## 安装方法

从教育 Skills 集合安装：

```bash
# 克隆教育 Skills 集合仓库
git clone https://github.com/flysheep-ai/education-skills.git

# 安装本 Skill 到个人配置
cp -r education-skills/gaokao-general-tech-tutor ~/.claude/skills/

# 或安装到项目配置（团队共享）
cp -r education-skills/gaokao-general-tech-tutor .claude/skills/
```

## 使用方法

安装后，当你向 Claude 提出通用技术学习问题时，Skill 会自动激活：

```
# 示例提问
这个结构设计怎么才能更稳定？

请帮我分析这个流程图

这道技术设计题我不会做

怎么判断这个系统是开环还是闭环？

这个算法的流程图怎么画？
```

## 教学特色

### 技术与设计
- 设计的一般过程（发现问题→设计方案→制作原型→评估优化）
- 设计三要素（人、物、环境）
- 设计原则（创新性、实用性、经济性、美观性等）

### 结构与设计
- 结构类型（实体、框架、壳体）
- 结构稳定性分析（重心、支撑面、形状）
- 结构强度优化（材料、形状、连接方式）

### 流程与设计
- 流程图绘制规范
- 流程优化方法（减少环节、并行处理、合并同类）

### 系统与设计
- 系统组成（输入、处理、输出、反馈、控制）
- 系统优化（整体性、目的性、环境适应性）

### 控制与设计
- 开环控制与闭环控制的区别
- 控制系统分析（被控对象、控制目标、检测、控制器、执行器）

### 简单编程与算法
- 算法的流程图表示
- 顺序、选择、循环结构
- 简单算法设计

## 示例对话

**学生**：老师，怎么提高这个结构的稳定性？

**老师**：
```
好，咱们一起分析这个结构的稳定性。

先想想，影响结构稳定性的因素有哪些？
（提示：重心、支撑面、结构形状...）

你觉得这个结构在这几个方面怎么样？
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
