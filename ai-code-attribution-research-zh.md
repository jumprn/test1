# 团队 AI 代码占比统计方案调研（面向 Cursor / Claude Code）

## 1. 调研目标

你希望统计团队成员提交代码中「AI 生成/辅助」占比，并且重点关注：

- 是否支持 **Cursor** 与 **Claude Code**
- 是否有 **免费可用** 方案
- 能否按成员、仓库、PR、文件维度查看占比

---

## 2. 结论先行（TL;DR）

在“免费可用”的前提下，优先考虑：

1. **git-ai（开源）**：更偏“底座”，跨工具追踪能力强，适合做长期标准化。  
2. **AgentBlame（开源）**：落地快，GitHub PR 可视化更直接，适合先跑试点。  
3. **AI Commit Tracker（VS Code 扩展）**：成本最低，但统计能力相对轻量，适合小团队快速起步。

> 对照组（非免费）：  
> - Cursor 官方 AI Code Tracking / Analytics API（企业版能力）  
> - Claude Code Analytics + Contribution Metrics（Team/Enterprise）

---

## 3. 候选方案横向对比

| 方案 | 免费情况 | Cursor 支持 | Claude Code 支持 | 统计粒度 | 技术路线 | 优势 | 局限 |
|---|---|---|---|---|---|---|---|
| **git-ai** | 开源免费（Apache-2.0） | 支持 | 支持 | 行级、提交级，可扩展到成员/仓库 | 通过 agent hook + Git Notes 做归因 | 跨工具统一、可离线、本地优先、标准化潜力高 | 初始接入和内部报表建设需要工程投入 |
| **AgentBlame** | 开源免费（Apache-2.0） | 支持 | 支持 | 行级、文件级、PR级、贡献者统计 | 采集编辑归因并在 GitHub 展示 | 上手快，PR 上直接看到 AI 占比 | 对浏览器扩展与 CLI 依赖较强，企业审计需评估 |
| **AI Commit Tracker（VS Code）** | 免费（开源扩展） | 间接支持（Cursor 兼容多数 VS Code 扩展） | 非原生 | 以提交标记为主（是否受 AI 影响） | 扩展记录接受建议并写入 commit footer | 部署最简单，适合低成本起步 | 精细度有限，不是严格行级占比 |
| **Cursor 官方 Analytics/AI Tracking API** | 企业版能力（非免费） | 原生 | 否 | 成员/团队/提交（取决接口） | 官方埋点与 API | 精度和产品整合度高 | 需企业版预算，不符合“纯免费”目标 |
| **Claude Code Analytics + Contribution Metrics** | Team/Enterprise（非免费） | 否 | 原生 | 成员/PR/代码行（保守口径） | 官方 GitHub 集成与后台统计 | 管理后台完善，适合管理层查看 | 非免费；需 GitHub App 与组织级配置 |

---

## 4. 各方案技术说明（重点看免费方案）

### 4.1 git-ai（推荐指数：★★★★★）

**适合场景**
- 想建立长期统一标准（不绑定单一 IDE/Agent）
- 希望未来可接入内部 BI 看板

**核心能力**
- 追踪 AI 代码到行级，并关联 agent/model/prompt 元信息
- 支持 Cursor 与 Claude Code 的 hook 集成
- 使用 Git Notes 记录归因，尽量减少对正常 Git 流程干扰

**落地成本**
- 中等：需要统一安装、配置 hook、以及做统计脚本/报表

**统计建议口径**
- AI 新增行占比 = AI 归因新增行 / 总新增行
- AI 变更占比 = AI 归因变更行 / 总变更行（新增+删除）
- 人均 AI 辅助占比 = 成员 AI 归因新增行 / 成员总新增行

---

### 4.2 AgentBlame（推荐指数：★★★★☆）

**适合场景**
- 先做 PoC，想在 PR 页面直观看效果
- 团队主要在 GitHub 协作

