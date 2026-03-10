# 补充调研：Claude Code（免订阅）+ 第三方大模型 API 方案

> 文档定位：在终版选型文档基础上的专项补充研究  
> 目标：回答“**Claude Code 不买订阅，只走 API**”是否可行，以及如何与 **GPT / Gemini / GLM / MiniMax** 等第三方模型 API 搭配  
> 时间点：基于 2026-03 可公开获取资料  
> 重要结论先行：  
> **Claude Code 免订阅是官方支持的；但把 GPT / Gemini / GLM / MiniMax 直接当 Claude Code 主模型，官方公开口径并不支持。**

---

## 1. 本文要回答的问题

在此前终版文档中，我们已经比较了：
- 工具层
- 模型层
- 个人/团队模式
- 成本与治理

但还缺少一个单独值得拿出来讲的方案：

> **Claude Code（免订阅、按 API 付费）+ 第三方大模型 API**

这个方案常被误解为两种不同意思：

1. **意思 A：用 Claude Code，但不买 Claude Pro / Max / Team 订阅**
   - 只用 API key
   - 按 token 计费
   - 这是**官方支持**的

2. **意思 B：用 Claude Code 作为外壳，但底层主模型换成 GPT / Gemini / GLM / MiniMax**
   - 这是很多人直觉上会想做的事
   - 但根据当前官方公开口径，**Claude Code 的主模型仍是 Claude 家族**
   - 第三方模型更现实的接法，是作为 **MCP / 自定义工具 / 内部网关上的外部推理工具**

本文的目的，就是把这两层说清楚。

---

## 2. 关键结论（TL;DR）

### 2.1 官方明确可行的部分

Claude Code 在**免订阅**情况下可以通过以下方式使用：

- Anthropic API key（Claude Console）
- Amazon Bedrock
- Google Vertex AI
- Microsoft Foundry

这意味着：

> **Claude Code 可以完全不依赖 Claude 订阅，直接按 API 使用。**

### 2.2 官方公开口径下，不建议当成“已支持”的部分

根据 Claude Code 官方模型配置文档，当前公开支持的主模型别名是：

- `sonnet`
- `opus`
- `haiku`
- `sonnet[1m]`
- `opusplan`

也就是说：

> **Claude Code 当前公开支持的“主推理模型”仍然是 Claude 家族。**

因此：
- **GPT-5.3-Codex**
- **Gemini 3.1 Pro / Flash-Lite**
- **GLM-5 / GLM-5-Code**
- **MiniMax M2.5**

这些模型**不能按“官方支持的 Claude Code 主模型”来表述**。

### 2.3 那第三方模型 API 还能不能跟 Claude Code 搭配？

可以，但要换一种说法：

> **不是“Claude Code 直接切换底模”，而是“Claude Code 调用外部模型工具”。**

更准确的落地方式是：

- Claude Code 作为主 Agent / 主编排器
- 第三方模型通过：
  - MCP server
  - 自定义 HTTP 工具
  - 内部 AI gateway
  暴露成“外部能力”

这时 Claude Code 仍然是核心 agent，第三方模型是：
- 第二视角
- 批量任务引擎
- 中文增强引擎
- 低成本副驾

---

## 3. 官方证据链：哪些是明确支持的，哪些不是

### 3.1 官方支持：Claude Code 免订阅 API 使用

官方认证与使用方式可分为：

- Claude.ai 订阅账户
- Claude Team / Enterprise
- Claude Console（API key）
- Amazon Bedrock
- Google Vertex AI
- Microsoft Foundry

这说明：

> **没有订阅也能用 Claude Code，只要你走 API / 云厂商认证。**

### 3.2 官方支持：Claude Code 通过 MCP 连接外部工具与 HTTP 服务

Claude Code 官方支持通过 MCP 连接：

- Remote HTTP servers
- Remote SSE servers
- Local stdio servers

也支持自定义工具，通过外部 HTTP API 获取结果。

这说明：

> Claude Code 可以官方支持地调用“外部 API 工具”，  
> 但这不等于它官方支持把外部模型当作主推理模型。

### 3.3 官方不支持为“主模型”的部分

Claude Code 官方模型配置文档中，公开给出的模型别名仍为 Claude 家族：

