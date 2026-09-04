# CampusPulse 项目详细计划书
## Designing a Data-Driven Study Space Discovery Experience

---

## 1. 项目概述

### 1.1 项目名称
**CampusPulse — Designing a Data-Driven Study Space Discovery Experience**

中文名称：**基于学生真实体验数据的学习空间决策系统**

### 1.2 项目定位
CampusPulse 是一个以地图为核心的交互式校园学习空间决策平台。

项目解决的不是简单的“找附近自习室”，而是：

> 不同学习任务对环境需求不同，但目前大多数地图和点评平台无法告诉用户“这个地点是否适合我现在要做的事情”。

因此项目将真实学生体验数据、地点属性、用户偏好和简单推荐算法结合，帮助学生找到最适合当前学习任务的空间。

### 1.3 核心痛点
常见情况：
- 图书馆评分高，但可能不适合小组讨论；
- 咖啡店舒适，但可能缺少插座；
- 某些空间适合编程，却不适合背诵；
- 普通地图只告诉用户距离、营业时间和综合评分；
- 用户需要手动比较多个地点，决策成本高；
- “适不适合学习”不是一个统一分数，而是与任务类型密切相关。

### 1.4 核心研究问题
**How might student-generated data help people choose study environments that match different study activities?**

中文：
> 学生生成的数据如何帮助人们选择与不同学习活动相匹配的学习环境？

### 1.5 项目目标
1. 建立一个真实校园学习空间数据集；
2. 分析不同地点的环境特征；
3. 通过聚类建立“学习空间类型”；
4. 根据用户任务和偏好生成个性化匹配分数；
5. 将数据通过地图、比较、推荐解释等方式转化成可理解的决策体验；
6. 验证 CampusPulse 是否能够提高用户选址效率与决策信心。

---

## 2. 目标用户

主要用户：
- 大学生；
- 有图书馆、自习区、咖啡店、公共学习区等多种学习地点可选择的人；
- 经常在“去哪里学习”这个问题上花时间的人。

---

## 3. 使用场景

### 场景 A：编程
用户需要：
- 插座；
- WiFi；
- 安静；
- 可以连续坐 2–3 小时。

### 场景 B：小组讨论
用户需要：
- 可以说话；
- 桌子较大；
- 不容易打扰他人。

### 场景 C：考试复习
用户需要：
- 低噪音；
- 低拥挤；
- 高舒适度。

### 场景 D：快速完成任务
用户更重视：
- 距离；
- 便利；
- 当前位置。

---

## 4. 数据采集计划

### 4.1 地点范围
建议选择 15–25 个真实地点。

例如：
- 图书馆不同楼层；
- 教学楼自习区；
- 校园公共区域；
- 咖啡店；
- 宿舍公共区域；
- 学生活动中心；
- 附近商业空间。

### 4.2 调查对象
建议：
- 50–100 名学生；
- 如果时间紧，可先完成 40–60 份高质量数据。

### 4.3 问卷字段
#### 基础信息
- Location
- Visit time
- Study task

#### 环境评分（1–5）
- Noise
- Crowding
- Lighting
- Comfort
- WiFi
- Power outlets
- Cleanliness
- Temperature comfort
- Safety
- Accessibility

#### 学习适配度
- Individual study
- Group discussion
- Coding
- Reading
- Writing
- Exam revision

#### 主观评价
- Overall satisfaction
- Would return
- Free-text comments

### 4.4 可选字段
- Distance from dorm/classroom
- Opening hours
- Indoor/outdoor
- Food/drink allowed
- Seat availability

---

## 5. 数据清洗与处理

### 5.1 清洗流程
```text
Survey Data
    ↓
Remove duplicates
    ↓
Handle missing values
    ↓
Standardize location names
    ↓
Normalize rating scales
    ↓
Aggregate by location
    ↓
Create study-space profiles
```

### 5.2 输出
每个地点形成：
- 平均噪音；
- 舒适度；
- WiFi；
- 插座；
- 拥挤度；
- 适合任务评分。

