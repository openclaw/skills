# API 密钥管理规范

## 📋 当前配置

### API 存储位置

所有 API 密钥现在统一存储在：

```
📁 ppt-generator/.env
```

### ✅ 安全验证

- ✅ `.env` 文件已创建
- ✅ 已被 `.gitignore` 保护（第15行规则）
- ✅ 不会被提交到 Git
- ✅ `run.sh` 可以正确加载

### 🎯 使用方法

**无需任何额外配置！** 直接使用即可：

```bash
./run.sh --plan slides_plan.json --style styles/gradient-glass.md --resolution 2K
```

输出显示：
```
📌 从 .env 文件加载API密钥
```

---

## 🔐 API 管理规范

### 1️⃣ 添加新的 API 密钥

编辑 `.env` 文件：

```bash
# 使用编辑器打开
nano .env

# 或使用 VS Code
code .env
```

按照以下格式添加：

```bash
# API 名称说明
# 用途：描述这个 API 的用途
# 获取地址：https://...
API_NAME=your-api-key-here
```

**示例**：

```bash
# OpenAI API
# 用途：未来可能用于文档分析
# 获取地址：https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

### 2️⃣ 在代码中使用 API 密钥

**❌ 错误做法**（硬编码）：

```python
# 绝对不要这样做！
api_key = "AIzaSyAfHE4vctPhMF2mVn96aEZZp8WuURlaGpM"
```

**✅ 正确做法**（从环境变量读取）：

```python
import os

# 从环境变量读取
api_key = os.environ.get("GEMINI_API_KEY")

# 或带默认值
api_key = os.getenv("GEMINI_API_KEY", "")

# 检查是否存在
if not api_key:
    raise ValueError("未找到 GEMINI_API_KEY 环境变量")
```

### 3️⃣ 环境变量加载优先级

`run.sh` 的加载逻辑：

```
1. 系统环境变量（~/.zshrc 等）
   ↓ 如果没有
2. .env 文件
   ↓ 如果都没有
3. 报错提示用户配置
```

这意味着：
- ✅ CI/CD 环境可以使用系统环境变量
- ✅ 本地开发使用 .env 文件
- ✅ 灵活切换不同环境的密钥

### 4️⃣ 多环境管理

如果需要管理多个环境（开发/测试/生产）：

```bash
# 开发环境
.env.development

# 测试环境
.env.test

# 生产环境
.env.production
```

使用时指定：

```bash
# 复制对应环境的配置
cp .env.development .env

# 或使用符号链接
ln -sf .env.development .env
```

---

## 📝 .env 文件结构

### 当前结构

```bash
.env
├─ [注释区域]
│  ├─ 安全提醒
│  ├─ 使用说明
│  └─ 加载优先级说明
│
├─ [主要 API 密钥]
│  └─ GEMINI_API_KEY (已配置)
│
├─ [备用 API 密钥]
│  ├─ OPENAI_API_KEY (注释状态)
│  ├─ ANTHROPIC_API_KEY (注释状态)
│  └─ STABILITY_API_KEY (注释状态)
│
└─ [项目配置]
   ├─ DEFAULT_RESOLUTION (注释状态)
   ├─ DEFAULT_STYLE (注释状态)
   └─ OUTPUT_DIR (注释状态)
```

### 字段说明

| 变量名 | 状态 | 用途 | 获取地址 |
|--------|------|------|----------|
| `GEMINI_API_KEY` | ✅ 已配置 | Nano Banana Pro 图像生成 | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `OPENAI_API_KEY` | 💤 预留 | 未来可能用于文档分析 | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `ANTHROPIC_API_KEY` | 💤 预留 | 未来可能用于Claude API | [Anthropic Console](https://console.anthropic.com/) |
| `STABILITY_API_KEY` | 💤 预留 | 未来可能用于其他图像模型 | [Stability AI](https://platform.stability.ai/) |

---

## 🚨 安全检查清单

### 开发时

- [ ] 从不在代码中硬编码 API 密钥
- [ ] 使用 `os.environ.get()` 或 `os.getenv()` 读取
- [ ] 添加密钥缺失时的错误提示
- [ ] 在函数/类初始化时读取，不要每次请求都读

### 提交前

- [ ] 运行 `git status` 确认 .env 不在列表中
- [ ] 运行 `grep -r "AIzaSy" --exclude-dir=.git .` 无输出
- [ ] 检查 `.gitignore` 包含 `.env`
- [ ] 代码中无任何硬编码的密钥

### 分享项目时

- [ ] 提供 `.env.example` 作为模板
- [ ] 在 README 中说明如何配置
- [ ] 不要通过聊天/邮件发送 .env 文件
- [ ] 建议用户使用自己的 API 密钥

---

## 💡 最佳实践

### 1. 密钥轮换

定期更新 API 密钥（建议 3-6 个月）：

```bash
# 1. 在 API 平台生成新密钥
# 2. 更新 .env 文件
# 3. 测试功能正常
# 4. 撤销旧密钥
```

### 2. 密钥权限

为不同用途创建不同的 API 密钥：

```bash
# 开发用（限制配额）
GEMINI_API_KEY_DEV=...

