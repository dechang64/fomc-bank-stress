# Editorial Review: Words Beyond the Rate v12.7
## 评审人：思怡（模拟 AEJ:Macro / JFE 审稿标准）
## 日期：2026-06-09

---

## 总评

**建议：Major Revision**

论文提出了一个有趣的发现——FOMC声明情绪对货币政策冲击的regime-dependent响应只在ZLB后才存在。这个ZLB结构性变化的发现有潜力，但当前版本在事实准确性、识别策略、经济解释和写作质量上存在多处硬伤，需要大修后重审。

---

## 一、事实错误（必须修正）

### 🔴 错误1：AR(2)系数错误
- **论文声称**：CB(t) = 0.81 × CB(t-1) + 0.25 × CB(t-2) + ε (R² = 0.81)
- **实际数据**：CB(t-1) = 0.807, CB(t-2) = **0.107** (非0.25), R² = **0.800** (非0.81)
- **严重性**：CB(t-2)系数差了2.3倍。这不是四舍五入误差，是事实错误。
- **修正**：用正确数字重算，或删除AR(2)细节只保留"高度持久"

### 🔴 错误2：CB score范围误导
- **论文声称**：CB score ranging from −0.092 to 0.064
- **实际数据**：ZLB+Post样本CB范围是 **−0.092 to −0.013**（全为负值！）
- **问题**：0.064来自Pre-ZLB（1995-2005），但论文在描述ZLB+Post分析时引用了这个范围
- **严重性**：审稿人会质疑"如果CB在ZLB后全为负，你的'hawkish during hikes'怎么成立？"
- **修正**：分era报告CB范围，并解释负值的含义

### 🟡 错误3：NW lag不一致
- **论文声称**：HAC with maxlags=4
- **实际数据**：N=55时NW lag应为3（int(55^(1/3))=3），N=131时应为5
- **修正**：用int(T^(1/3))自动选择lag，不要硬编码4

---

## 二、识别与因果推断问题（核心挑战）

### 🔴 问题1：Pre-ZLB null的regime分类不可靠
- Pre-ZLB的regime来自FRED日度利率变化的7天窗口
- 这个分类与master的regime在2006-2022重叠期只有**51.9%匹配率**
- 审稿人会问：Pre-ZLB null是因为效应真的不存在，还是因为regime分类错误导致attenuation bias？
- **必须做**：
  1. 报告Pre-ZLB regime分类的匹配率
  2. 用Jarociński & Karadi (2020)的information-cleaned shocks做robustness
  3. 用连续的ff.shock.0作为替代direction变量（避免离散regime分类）

### 🔴 问题2：ZLB break的识别不干净
- ZLB = 2008-12-01 是内生的（GFC导致的）
- ZLB后同时发生了：(a) FG成为工具 (b) 量化宽松 (c) 语句变长 (d) FOMC沟通策略变化
- 论文归因于FG，但没有排除其他解释
- **必须做**：
  1. 控制语句长度（total_words）——ZLB后语句从~400词暴增到~1200词
  2. 控制FOMC沟通策略变化（如2011年Bernanke新闻发布会开始）
  3. 讨论QE作为替代解释

### 🟡 问题3：N=17 hike meetings in ZLB+Post
- ZLB+Post只有17个hike meeting
- 交互项的统计功效严重依赖这17个观测
- Leave-one-regime-out: drop hike → target×dir t=-1.35 (不显著!)
- **必须做**：明确承认hike子样本太小，target×dir的稳健性有限

---

## 三、经济解释问题

### 🟡 问题1：CB score全为负值
- ZLB+Post期间，CB score从-0.092到-0.013，**全部为负**
- 论文说"hike时更hawkish"，但CB仍然是负的（net dovish）
- 需要解释：CB score衡量的是**相对**hawkishness，不是绝对水平
- **修正**：在4.3节明确说明"more hawkish"= "less dovish" = CB score less negative

### 🟡 问题2：经济意义的基准不清晰
- "71% of σ(CB)"听起来很大，但σ(CB)本身只有0.020
- 0.014的CB变化在实际中意味着什么？
- **建议**：换算为hawkish/dovish词数变化。例如：
  - 平均语句879词，0.014的CB变化 ≈ 879 × 0.014 ≈ 12个词的hawkish-dovish差异
  - 这比"71% of σ"更直观