**核心能力**
- 在 GitHub PR 视图展示 AI 标记和比例
- 支持 Cursor / Claude Code 编辑归因
- 可查看贡献者维度趋势

**落地成本**
- 低~中：CLI + 浏览器扩展 + 仓库初始化

**注意事项**
- 依赖浏览器扩展的团队，需要提前过安全与合规评审

---

### 4.3 AI Commit Tracker（推荐指数：★★★☆☆）

**适合场景**
- 快速试点、预算为 0、只需要“是否被 AI 影响”的可见性

**核心能力**
- 记录 AI 建议接受情况，并在 commit 写入 AI 影响标记

**落地成本**
- 低：按扩展部署即可

**主要短板**
- 粒度偏粗，不适合做严格“行级 AI 占比”考核

---

## 5. 对照组：官方能力（非免费）

### 5.1 Cursor 官方 Analytics / AI Code Tracking API

- 面向团队/企业管理，支持 AI 编辑与 Tab 使用等分析能力  
- 优点是精度与产品一致性较高  
- 缺点是企业版门槛，无法满足“免费”约束

### 5.2 Claude Code Analytics + Contribution Metrics

- Team/Enterprise 可用，支持 GitHub 集成后查看贡献指标  
- 指标口径通常较保守（只计高置信度 AI 参与）  
- 同样不属于免费方案

---

## 6. 推荐选型策略

## 方案 A（最稳妥免费方案）

**git-ai + 简单内部报表脚本**

- 为什么：跨 Cursor/Claude Code 一致、可持续
- 适合：希望后续形成组织标准的研发团队

## 方案 B（最快试点方案）

**AgentBlame（CLI + GitHub 扩展）**

- 为什么：PR 页面可视化直观、试点反馈快
- 适合：先验证团队接受度，再决定是否平台化

## 方案 C（轻量过渡方案）

**AI Commit Tracker**

- 为什么：几乎零改造
- 适合：先建立“AI 参与透明度”，后续再升级行级统计

---

## 7. 2 周 PoC 执行模板（可直接照搬）

### Week 1：接入与样本采集

1. 选 1~2 个仓库 + 8~15 名开发者试点  
2. 安装并配置（优先 git-ai 或 AgentBlame）  
3. 统一统计窗口（例如按日汇总，观察 7 天）

### Week 2：指标验证与复盘

1. 输出 4 个核心指标：
   - 团队 AI 新增行占比
   - 成员 AI 新增行占比分布（P50/P90）
   - PR 维度 AI 占比
   - 人工抽样准确率（随机抽查 30~50 段）
2. 评估误差来源（复制粘贴、重构改写、非标准流程提交）
3. 给出是否全员推广结论

---

## 8. 风险与治理建议

1. **不要把 AI 占比直接作为绩效指标**  
   该指标更适合作为过程透明度和工程效率观察项。

2. **先统一口径再比较团队**  
   明确“新增行 vs 变更行”“是否包含测试代码”“是否按 squash 后统计”。

3. **结合质量指标一起看**  
   建议配套缺陷率、回滚率、PR review 通过率，避免“只追求占比”。

4. **注意隐私与合规**  
   若记录 prompt 或上下文，需要提前确认数据边界与保留策略。

---

## 9. 最终建议（给决策者）

- 如果你要的是“**免费 + 可持续 + 跨 Cursor/Claude**”，首选 **git-ai**。  
- 如果你要的是“**最快看到效果**”，首选 **AgentBlame**。  
- 官方能力（Cursor/Claude）适合预算充足且希望统一管理后台的团队，可作为后续升级路线，而不是第一步。

---

## 10. 信息来源（公开文档/项目主页）

- Cursor Docs（Extensions、Analytics、AI Code Tracking API、Pricing）
- Claude Code Docs（Analytics、Contribution Metrics、Analytics API）
- git-ai 项目与文档
- AgentBlame 项目与文档
- AI Commit Tracker 项目页