---

## 6. 数据分析计划

### 6.1 Exploratory Data Analysis
分析：
- 哪些属性与整体满意度最相关？
- Coding 用户最重视什么？
- Group Work 与 Individual Study 的环境偏好有何差异？
- 哪些地点评价分布最稳定？

### 6.2 Correlation Analysis
分析：
- Noise vs satisfaction
- Crowding vs focus
- Power outlets vs coding suitability
- Comfort vs long-session willingness

### 6.3 Clustering
使用：
- K-Means

输入特征：
- Noise
- Comfort
- Crowding
- Discussion-friendly
- WiFi
- Power
- Lighting

输出空间类型，例如：

1. **Deep Focus**
2. **Social Study**
3. **Quick Work**
4. **Group Collaboration**

### 6.4 PCA 可视化
将高维特征压缩到二维，展示各地点如何聚集。

---

## 7. 推荐逻辑

### 7.1 用户输入
用户选择：

**What are you doing today?**
- Coding
- Reading
- Writing
- Group Work
- Exam Revision

然后设置权重：

```text
Quiet        ━━━━━●━━
WiFi         ━━━━━━●━
Power        ━━━━━━━●
Comfort      ━━━━●━━
Distance     ━━●━━━━
```

### 7.2 Weighted Score
每个地点：

```text
Score =
Quiet × user_weight
+ WiFi × user_weight
+ Power × user_weight
+ Comfort × user_weight
+ Distance × user_weight
...
```

归一化为：
- 0–100%
- Match Score

### 7.3 推荐输出
例如：

**Library 4F — 92% Match**

并解释：
> This space was recommended mainly because you prioritised quietness and power availability.

---

## 8. 产品功能范围

### 8.1 核心地图
以地图作为主界面。

每个地点显示：
- 地点名称；
- 类型；
- 匹配度；
- 标签。

### 8.2 Task Selector
用户首先选择学习任务。

### 8.3 Preference Sliders
调整：
- Quiet
- Distance
- Power
- Comfort
- WiFi
- Group friendliness

### 8.4 Best Match
展示前三名。

### 8.5 Location Detail
包含：
- 雷达图；
- 属性评分；
- 学习类型标签；
- 用户评论摘要；
- 地图位置。

### 8.6 Compare Mode
允许同时比较 2–3 个地点。

### 8.7 Why Recommended?
解释主要推荐原因。

### 8.8 Community Update
用户使用后提交：
- 当天拥挤度；
- 噪音；
- 舒适度；
- 是否推荐。

---

## 9. 技术栈

### 编程
- Python

### 数据处理
- Pandas
- NumPy

### Machine Learning
- Scikit-learn

### 地图
首选：
- Folium

备选：
- Plotly Map
- Leaflet

### 可视化
- Plotly
- Matplotlib

### Web
- Streamlit

### 设计
- Figma

### 问卷
- Google Forms / 问卷星

---

## 10. 系统架构

```text
Student Survey
     ↓
Data Cleaning
     ↓
Location Aggregation
     ↓
EDA / Correlation
     ↓
K-Means Clustering
     ↓
Space Categories
     ↓
User Task + Preferences
     ↓
Weighted Matching Algorithm
     ↓
Interactive Map
     ↓
Recommendation + Explanation
```

---

## 11. HCI 研究

### 11.1 前期访谈
建议：
- 8–10 人

问题：
1. 你通常在哪里学习？
2. 选择学习地点时最看重什么？
3. 不同任务会不会选择不同地点？
4. 你最讨厌哪些学习环境问题？
5. 你是否会在地图或点评平台寻找学习地点？
6. 现有平台缺少什么信息？
7. 你是否愿意贡献实时环境评价？

### 11.2 输出
- Persona；
- User Journey；
- Key Pain Points；
- Design Requirements。

---

## 12. 设计策略

### 12.1 核心原则
1. **Task-first**
先问“你今天要做什么”，而不是先让用户找地点。

2. **Decision over Dashboard**
不是展示越多图越好，而是帮助用户做决定。

