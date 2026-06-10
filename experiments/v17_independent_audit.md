# v17 独立审计：顶刊标准下的论文诊断

**基准**: 不是执行审稿人清单，而是我自己按 JFE/JPE/AER 标准审读 v15.1 + v16 后的独立判断。
**原则**: 审稿人说的对的我采纳，审稿人遗漏的我补上，审稿人说错的我反驳。

---

## 一、论文的核心问题（审稿人没看透的）

### 1. 论文有两条叙事线在打架

**叙事A（M2 quadratic）**：FOMC 语言对 target shock 的响应是凸的——鹰派信号被放大，鸽派信号被压制。这是"鸽派不对称"。

**叙事B（M4 direction-interaction）**：鹰派会议和鸽派会议上，target 和 path shock 对语言的影响不同。这是"regime-dependent asymmetry"。

这两条叙事**不是同一个故事**。M2 的凸性来自 target²，是一个连续的非线性；M4 的不对称来自离散的 direction 交互，是一个分段线性。论文试图让两者共存，但：

- 摘要用 M4
- 引言用 M2
- §3.1 先写 M4 再写 M2 再混着解释
- §4.1 说 M4 是主模型但 Table 2 报的是 M2 的 progressive controls
- §4.3 (LM 对比) 完全基于 M2
- §4.5 (DXY) 用 M2
- §5.7 才说 M4 赢了

**顶刊读者在读完摘要后，应该能在 30 秒内回答"这篇论文的核心发现是什么"。当前版本做不到。**

**我的判断**：M4 是正确的首选模型（J-test 支持、wild bootstrap 通过、DM OOS 显著）。M2 应该降级为 M4 的一个特例/近似。具体来说：

- M4 的 target×direction 在 hike 时 = β₁ + β₄，在 cut 时 = β₁ − β₄。如果 β₄ > 0，鹰派会议的 target 斜率更大——这就是"鸽派不对称"的 regime-interaction 版本
- M2 的 target² 是 M4 的二阶 Taylor 近似（当 direction ≈ sign(target) 时），但 M2 丢失了 path×direction 这个独立通道
- **M2 应该只出现在 §5 Robustness 里**，不应该在引言和 §3 占据主要篇幅

### 2. "Credibility maintenance" 叙事是论文最大的软肋

论文把凸性解释为"美联储害怕失去抗通胀信誉，所以压制鸽派语言"。这个叙事：

- **没有理论推导**：§3.1 para 44 说"credibility floor S ≥ S_floor 会产生凸性"，但没有推导 FOC。审稿人指出这一点是对的
- **与 M4 不兼容**：M4 的不对称是离散的（hike vs cut），不是连续的凸性。credibility floor 叙事预测的是连续凸性（target²），不是分段线性
- **有更简单的替代解释**：鹰派会议本身就是鹰派信号——美联储加息时自然会说更鹰派的话，这不是"信誉维护"，是"言行一致"。论文没有排除这个 null

**我的判断**：与其修补 credibility maintenance 的微观基础（审稿人建议推导 FOC），不如**换叙事**。更诚实的做法是：

1. 承认 M4 是 reduced-form，不需要 structural 叙事
2. 把"鸽派不对称"从"信誉维护"降级为"一个与信誉维护一致的 reduced-form 发现"
3. 在 Discussion 里列出三种等价解释：(a) credibility maintenance, (b) asymmetric reaction function, (c) tone saturation，然后说明现有数据无法区分——这比强行推销一个叙事更顶刊

### 3. 2014-2019 安慰剂结果其实削弱了论文的核心主张

v16 加了 2014-2019 子样本（N=48），target² t=1.42 不显著。论文解释为"不对称集中在 QE 和 COVID 时期，不是 ZLB 本身"。

但这恰恰说明：**不是 ZLB 产生了不对称，而是危机产生了不对称**。ZLB 只是危机的伴随特征。论文的标题是 "at the Zero Lower Bound"，但数据说的是 "during crises"。这是一个根本性的 identification 问题。

**我的判断**：不要回避这个发现，而是**拥抱它**。把论文的核心主张从"ZLB 产生不对称"改为"危机时期的沟通压力产生不对称，ZLB 是危机的代理变量"。这实际上是一个更强的故事——它解释了为什么 2014-2019（ZLB 但无危机）没有不对称。具体改法：

