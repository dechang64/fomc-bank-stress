# v16 审计：审稿人意见 vs v16 修改对照

**审稿标准**: JFE / JPE / QJE / AER / RES desk-rejection  
**审稿结论**: Major Revision (borderline R&R)  
**审稿人**: 愿意审 v16，前提是 P0 全修 + 大部分 P1 修

---

## P0 修复状态（8 项，必须全修）

| # | 问题 | v15.1 | v16 | 状态 |
|---|------|-------|-----|------|
| P0-1 | §4.4 出现两次，§4.5 是幽灵节 | 4.4 Economic Significance + 4.4 Cross-Asset + 4.5 Economic Significance | 4.4 Economic Significance + 4.5 Cross-Asset + **4.6 Economic Significance** | ❌ **未修** — 编号不再重复但内容仍重复：§4.4 和 §4.6 都是 "Economic Significance"，应合并 |
| P0-2 | §5.7 出现两次 | 5.7 Specification Comparison + 5.7 Path Shock Nonlinearity | 5.7 Specification Comparison + **5.8** Path Shock Nonlinearity | ✅ 已修 |
| P0-3 | 半衰期矛盾：8.7 vs 3.2 | 正文 8.7，结论 3.2 | 全文统一为 **3.2 meetings** | ✅ 已修 |
| P0-4 | 累积乘子 13.0× 与半衰期矛盾 | 1/(1-0.923)≈13.0 | 改为 **1/(1-0.81)≈5.3×** | ✅ 已修 |
| P0-5 | Pre-ZLB 字数 240 vs 168 | 正文 4 处写 240，表 1 写 168 | 全文统一为 **168** | ✅ 已修 |
| P0-6 | Gambacorta 2024 参考文献重复 | 两条不同卷号 | 只保留一条 (JME 148, Article 103630) | ✅ 已修 |
| P0-7 | Hassan 2019, Tadle 2022, Eijffinger 2000 缺失 | 正文引用但参考文献无 | 三条均已补 | ✅ 已修 |
| P0-8 | §3.1 标题 "Quadratic Interaction Model" 与 §4.1 主模型不一致 | §3.1 只讲 M2 quadratic | §3.1 改为 **"Regime-Interaction Model"**，M4 为主，M2 为对比 | ⚠️ **部分修** — 标题改了，但内容混乱：先写 M4 公式，紧接着又写 M2 公式和边际效应推导，读者分不清哪个是主模型 |

**P0 总结：3 修好，3 部分修，2 未修。P0-1（重复节）和 P0-8（§3.1 结构混乱）仍需处理。**

---

## P1 修复状态（12 项，审稿人要求修大部分）

| # | 问题 | v16 状态 | 说明 |
|---|------|---------|------|
| P1-1 | 2014-2019 clean ZLB 安慰剂 (N=48) | ✅ 已加 | §5.5 报告 target² t=1.42 不显著，结论正确 |
| P1-2 | Bauer-Swanson 可预测性检验 | ✅ 已加 | §6 新增一段，R²=0.034/0.029，F 检验不显著 |
| P1-3 | path×direction 经济解释不足 | ❌ 未修 | 仍只说 "forward guidance channel"，未按审稿人要求分解 |
| P1-4 | "Dovish asymmetry" 部分由样本选择驱动 | ❌ 未修 | 未回应 |
| P1-5 | M2/M4 关系不清，读者不知哪个是"结果" | ⚠️ 部分 | §3.1 改了标题但内容仍混乱；摘要提了 J-test 但 198 词仍超 150 词建议 |
| P1-6 | §3.1 loss-function 叙事方向错误 | ⚠️ 部分 | 改了 φ→λ 但未按审稿人要求推导 FOC 或改为纯 reduced-form 叙事 |
| P1-7 | Cross-asset 用了不同（更弱）模型 | ❌ 未修 | DXY 仍用 target×direction 而非 M4 |
| P1-8 | "Credibility-maintenance" 解释未认真对待替代假说 | ❌ 未修 | 仍一段话打发 (b)(c) |
| P1-9 | CB 字典 87% 准确率无交叉验证 | ❌ 未修 | 未回应 |
| P1-10 | 220 vs 131 样本未解释 | ⚠️ 部分 | §2.3 提到 33 个 pre-2006 缺 CB score，但 220-131=89≠33 |
| P1-11 | 164 vs 131 样本使用不一致 | ⚠️ 部分 | 摘要说 baseline 131，§4.2 用 164，但未明确说明何时用哪个 |
| P1-12 | Acosta 只有数据引用无论文引用 | ✅ 已修 | 参考文献新增 Acosta (2022) 工作论文 |