- sonnet
- opus
- haiku
- sonnet[1m]
- opusplan

没有官方文档表明可以直接把：
- GPT-5.3-Codex
- Gemini 3.1 Pro
- GLM-5-Code
- MiniMax M2.5

配置成 Claude Code 的主模型。

### 3.4 因此本次调研的严格结论

#### 可以说“官方支持”的
- Claude Code + Anthropic API（免订阅）
- Claude Code + Bedrock / Vertex / Foundry（仍是 Claude 模型）
- Claude Code + MCP / 自定义工具调用外部模型 API

#### 不应该说“官方支持”的
- Claude Code 直接切换为 GPT / Gemini / GLM / MiniMax 作为底模

---

## 4. Claude Code 免订阅方案的三种分型

### 4.1 方案 A：官方纯净型

**结构**
- Claude Code
- Anthropic API key
- 主模型：Claude Sonnet 4.6 / Opus 4.6

**特点**
- 官方路径最明确
- 风险最低
- 最适合严肃生产使用

**优点**
- 成本透明
- `/cost` 可直接看 token 使用
- 可接 Claude Console 的 workspace / spend limit / Usage API

**缺点**
- 仍然只有 Claude 模型
- 无法直接享受 GPT / Gemini / GLM / MiniMax 的差异化优势

### 4.2 方案 B：官方 + 外部工具型（推荐）

**结构**
- Claude Code 作为主 Agent
- Anthropic API 为主推理
- 第三方模型 API 通过 MCP / HTTP 工具接入

**特点**
- 核心能力仍稳定
- 第三方模型承担特定任务
- 最符合“可落地 + 不硬碰官方边界”的现实方案

**优点**
- 能把 Claude Code 的 agent 工作流保留下来
- 能按任务引入 GPT / Gemini / GLM / MiniMax 的优势

**缺点**
- 第三方模型不是主模型，而是工具
- 外部模型成本通常是**增量成本**，不一定能完全替代 Claude token 消耗

### 4.3 方案 C：兼容代理 / 网关伪装型（不推荐）

**结构**
- 通过兼容层把外部模型伪装成 Claude 可调用目标

**为什么不推荐**
- 官方没有公开保证
- 升级脆弱
- 出错难排查
- 预算、稳定性、兼容性风险高

**结论**
- 研究可讨论
- 生产不建议作为正式主方案

---

## 5. 第三方模型在 Claude Code 工作流里最合理的角色

### 5.1 GPT-5.3-Codex

**最合理角色**
- 工程第二视角
- 复杂长链路任务的补位分析
- 对 Claude 输出做工程性复核

**不适合**
- 做 Claude Code 的日常“即时副驾”

**原因**
- 首字延迟高
- 但工程 reasoning 强

### 5.2 Gemini 3.1 Pro

**最合理角色**
- 超长上下文分析器
- 长文档 / 大仓库阅读器

**不适合**
- 做日常高频交互工具内副驾

**原因**
- 长上下文强
- 交互体感不快

### 5.3 Gemini 3.1 Flash-Lite

**最合理角色**
- 低成本批量任务
- 抽取 / 草稿 / 低风险副任务

**不适合**
- 高风险复杂任务主决策

### 5.4 GLM-5-Code

**最合理角色**
- 中文业务开发增强
- 中文 PRD 转代码辅助
- 国内业务规则理解

**不适合**
- 直接替代 Claude Code 主 agent

### 5.5 MiniMax M2.5

**最合理角色**
- 批量生成
- 低成本流水任务
- 边缘任务分流

**不适合**
- 高风险关键重构主导

---

## 6. 成本测算方法：Claude Code API 模式 + 外部模型 API

### 6.1 成本测算原则

这里和前面文档最大的不同是：

> **当第三方模型通过 MCP / 外部工具方式接入 Claude Code 时，成本通常是“增量”而不是“替代”。**

原因：
- Claude Code 仍然要先理解任务、决定调用工具、整合结果
- 外部模型只是被调用
- 因此 Claude 的 token 成本不会按同等比例完全消失

### 6.2 本文的保守预算口径

为了避免低估预算，本次对 Claude Code + 外部模型 API 采用保守估算：

- **Claude 主模型成本按完整工作负载保留**
- 第三方模型成本按“外部调用增量”计算

