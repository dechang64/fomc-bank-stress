
# 全面审计报告：v15.1 代码·数据·文献

## 一、代码与数据审计

### 1.1 数据来源与完整性

| 数据集 | 行数 | 时间范围 | 用途 | 状态 |
|--------|------|----------|------|------|
| fomc_master_v3.csv | 131 | 2006-01 ~ 2022-07 | 主回归数据 | ✅ |
| fomc_master_extended.csv | 164 | 1995-07 ~ 2022-07 | ZLB break test | ✅ |
| acosta_shocks.xlsx | 220 | 1995-02 ~ 2024+ | HF shocks | ✅ |
| fomc_cb_v2_scores.csv | 212 | 1994-05 ~ 2025-12 | CB字典评分 | ✅ |
| fomc_lm_full_scores.csv | 212 | 1994-05 ~ 2025-12 | LM字典评分 | ✅ |
| DXY.csv | 8315 | 1993-06 ~ 2025+ | DXY汇率 | ✅ |
| bank_events.csv | 216 | 1994-05 ~ 2025-12 | 银行CAR | ✅ |
| y9c_complete.csv | 1782行 | 2000-2025 | FR Y-9C | ✅ |

### 1.2 关键回归结果验证

| 回归 | 论文声称 | 复现结果 | 一致？ |
|------|----------|----------|--------|
| M4 target×direction (HAC) | t=3.73 | t=3.73 | ✅ |
| M4 path×direction (HAC) | t=-2.93 | t=-2.93 | ✅ |
| M4 R² | 0.18 | 0.1816 | ✅ |
| M2 target² (HAC, ZLB+Post) | t=2.77 | t=2.77 | ✅ |
| M2 R² | 0.07 | 0.0722 | ✅ |
| Chow test F | 14.12 | 14.12 | ✅ |
| DXY spanning CB t | -2.16 | -2.16 | ✅ |
| DXY R² 0.059→0.096 | ✓ | ✓ | ✅ |
| M2 + total_words R² | 0.514 | 0.5136 | ✅ |
| LM% target² (full sample, HAC) | t=-6.89 | t=-6.89 | ✅ |

### 1.3 🐛 发现的Bug

**Bug 1: 半衰期计算错误（严重）**
- 论文声称：3.2 meetings, 累积乘子 5.3×
- 正确值：8.6 meetings, 累积乘子 13.0×
- 原因：论文用AR(1)近似（ln(0.5)/ln(0.81)=3.3），但数据是AR(2)
- AR(2)特征根：0.923和-0.116，主导根0.923→半衰期=8.6
- 审稿人P0-3/P0-4指出了矛盾，但v16的"修复"（8.7→3.2）反而更错
- 8.7才是接近正确的数字（用实际数据的主导根0.923算出8.6）

**Bug 2: LM%对比的样本不一致**
- §4.3声称LM% target² t=-6.89（concave）
- 这个数字只在全样本(N=131)下成立
- ZLB+Post子样本(N=109)下target² t=-1.73，不显著
- 论文在§4.3没有说明用的是哪个样本，读者会以为是ZLB+Post

**Bug 3: 2014-2019 M2 target² t值**
- 论文声称t=1.42
- 复现得到t=0.92 (HAC lag=3)
- 差异可能来自不同的HAC lag选择，但论文没有说明

**Bug 4: Pre-ZLB M2 target²方向相反**
- Pre-ZLB (N=15): target² t=-4.38 (HC1)，显著为负
- 意味着Pre-ZLB时期CB响应是CONCAVE（与ZLB+Post的convex相反）
- 论文没有清楚报告这个发现

**Bug 5: 参考文献区混入正文**
- v16的References节最后3条(39-41)是正文段落，不是参考文献

### 1.4 样本定义问题

- 论文说"baseline sample of 131 FOMC meetings (2006-2022)"
- Acosta shocks从1995年开始，但CB字典评分从2006年才有
- 220个Acosta shocks → 131个有CB评分的会议
- ZLB+Post = Dec 2008+ = 109 meetings
- 论文没有清楚解释为什么2006年之前没有CB评分（是因为CB字典只覆盖2006+？）

## 二、文献审计

### 2.1 引用错误

