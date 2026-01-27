# 飞书 × Clawdbot 桥接器

> 让你的 Clawdbot 智能体直接在飞书里对话——无需公网服务器、无需域名、无需备案。

---

## 它是怎么工作的？

想象三个角色：

```
飞书用户 ←→ 飞书云端 ←→ 桥接脚本（你的电脑上） ←→ Clawdbot 智能体
```

### 通俗解释

1. **飞书那边**：你在飞书开发者后台创建一个"自建应用"（机器人），飞书会给你一个 App ID 和 App Secret——这就像是机器人的"身份证"。

2. **桥接脚本**：一个运行在你电脑上的小程序。它用飞书提供的 **WebSocket 长连接**（而不是传统的 Webhook）来接收消息——这意味着：
   - ✅ 不需要公网 IP / 域名
   - ✅ 不需要 ngrok / frp 等内网穿透
   - ✅ 不需要 HTTPS 证书
   - 就像微信一样，你的客户端主动连上去，消息就推过来了

3. **Clawdbot**：桥接脚本收到飞书消息后，通过本地 WebSocket 转发给 Clawdbot Gateway。Clawdbot 调用 AI 模型生成回复，桥接脚本再把回复发回飞书。

### 保活机制

脚本通过 macOS 的 **launchd**（系统服务管理器）运行：
- 开机自动启动
- 崩溃自动重启
- 日志自动写入文件

就像把一个程序设成了"开机启动项"，但更可靠。

---

## 5 分钟上手

### 前提

- macOS（已安装 Clawdbot 并正常运行）
- Node.js ≥ 18
- Clawdbot Gateway 已启动（`clawdbot gateway status` 检查）

### 第一步：创建飞书机器人

1. 打开 [飞书开放平台](https://open.feishu.cn/app)，登录
2. 点击 **创建自建应用**
3. 填写应用名称（随意，比如 "My AI Assistant"）
4. 进入应用 → **添加应用能力** → 选择 **机器人**
5. 进入 **权限管理**，开通以下权限：
   - `im:message` — 获取与发送单聊、群聊消息
   - `im:message.group_at_msg` — 接收群聊中 @ 机器人的消息
   - `im:message.p2p_msg` — 接收机器人单聊消息
6. 进入 **事件与回调** → **事件配置**：
   - 添加事件：`接收消息 im.message.receive_v1`
   - 请求方式选择：**使用长连接接收事件**（这是关键！）
7. 发布应用（创建版本 → 申请上线）
8. 记下 **App ID** 和 **App Secret**（在"凭证与基础信息"页面）

### 第二步：安装依赖

```bash
cd feishu-bridge
npm install
```

### 第三步：配置凭证

把你的飞书 App Secret 保存到安全位置：

```bash
# 创建 secrets 目录
mkdir -p ~/.clawdbot/secrets

# 写入 secret（替换成你自己的）
echo "你的AppSecret" > ~/.clawdbot/secrets/feishu_app_secret

# 设置权限，只有自己能读
chmod 600 ~/.clawdbot/secrets/feishu_app_secret
```

### 第四步：测试运行

```bash
# 替换成你的 App ID
FEISHU_APP_ID=cli_xxxxxxxxx node bridge.mjs
```

在飞书里给机器人发一条消息，看到回复就说明成功了 🎉

### 第五步：设置开机自启（可选但推荐）

```bash
# 生成 launchd 服务配置（自动检测路径）
node setup-service.mjs

# 加载服务
launchctl load ~/Library/LaunchAgents/com.clawdbot.feishu-bridge.plist

# 查看状态
launchctl list | grep feishu
```

之后电脑重启也会自动连上。

---

## 文件说明

```
feishu-bridge/
├── bridge.mjs           # 核心桥接脚本（~200行）
├── setup-service.mjs    # 自动生成 launchd 保活配置
├── package.json         # 依赖声明
├── .env.example         # 环境变量示例
└── README.md            # 你正在读的这个
```

---

## 进阶

### 群聊行为

在群聊中，桥接器默认"低打扰"模式——只在以下情况回复：
- 被 @ 了
- 消息看起来是提问（以 `?` / `？` 结尾）
- 消息包含请求类动词（帮、请、分析、总结、写…）
- 用名字呼唤（bot、助手…，可在代码中自定义）

其他闲聊不会回复，避免刷屏。

### "正在思考…" 提示

如果 AI 回复超过 2.5 秒，会先发一条"正在思考…"，等回复生成后自动替换成完整内容。

### 日志位置

```
~/.clawdbot/logs/feishu-bridge.out.log   # 正常输出
~/.clawdbot/logs/feishu-bridge.err.log   # 错误日志
```

### 停止服务

```bash
launchctl unload ~/Library/LaunchAgents/com.clawdbot.feishu-bridge.plist
```

---

## 常见问题

**Q: 需要服务器吗？**
不需要。飞书的 WebSocket 长连接模式让你的电脑直接连到飞书云端，不需要公网暴露。

**Q: 电脑关机了怎么办？**
机器人会离线。重新开机后 launchd 会自动重启桥接服务。如需 24/7 在线，可以部署到一台常开的机器（比如 NAS、云服务器、甚至树莓派）。

**Q: 飞书免费版能用吗？**
可以。自建应用和机器人能力对所有飞书版本开放。

**Q: 能同时接 Telegram / 微信吗？**
可以。Clawdbot 原生支持 Telegram 等渠道，飞书桥接只是多加一个入口，互不影响。

---

## License

MIT