也就是说：

`总成本 ≈ Claude Code 主成本 + 外部模型增量成本`

### 6.3 Claude 主成本基线

采用此前统一工作量基线：
- 平均工作量：16M input + 4.8M output / 月
- 以 Sonnet 4.6 计：
  - **$120 / 人 / 月**

如果 Claude Code 主模型改为 Opus，则：
- **$200 / 人 / 月**

---

## 7. 推荐方案：Claude Code（免订阅）+ 第三方模型 API

> 为了和前一个终版保持一致，这里也把每个方案控制为：  
> **Claude 主模型 + 1 个第三方外部模型**

### 7.1 方案 CC-A：Claude Code API 纯官方方案

**组合**
- Claude Code（免订阅）
- Anthropic API key
- 主模型：Claude Sonnet 4.6

**适合**
- 要求最稳定
- 要求最官方
- 不希望引入外部集成复杂度

**优点**
- 官方路径最清晰
- 成本可观测
- 与 Claude Console / workspace 治理一致

**缺点**
- 不利用第三方模型差异化优势

**平均工作量预算**
- **约 $120 / 人 / 月**

### 7.2 方案 CC-B：Claude Code + GPT-5.3-Codex（工程第二视角）

**组合**
- Claude Code（免订阅）
- 主模型：Claude Sonnet 4.6
- 外部工具模型：GPT-5.3-Codex

**建议用途**
- 仅把 GPT-5.3-Codex 用于：
  - 复杂工程 second opinion
  - 关键改动复核
  - 长链路工程方案校验

**建议增量比例**
- 外部调用预算按 Claude 工作量的 **10%** 估算

**成本**
- Claude 主成本：**$120**
- GPT-5.3-Codex 增量：
  - `0.1 * 95.2 = 9.52`
- **粗估总成本：约 $129.52 / 人 / 月**

**优点**
- 工程校验能力强
- 最适合复杂项目

**缺点**
- 成本上升
- 不适合高频小任务都调 GPT-5.3-Codex

### 7.3 方案 CC-C：Claude Code + Gemini 3.1 Flash-Lite（低成本副驾）

**组合**
- Claude Code（免订阅）
- 主模型：Claude Sonnet 4.6
- 外部工具模型：Gemini 3.1 Flash-Lite

**建议用途**
- 批量抽取
- 草稿生成
- 低风险辅助任务

**建议增量比例**
- 按 Claude 工作量的 **20%** 作为外部调用预算

**成本**
- Claude 主成本：**$120**
- Flash-Lite 增量：
  - `0.2 * 11.2 = 2.24`
- **粗估总成本：约 $122.24 / 人 / 月**

**优点**
- 是所有“Claude Code + 第三方模型”里最便宜的一类
- 很适合把批量轻任务从 Claude 主流程中分出去

**缺点**
- 不适合高风险复杂推理

### 7.4 方案 CC-D：Claude Code + GLM-5-Code（中文业务增强）

**组合**
- Claude Code（免订阅）
- 主模型：Claude Sonnet 4.6
- 外部工具模型：GLM-5-Code

**建议用途**
- 中文 PRD / 规则 / 中文注释
- 中文业务系统辅助分析

**建议增量比例**
- 外部调用预算按 Claude 工作量的 **20%**

**成本**
- Claude 主成本：**$120**
- GLM-5-Code 增量：
  - `0.2 * 43.2 = 8.64`
- **粗估总成本：约 $128.64 / 人 / 月**

**优点**
- 中文业务场景更友好

**缺点**
- 比 Flash-Lite 显著更贵
- 不是最低成本的旁路模型

### 7.5 方案 CC-E：Claude Code + MiniMax M2.5（低价批量分流）

**组合**
- Claude Code（免订阅）
- 主模型：Claude Sonnet 4.6
- 外部工具模型：MiniMax M2.5

**建议用途**
- 批量生成
- mock / 样板 / 低风险脚本

**建议增量比例**
- 外部调用预算按 Claude 工作量的 **20%**

**成本**
- Claude 主成本：**$120**
- MiniMax 增量：
  - `0.2 * 8.16 = 1.63`
- **粗估总成本：约 $121.63 / 人 / 月**

**优点**
- 增量预算最低
- 很适合边缘任务分流