- 标题保留 ZLB（因为 ZLB 是最显著的制度特征），但引言和结论要明确说"不对称的驱动因素是危机沟通压力，不是零利率本身"
- §4.2 的 ZLB break 应该加一个讨论：break date 可能捕捉的是 2008 金融危机 + QE，不是 ZLB per se
- 加一个 Andrews (1993) unknown break test，看估计的 break date 是否真的是 2008 年 12 月

---

## 二、审稿人意见的逐条评估

### 审稿人说对了的（我采纳）

| # | 审稿人意见 | 我的判断 |
|---|-----------|---------|
| P0-1 | §4.4 重复 | ✅ 必须合并。v16 没修 |
| P0-2 | §5.7 重复 | ✅ v16 已修 |
| P0-3 | 半衰期 8.7 vs 3.2 | ✅ v16 已修 |
| P0-4 | 累积乘子 13.0 vs 5.3 | ✅ v16 已修 |
| P0-5 | 240 vs 168 字数 | ✅ v16 已修 |
| P0-6 | Gambacorta 重复 | ✅ v16 已修 |
| P0-7 | 缺 Hassan/Tadle/Eijffinger | ✅ v16 已修 |
| P0-8 | §3.1 标题与内容不匹配 | ✅ v16 改了标题但内容仍混乱 |
| P1-1 | 2014-2019 安慰剂 | ✅ v16 已加，但解释方向错了（见上） |
| P1-2 | Bauer-Swanson predictability | ✅ v16 已加 |
| P1-5 | M2/M4 叙事混乱 | ✅ 核心问题，v16 没修 |
| P1-6 | credibility floor 需推导 | ⚠️ 我不同意推导 FOC——应该换叙事（见上） |
| P1-10 | 220→131 样本缺口 | ✅ 必须解释 |
| P1-12 | Acosta 论文 vs 数据引用 | ✅ v16 已修 |

### 审稿人说错了的（我反驳）

| # | 审稿人意见 | 我的反驳 |
|---|-----------|---------|
| P1-6 建议推导 FOC | 推导一个 central bank loss function 的 FOC 来 justify β₃ > 0，这在 JFE/JPE 不可行——任何审稿人都会问"你的模型假设了凸调整成本，所以得到凸响应，这不是 tautology 吗？"。正确做法是**删掉 structural 叙事，改为 reduced-form** |
| P1-7 要求 M4 重估 DXY | DXY 用 M2 (target²) 已经显著（t=-2.44），用 M4 反而可能因为 N=109 估计 6 个参数而损失 power。M2 对 DXY 是更合适的模型——DXY 是连续变量，不需要离散 regime 交互。论文应该明确说"CB 用 M4，DXY 用 M2，因为 dependent variable 的性质不同" |
| P2-5 要求 Andrews unknown break | Andrews test 在 N=55 的 pre-ZLB 子样本里 power 极低，结果不可靠。Chow test at known date 是标准做法（Hansen 1997 robust version 已报告）。加 Andrews 是锦上添花不是必须 |
| P2-10 摘要缩到 150 词 | JFE 摘要可以到 200 词。198 词没问题，但内容需要重组——先说发现，再说模型 |

### 审稿人遗漏的（我补上）

1. **§4.3 LM 对比完全基于 M2，但论文说 M4 是主模型**。如果 M4 是主模型，LM 对比也应该用 M4。用 M2 做 LM 对比然后说 M4 是主模型，是自相矛盾的
2. **Table 2 的 progressive controls 是 M2 的，不是 M4 的**。论文说 M4 是主模型，但 Table 2 报的是 M2 的 6 列。M4 的 progressive controls 在哪？
3. **path×direction 的经济解释不够**。β₅ = -0.023 意味着鸽派会议上 path shock 使语言更鸽派——这和"信誉维护"叙事矛盾（信誉维护应该压制鸽派信号）。论文没有解释为什么 target 和 path 的不对称方向相反
4. **Gambacorta et al. (2024) 的 "164,622 communications from 169 institutions" 数字可能有误**。审稿人 P3-21 指出发表版是 26,933 documents from 26 central banks。v16 没修
5. **§6 Related Literature 有两个 "Fourth"**（para 133 和 134）。v16 没修
6. **Bauer-Swanson (2023) 的期刊**：审稿人 P3-18 说是 AER: Insights 5(4), 469-75。但 v16 仍写 AER 113(5), 1266-1310。这两个可能是不同的 Bauer-Swanson 论文——需要核实

---

## 三、v17 修改方案

### 结构重组（最重要的改动）