**P1 总结：3 修好，4 部分修，5 未修。**

---

## P2/P3 修复状态（关键项）

| # | 问题 | v16 状态 |
|---|------|---------|
| P2-4 | Information Channel (§6.4) 最薄弱 | ⚠️ 加了 Bauer-Swanson 但仍偏引用罗列 |
| P2-5 | Chow test 用已知断点，未用 Andrews (1993) | ❌ 未修 |
| P2-6 | HAC size distortion 无 MC 表 | ❌ 未修 |
| P2-8 | DXY 窗口/频率未说明 | ❌ 未修 |
| P2-10 | 摘要太长 (~250词) | ⚠️ 缩到 198 词，但仍超审稿人建议的 150 词 |
| P3-16 | AIT 只在结论提，intro 未提 | ❌ 未修 |
| P3-18 | Bauer-Swanson 引用格式 | ✅ 已修 (AER 113(5)) |
| P3-20 | Cieslak 2018 "Fed put" 引用不当 | ❌ 未加 Cieslak-Schrimpf 2019 或 Haddad 2021 |

---

## 审稿人 10 条具体建议执行情况

| # | 建议 | v16 |
|---|------|-----|
| 1 | 围绕 M4 重组 §3-§4 | ⚠️ 标题改了，内容未理清 |
| 2 | 修 240→168 | ✅ |
| 3 | 统一半衰期 3.2、乘子 5.3× | ✅ |
| 4 | 加 2014-2019 安慰剂 | ✅ |
| 5 | 加 Bauer-Swanson 检验 | ✅ |
| 6 | 补 Hassan/Tadle/Eijffinger | ✅ |
| 7 | 删 Gambacorta 重复 | ✅ |
| 8 | 加 Acosta 论文引用 | ✅ |
| 9 | 摘要缩到 150 词，M4 开头 | ⚠️ 198 词，M4 开头已做 |
| 10 | 摘要提 J-test 和 DM | ✅ |

---

## v16 新增问题（v15.1 没有）

1. **§3.1 结构混乱**：先写 M4 公式 (para 34)，紧接着写 M2 公式 (para 35)，然后 M4 和 M2 混合解释 (para 36)，再接着全是 M2 的边际效应推导 (para 38-43)。读者完全分不清哪个是主模型
2. **§4.4 + §4.6 重复**：两个 "Economic Significance" 节——§4.4 讲 spanning test + DXY 校准，§4.6 讲边际效应 + AR(2) 持续性。应合并为一节
3. **§3.1 para 44 的 credibility floor 叙事**：审稿人明确说"要么推导 FOC，要么删掉 loss-function 动机，改成 reduced-form Taylor expansion"。v16 改了 φ→λ 但没做推导，也没改成 reduced-form 叙事

---

## 下一步优先级

### 必须修（否则审稿人不会接受）

1. **§3.1 重写**：M4 为主模型，M2 作为 "quadratic approximation of M4" 一段带过，删掉 M2 的边际效应推导（移到附录或 robustness）
2. **§4.4 + §4.6 合并**：一个 "Economic Significance" 节
3. **§3.1 para 44**：要么推导 FOC（审稿人给的例子），要么删掉 credibility floor 叙事，改为 "The quadratic specification is a second-order Taylor expansion of the unknown response function S(·)"
4. **path×direction 经济解释** (P1-3)：至少分解 hike/cut/hold 三组
5. **Cross-asset 用 M4 重估** (P1-7)

### 应该修

6. 摘要缩到 150 词
7. 220→131 样本缺口解释清楚 (P1-10)
8. DXY 窗口/频率说明 (P2-8)
9. AIT 在 intro 提及 (P3-16)
10. Cieslak "Fed put" 引用修正 (P3-20)