# 生产用（完整权限）
GEMINI_API_KEY_PROD=...
```

### 3. 错误处理

代码中添加友好的错误提示：

```python
import os
import sys

def get_api_key(key_name):
    """安全获取 API 密钥"""
    api_key = os.getenv(key_name)

    if not api_key:
        print(f"❌ 错误: 未找到 {key_name} 环境变量")
        print("")
        print("请配置 API 密钥：")
        print("1. 编辑 .env 文件")
        print("2. 添加：{key_name}=your-key")
        print("3. 保存并重新运行")
        sys.exit(1)

    return api_key

# 使用
gemini_key = get_api_key("GEMINI_API_KEY")
```

### 4. 日志安全

不要在日志中输出完整密钥：

```python
# ❌ 危险
print(f"Using API key: {api_key}")

# ✅ 安全
print(f"Using API key: {api_key[:8]}...{api_key[-4:]}")
# 输出: Using API key: AIzaSyAf...GpM
```

---

## 🔄 迁移指南

### 从系统环境变量迁移到 .env

如果您之前在 `~/.zshrc` 中配置了密钥：

**步骤1**: 从 .zshrc 删除

```bash
# 编辑配置文件
nano ~/.zshrc

# 删除这一行
export GEMINI_API_KEY="..."

# 重新加载
source ~/.zshrc
```

**步骤2**: 添加到 .env

```bash
# .env 文件已包含密钥，无需额外操作
```

**步骤3**: 测试

```bash
./run.sh --help
# 应该显示：📌 从 .env 文件加载API密钥
```

### 从 .env 迁移到系统环境变量

如果您想使用系统环境变量（跨项目共享）：

```bash
# 1. 复制 .env 中的密钥
cat .env | grep GEMINI_API_KEY

# 2. 添加到 .zshrc
echo 'export GEMINI_API_KEY="..."' >> ~/.zshrc

# 3. 重新加载
source ~/.zshrc

# 4. 测试
./run.sh --help
# 应该显示：✅ 使用系统环境变量中的API密钥
```

---

## 📚 相关文档

- **SECURITY.md** - 完整的安全指南
- **ENV_SETUP.md** - 环境变量配置详解
- **.env.example** - 配置模板
- **README.md** - 项目使用说明

---

## 🆘 常见问题

### Q: .env 文件在哪里？

A: 在项目根目录 `ppt-generator/.env`

### Q: 如何查看我的 API 密钥？

A:
```bash
cat .env | grep GEMINI_API_KEY
```

### Q: 可以提交 .env 文件吗？

A: **绝对不可以！** .env 文件包含敏感信息，已被 .gitignore 保护。

### Q: 团队协作时如何共享配置？

A:
1. 提交 `.env.example` 模板
2. 团队成员复制为 `.env`
3. 各自填入自己的 API 密钥

### Q: 如何知道密钥是从哪里加载的？

A: 运行任何命令时查看输出：
- `✅ 使用系统环境变量中的API密钥` - 从系统加载
- `📌 从 .env 文件加载API密钥` - 从 .env 加载

---

## ✅ 总结

### 当前配置

✅ **API 密钥统一管理**
- 存储位置：`ppt-generator/.env`
- 安全保护：`.gitignore` 规则
- 自动加载：`run.sh` 脚本

✅ **开发规范**
- 不在代码中硬编码
- 使用 `os.getenv()` 读取
- 添加错误处理
- 日志中不输出完整密钥

✅ **安全保证**
- .env 不会提交到 Git
- .env.example 作为模板
- 定期轮换密钥
- 不同环境使用不同密钥

### 立即可用

现在您可以直接开始迭代功能，所有 API 配置都已就绪！

```bash
# 直接使用
./run.sh --plan your_plan.json --style styles/gradient-glass.md
```

---

**创建日期**: 2026-01-11
**最后更新**: 2026-01-11
**创作者**: 歸藏