```
1. Introduction
   - 核心发现：M4 direction-interaction model
   - 鹰派信号放大、鸽派信号压制（用 M4 的斜率比，不用 target²）
   - ZLB break + 2014-2019 安慰剂（危机驱动，不是 ZLB per se）
   - LM 字典相反曲率（一段带过）
   - 贡献：3 点

2. Data
   - 2.1 Shocks (Acosta)
   - 2.2 Sentiment (CB + LM)
   - 2.3 Sample (统一命名：baseline N=131, extended N=164, ZLB+Post N=109)
   - 2.4 Summary Statistics

3. Methodology
   - 3.1 Direction-Interaction Model (M4) ← 主模型，完整推导
     - target×direction: dovish asymmetry channel
     - path×direction: forward guidance channel
     - M2 quadratic as second-order approximation (一段)
   - 3.2 Inference (HAC + permutation + wild bootstrap)
   - 3.3 Structural Break Test

4. Results
   - 4.1 Direction-Interaction Estimates (M4, Table 2 ← 重做，M4 的 progressive controls)
   - 4.2 Economic Significance (合并当前 §4.4 + §4.6)
     - 边际效应、字数换算、AR(2) 持续性
   - 4.3 The ZLB Structural Break
     - 加 2014-2019 讨论：危机 vs ZLB
   - 4.4 Cross-Asset Evidence (DXY, banks)
   - 4.5 Complementary Evidence: LM Dictionary (M2-based, 明确标注)

5. Robustness
   - 5.1 Quadratic Model (M2) ← 从 §3 降级到这里
   - 5.2 Alternative Shock Measures
   - 5.3 HAC Size Distortion
   - 5.4 Statement Length
   - 5.5 Subsample Stability (含 2014-2019)
   - 5.6 Alternative Sentiment Measures
   - 5.7 Specification Comparison (J-test, DM)
   - 5.8 Bauer-Swanson Predictability
   - 5.9 Path Shock Nonlinearity

6. Discussion (新节，替代当前 §6 Related Literature 中的理论讨论)
   - 6.1 What Drives the Asymmetry? (crisis vs ZLB)
   - 6.2 Three Equivalent Interpretations (credibility / reaction function / tone saturation)
   - 6.3 Policy Implications (Fed put, AIT)

7. Related Literature (精简，去掉理论讨论)

8. Conclusion
```

### 具体修改清单

**必须改（不改不能投）**

1. §3.1 重写：M4 为主，M2 一段带过
2. Table 2 重做：M4 的 progressive controls（6 列），不是 M2 的
3. §4.4 + §4.6 合并为一个 "Economic Significance"
4. 引言重写：用 M4 的语言（斜率比 2.4:1），不用 target² 的边际效应
5. §3.1 para 44：删掉 credibility floor / loss function 叙事，改为 "M4 is a reduced-form specification; the convexity is consistent with several interpretations discussed in §6"
6. 2014-2019 结果的解读：从"ZLB per se 不够"改为"crisis communication stress 驱动"
7. 220→131 样本缺口解释清楚
8. §6 两个 "Fourth" 修掉
9. Bauer-Swanson 期刊核实
10. Gambacorta 数字核实

**应该改**

11. 摘要重组：先说发现（M4 斜率比），再说模型，150-200 词
12. §4.5 DXY 用 M2 是合理的——加一句解释为什么 DXY 不用 M4
13. path×direction 的经济解释：不是"信誉维护"，是"forward guidance 替代效应"——鸽派会议上 path shock 更重要是因为利率已经到零，语言是唯一工具
14. 结论第一段：一句话说核心发现 + M4 是 preferred model
15. 加 Andrews unknown break test（作为 robustness）
16. Müller (2014) 加到参考文献

**可以不改**

17. CB 字典 87% 验证——这是 Correa et al. 的数字，借用来没问题
18. Bootstrap CI——有 p 值就够了，CI 是锦上添花
19. DXY 数据频率/窗口——加一个 footnote 就够

---

## 四、与 v16 参考文档的差异

v16 参考文档（专家改的版本）修了大部分"容易修"的问题，但在三个关键地方没动：

1. **M2/M4 叙事混乱**——v16 的 §3.1 仍然先写 M4 再写 M2 再混着解释
2. **Table 2 仍是 M2 的 progressive controls**——M4 没有自己的 controls 表
3. **Credibility floor 叙事**——v16 只改了 φ→λ，没改叙事逻辑

这三个是结构性问题，不是编辑能修的，需要重写。