**缺点**
- 对复杂任务帮助有限

---

## 8. 如何理解这些成本：为什么不是“更便宜就替代 Claude”

这是最重要的认识误区之一。

### 8.1 如果你在 Claude Code 里调用外部模型

Claude 仍然要：
- 理解你的任务
- 决定是否调用工具
- 读取工具结果
- 再综合输出

所以：
- 外部模型成本是**额外成本**
- 不是 1:1 替换 Claude 成本

### 8.2 真正能替代 Claude 主成本的方式

只有当你：
- 不在 Claude Code 会话里完成这部分任务
- 而是在外部工作流里单独跑这部分任务

才可能出现：
- Claude 成本下降
- 外部模型成本上升

但那已经不再是“Claude Code 作为统一主 agent”的体验了。

### 8.3 因此这类方案最适合怎么用

> **把 Claude Code 作为主 agent，第三方模型只承担“专项辅助能力”。**

这才是最符合官方能力边界、也最稳定的做法。

---

## 9. 个人模式与团队模式，Claude Code API 方案怎么选

### 9.1 个人模式推荐

#### 最稳方案
- **Claude Code + Anthropic API only**
- 约 **$120 / 人 / 月**

#### 最值得补位的方案
- **Claude Code + Gemini 3.1 Flash-Lite**
- 约 **$122.24 / 人 / 月**

为什么最推荐 Flash-Lite：
- 增量成本很低
- 对草稿/批量任务最划算
- 不会把复杂度和预算拉得太高

#### 中文业务增强方案
- **Claude Code + GLM-5-Code**
- 约 **$128.64 / 人 / 月**

#### 工程第二视角方案
- **Claude Code + GPT-5.3-Codex**
- 约 **$129.52 / 人 / 月**

### 9.2 团队模式推荐

如果是团队，又不想买 Claude Team 订阅，而是希望：
- 统一走 API
- 统一做 budget / workspace / usage

更推荐：

#### 团队推荐 A
- Claude Code + Anthropic API
- workspace / spend limit / Usage & Cost API

#### 团队推荐 B
- Claude Code + Anthropic API + Gemini 3.1 Flash-Lite
- 低成本副任务分流

#### 团队推荐 C
- Claude Code + Anthropic API + GLM-5-Code
- 中文业务增强

### 9.3 不推荐的表述方式

不建议在正式方案里写成：

> “Claude Code 支持 GPT / Gemini / GLM / MiniMax 作为底层主模型”

更严谨的写法应当是：

> “Claude Code 在免订阅 API 模式下，可通过 MCP / 自定义工具 / 内部网关调用第三方模型 API 作为辅助能力，但 Claude Code 主模型仍按官方支持的 Claude 家族来理解。”

---

## 10. 最终结论

### 10.1 一句话结论

> **Claude Code 免订阅是官方支持的；  
> Claude Code + 第三方模型 API 也是可落地的，但更准确的说法是“Claude 作为主 agent，第三方模型作为外部工具能力”。**

### 10.2 如果只推荐两套

#### 套餐 1：最稳
- Claude Code + Anthropic API
- **约 $120 / 人 / 月**

#### 套餐 2：最实用
- Claude Code + Anthropic API + Gemini 3.1 Flash-Lite
- **约 $122.24 / 人 / 月**

为什么我把 Flash-Lite 放在最推荐的第三方模型：
- 成本最低
- 增量预算最小
- 对日常分流任务最有效
- 比 GPT / GLM 更不容易把总预算推高

### 10.3 如果团队是中文业务

可优先评估：
- Claude Code + Anthropic API + GLM-5-Code
- **约 $128.64 / 人 / 月**

### 10.4 如果团队是复杂工程导向

可优先评估：
- Claude Code + Anthropic API + GPT-5.3-Codex
- **约 $129.52 / 人 / 月**

---

## 11. 与终版主文档的关系

本文建议作为：

- `终版_个人与团队模式_AI研发工具模型选型方案.md` 的补充附录

最适合在以下场景引用：

1. 你们决定不用 Claude Team 订阅，而统一走 API
2. 你们想保留 Claude Code 工作流，但引入第三方模型优势
3. 你们需要一个“**官方支持边界清晰**”的技术说明，避免方案写得过头