| 引用 | 论文写的 | 正确的 | 严重度 |
|------|----------|--------|--------|
| Bauer & Swanson (2023) | AER 113(5), 1266-1310 | **AER 113(3), 664-700** | 高 — 卷期页全错 |
| Acosta (2022) | Working Paper | **IJCB 19(3), 49-97 (2023)** | 中 — 已发表 |
| Gambacorta et al. (2024) | "164,622 communications from 169 institutions" | 可能是26,933 documents from 26 banks | 高 — 数字可疑 |

### 2.2 必须引用但缺失的文献

1. **Haavio, Heikkinen, Jalasjoki, Kilponen, Paloviita & Vänni** — "Reading between the Lines: Uncovering Asymmetry in the Central Bank Loss Function," JMCB (2024/2025)
   - 直接相关：ECB损失函数不对称，通胀超目标时斜率3倍陡
   - 为我们的"credibility maintenance"叙事提供理论支撑

2. **Hubert & Portier (2025)** — "The Signaling Effects of Tightening and Easing Monetary Policy," BdF WP 999
   - 直接相关：欧元区MP不对称传导，easing surprises效果更强
   - 与我们的发现形成对比（我们：hawkish surprises效果更强）

3. **Gáti & Handlan** — "Reputation for Confidence," ECB WP
   - 直接相关：央行沟通中的信誉-信心动态
   - 为"credibility floor"叙事提供理论基础

4. **Camous & Matveev (2025)** — "Central Bank Strategic Communication and the Dynamics of Reputation"
   - 直接相关：央行策略性沟通与信誉动态

5. **Ehrmann (2024)** — "Trust in Central Banks," ECB WP 3006
   - 相关：央行信任度，与credibility叙事有关

### 2.3 应该引用的文献

6. **Fernández-Fuertes (2025)** — "Monetary Policy Shocks: A New Hope — LLMs and Central Bank Communication"
   - 最新LLM方法在MP shock识别中的应用

7. **Acosta, Brennan & Jacobson (2024)** — "Constructing HF monetary policy surprises from SOFR futures"
   - Acosta数据的更新版本

## 三、系统性诊断

### 3.1 论文的核心逻辑链

论文试图建立：HF shock → CB sentiment → asymmetric response → regime-dependent

但逻辑链有两个断裂：

**断裂1：direction变量的外生性**
- direction = +1(hike)/-1(cut)/0(hold) 来自FOMC决策
- FOMC决策本身是endogenous（基于经济状况）
- target×direction的系数可能捕获的是"经济状况×shock"而非"政策方向×shock"
- 论文没有控制经济状况（如失业率、通胀率）来隔离direction的独立效应

**断裂2：从M4到"credibility maintenance"的跳跃**
- M4发现：hike时target斜率大，cut时小
- 论文解释为"credibility maintenance"（央行维护信誉→hawkish信号被放大）
- 但同样可以解释为"information channel"（hike时Fed有更多private info→语言更确定）
- 或"attention allocation"（市场在hike时更关注→Fed语言更精确）
- 论文没有区分这些机制

### 3.2 与现有文献的定位

论文的核心贡献应该是：
1. **发现**：FOMC statement sentiment对MP shock的响应是regime-dependent的
2. **方法**：direction-interaction model比quadratic model更优（J-test证明）
3. **机制**：这种regime-dependence是ZLB/crisis时期的特殊现象

但论文目前的定位模糊——既想说"发现不对称"，又想说"解释不对称"，两个都没做透。

### 3.3 修改优先级

**必须修（否则不可投稿）**：
1. 半衰期：8.6 meetings, 累积乘子 13.0×（不是3.2和5.3）
2. Bauer & Swanson引用：AER 113(3), 664-700
3. Acosta引用：IJCB 19(3), 49-97 (2023)
4. LM%对比：明确说明用的是全样本(N=131)，不是ZLB+Post
5. §3.1重写：M4为主模型，M2降级为robustness
6. §4.4+§4.6合并
7. Pre-ZLB concave结果必须报告和讨论
8. 参考文献区删除混入的正文段落

**应该修**：
9. 加Haavio et al. (JMCB) 和 Hubert & Portier (BdF WP) 引用
10. direction外生性讨论（加经济状况控制）
11. 机制区分：credibility vs information vs attention
12. 2014-2019结果重新解读：不是"ZLB不够"，而是"crisis stress驱动"
13. 样本选择：解释为什么2006年之前没有CB评分
14. 摘要重组

**可以不改**：
15. DXY窗口/频率（加footnote即可）
16. Bootstrap CI（有p值够了）
17. Gambacorta数字（加footnote说明来源即可）