### 🟡 问题3：FG机制的间接性
- 论文说ZLB后path shock重要是因为FG，但没有直接测FG
- Lu & Wu (2026)用quarter-end timing test直接验证再平衡机制
- 我们需要类似的直接验证
- **建议**：用FG强度指标（如"forward guidance"短语出现频率）做中介效应分析

---

## 四、方法论问题

### 🟡 问题1：HAC size distortion未充分处理
- N=109时HAC 5%检验实际拒绝率16.6%（3.3× over-rejection）
- 论文用permutation test作为替代，但正文中仍大量引用HAC t值
- **建议**：正文中只报告permutation p值，HAC t值放附录

### 🟡 问题2：permutation test的交换性假设
- 交换direction标签假设direction与残差独立
- 但direction可能与未观测的宏观状态相关
- **建议**：加wild bootstrap作为补充（已有，但应更突出）

### 🟢 问题3：multiple testing
- 同时检验target×dir和path×dir，应做Bonferroni或Holm校正
- 校正后path×dir的permutation p=0.016 → Holm p=0.032，仍显著
- 影响不大，但应报告

---

## 五、写作问题

### 🔴 问题1：摘要过长
- 当前摘要~200词，包含太多技术细节
- AEJ:Macro摘要通常150词以内
- **修正**：砍掉permutation p值和具体数字，只保留核心发现

### 🟡 问题2：Introduction缺少文献定位
- 没有讨论与GSS (2005)、Nakamura & Steinsson (2018)、Jarociński & Karadi (2020)的关系
- 没有讨论与Correa et al. (2021)的关系（CB字典的来源）
- **修正**：加一段文献定位

### 🟡 问题3：Table 2渐进控制不够渐进
- 当前6列只加了ff.shock.0和ns shock
- Lu & Wu加了duration, beta, MPE, size, dividend, FF4 factors
- 我们应该加：语句长度、FG强度、会议类型（scheduled vs unscheduled）
- **修正**：至少加total_words和fg_strength作为控制

### 🟢 问题4：被动语态残留
- "It is shown that..." → "We show that..."
- "The results suggest..." → "We find..."
- 少量残留，容易修

---

## 六、与Lu & Wu (2026)的差距分析

| 维度 | Lu & Wu (2026) | 本文 v12.7 | 差距 |
|---|---|---|---|
| 理论模型 | ✅ 2-stock模型推导命题 | ❌ 无 | **最大差距** |
| 识别策略 | ✅ Dual shares IV (2SLS) | ❌ 无IV | 无法做 |
| 渐进控制 | ✅ 6列(duration→FF4) | 🟡 6列但控制弱 | 可改进 |
| Timing test | ✅ Quarter-end | ✅ ZLB break | 逻辑类似 |
| Placebo | ✅ Non-rebalancer null | ✅ LM% null | 逻辑类似 |
| Quantity evidence | ✅ 持仓变化 | ❌ 无 | 可加FG词频 |
| 校准 | ✅ 截面→总量 | ❌ 无 | 可简单做 |
| 样本量 | N=58,497 | N=109 | 无法改变 |

**最大差距是理论模型**。Lu & Wu先推导命题再检验，我们只有empirical finding没有理论支撑。建议加一个简单的理论框架（不需要完整模型，2-3个命题即可）。

---

## 七、修改优先级

### P0（必须修，否则reject）
1. 修正AR(2)系数错误（0.25→0.107）
2. 修正CB score范围（分era报告）
3. Pre-ZLB regime分类可靠性分析
4. 控制语句长度（total_words）
5. 承认N=17 hike子样本的局限性

### P1（强烈建议，否则major revision）
6. 加理论框架（2-3个命题）
7. 加FG强度中介效应分析
8. 加total_words和fg_strength控制
9. 正文只报告permutation p值
10. 摘要精简到150词

### P2（建议，提升质量）
11. 用ff.shock.0连续direction做robustness
12. Bonferroni/Holm校正
13. 经济意义换算为词数
14. 文献定位段落
15. NW lag自动选择

---

## 八、一句话总结

**发现有趣（ZLB break），但执行粗糙（事实错误+识别不干净+缺理论）。修好P0和P1后，这是一篇可投AEJ:Macro的论文。当前版本会被desk reject或R1给major revision。**
