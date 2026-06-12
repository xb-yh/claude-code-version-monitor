# Claude Code Version Monitor

监控 npm 包 `@anthropic-ai/claude-code` 的版本更新，并在发现新版本时通过飞书（Feishu / Lark）群机器人推送通知。

## 工作原理

1. 每天北京时间 09:00（UTC 01:00）通过 GitHub Actions 运行一次检查。
2. 请求 npm registry 获取 `@anthropic-ai/claude-code` 的最新版本。
3. 与仓库中的 `state.json` 记录的版本对比。
4. 如果发现新版本，调用飞书 webhook 发送通知，并更新 `state.json`。

## 快速开始

### 1. 创建飞书群机器人

1. 打开一个飞书群，点击「设置」→「群机器人」→「添加机器人」。
2. 选择「自定义机器人」，复制 Webhook 地址。
3. 建议启用「签名校验」或至少保管好该 URL，不要泄露到公开代码中。

### 2. 配置 GitHub Secret

进入本仓库的 **Settings → Secrets and variables → Actions → New repository secret**：

- Name: `FEISHU_WEBHOOK_URL`
- Value: 上一步复制的飞书 Webhook 地址

### 3. 启用 GitHub Actions

Actions 已经配置在 `.github/workflows/check-version.yml`，默认每天运行一次。你也可以在 Actions 页面手动触发 `workflow_dispatch` 进行测试。

### 4. 首次运行

首次运行时会创建 `state.json` 并记录当前最新版本，**不会发送通知**。从第二次运行开始，如果检测到版本变化，才会推送飞书消息。

## 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量后运行
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx"
python main.py
```

## 自定义

- 修改检查时间：编辑 `.github/workflows/check-version.yml` 中的 `cron` 表达式。
- 修改通知内容：编辑 `main.py` 中的 `send_feishu` 函数。
- 添加更多监控源：可以在 `main.py` 中扩展，例如同时监控 VS Code 插件版本或 Homebrew 版本。

## 许可证

MIT