3. **Explain Recommendation**
用户应知道推荐为什么产生。

4. **Community-generated**
数据不是死的，可以被学生持续更新。

---

## 13. Figma 页面建议

### 页面 1
Landing / Task Selection

### 页面 2
Interactive Map

### 页面 3
Preference Settings

### 页面 4
Best Matches

### 页面 5
Location Detail

### 页面 6
Compare Locations

### 页面 7
Submit Feedback

---

## 14. 用户测试

### 14.1 参与者
建议：
- 15–20 名学生

### 14.2 对照方式
#### Version A
普通地图/静态地点列表。

#### Version B
CampusPulse。

### 14.3 测试任务
例如：

> 你需要完成一个 2 小时编程任务，需要安静、插座和稳定 WiFi，请选择地点。

> 你需要和 3 位同学讨论小组作业，请选择最合适地点。

### 14.4 记录指标
- 决策时间；
- 选择信心；
- 信息有用性；
- 对结果满意度；
- 是否理解推荐原因；
- 任务完成率。

---

## 15. 时间计划（建议 7–8 周）

### 第 1 周
- 前期访谈；
- 地点范围确定；
- 问卷设计。

### 第 2 周
- 发放问卷；
- 实地记录地点信息；
- 初步 Figma。

### 第 3 周
- 数据清洗；
- EDA；
- Correlation。

### 第 4 周
- Clustering；
- Recommendation Score；
- PCA。

### 第 5 周
- 地图开发；
- Preference sliders；
- Best Match。

### 第 6 周
- Compare；
- Why Recommended；
- Community Feedback。

### 第 7 周
- 用户测试；
- 数据记录。

### 第 8 周
- 分析；
- UI 优化；
- Portfolio 排版。

---

## 16. 风险控制

### 风险 1：问卷样本不够
解决：
- 控制地点数量；
- 先做 15–20 个地点；
- 优先保证每个地点有足够评价。

### 风险 2：地图功能过于复杂
解决：
- 只需实现地图定位、点击地点、显示信息；
- 不做路径导航。

### 风险 3：项目看起来像大众点评
解决：
- 强调“任务类型匹配”；
- 强调“个性化权重”；
- 强调“解释为什么推荐”。

### 风险 4：数据更新困难
解决：
- 用户提交反馈后先写入 CSV / SQLite；
- 无需搭建复杂实时数据库。

---

## 17. 最终交付物

必须：
- 校园学习空间数据集；
- 数据分析 Notebook；
- K-Means / PCA 分析；
- 可运行地图 Web App；
- Figma；
- 用户测试报告；
- GitHub；
- Portfolio Case Study。

建议：
- 地图演示 GIF；
- 2–3 分钟 Demo 视频；
- 一页 Data Pipeline 图。

---

## 18. 作品集展示结构

### Page 1 — Hero
地图视觉 + 核心问题。

### Page 2 — Problem
为什么普通地图无法回答“哪里最适合我现在学习”。

### Page 3 — Research
学生访谈和问卷。

### Page 4 — Dataset
展示你自己建立的数据集。

### Page 5 — Analysis
相关性、聚类、PCA。

### Page 6 — Design Opportunity
从研究洞察到设计原则。

### Page 7 — Recommendation Logic
权重如何转成 Match Score。

### Page 8 — Interactive Map
最终地图。

### Page 9 — Comparison & Explanation
比较和 Why Recommended。

### Page 10 — User Testing
实验设计。

### Page 11 — Results
决策时间、信心等指标。

### Page 12 — Reflection
局限与未来迭代。

---

## 19. 项目成功标准

如果达到以下条件，项目就已经具有较高作品集价值：

- 数据是你自己收集或实地补充的；
- 至少 15 个真实地点；
- 有聚类和数据分析；
- 地图真实可交互；
- 用户可以根据任务设置偏好；
- 推荐不是随机，而是有明确逻辑；
- 推荐理由可解释；
- 有真实学生完成用户测试；
- 最终结论能够回答原始研究问题。