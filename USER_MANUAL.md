# AHP-FCE-TOPSIS-GA 无人作战体系效能评估系统 V2.0
## 详细用户使用手册 - 研究级多准则决策分析

**版本**: V2.0 - Production Ready
**更新日期**: 2025-12-04
**测试状态**: 75/76 单元测试通过 (98.7% 成功率)
**适用对象**: 军事系统分析人员、决策支持人员、学术研究人员、系统开发人员

---

## 📋 目录

1. [系统概述](#系统概述)
2. [安装与环境配置](#安装与环境配置)
3. [文件结构说明](#文件结构说明)
4. [配置文件详解](#配置文件详解)
5. [核心功能使用](#核心功能使用)
6. [体系构建配置](#体系构建配置)
7. [遗传算法优化](#遗传算法优化)
8. [结果文件说明](#结果文件说明)
9. [常见问题解答](#常见问题解答)
10. [高级使用技巧](#高级使用技巧)

---

## 🎯 系统概述

### 系统功能
AHP-FCE-TOPSIS-GA评估系统是一个综合性的多准则决策分析工具，专门用于无人作战体系配置的效能评估和优化。系统支持场景感知评估，能够根据具体作战环境动态调整评估标准。

### 核心算法
- **AHP (层次分析法)**: 计算指标权重，一致性检验
- **FCE (模糊综合评价)**: 处理定性指标评估
- **TOPSIS (逼近理想解排序法)**: 多方案排序
- **GA (遗传算法)**: 体系配置优化
- **场景感知评估**: 根据作战场景动态调整评估标准和权重

### 🚀 V2.0 重大更新

#### ✅ 核心数学算法验证 (100% 成功率)
- **TOPSIS Module**: 17/17 测试通过 - 数学算法完全验证
- **FCE Module**: 14/14 测试通过 - 模糊评价完全验证
- **GA Optimizer**: 13/13 测试通过 - 遗传算法完全验证
- **Scenario Integration**: 18/18 测试通过 - 场景感知评估完全验证

#### 🔧 主要改进和新增功能

**1. 全面测试框架** (V2.0新增)
- **专业pytest配置**: 95%+ 代码覆盖率要求
- **性能基准测试**: 可扩展性监控和回归测试
- **数学精度验证**: 1e-6 精度验证标准
- **研究级测试标记**: mathematical, research, performance

**2. 增强的数据基础设施** (V2.0扩展)
- **5个作战场景**: 包括北极域优势、联军演习、快速危机响应
- **8个力量结构示例**: 从成本最优到能力最大化的完整配置谱系
- **完整专家判断矩阵**: 15个二级指标的成对比较矩阵
- **智能数据格式**: 向后兼容的数据结构设计

**3. 生产级可靠性** (V2.0完善)
- **健壮的错误处理**: 全面的异常处理和优雅降级
- **数学稳定性**: 除零保护和边界条件处理
- **审计追踪**: 完整的转换链记录
- **性能监控**: 实时内存和执行时间跟踪

**4. 研究级验证** (V2.0特色)
- **统计验证**: 假设检验和置信区间计算
- **重现性标准**: 确定性行为和受控随机性
- **发表质量**: 自动化生成验证报告
- **基准数据集**: 标准化测试数据集用于比较

#### 🆕 V1.1.0 功能保留
- **作战场景集成**: 支持四类典型作战场景的针对性评估
- **动态权重调整**: 根据场景威胁和任务需求调整指标权重
- **场景特定约束**: 不同场景具有不同的约束条件和成功标准
- **场景成功评分**: 提供场景特定的任务达成度评估

### 评估指标体系
基于无人作战体系效能评估一级指标体系的设定，本系统采用以下五级指标体系：

```
一级指标 (5个):
├── C1: 态势感知能力 (Situational Awareness Capability) (权重: 0.25)
│   ├── C1_1: 侦察探测能力 (Reconnaissance & Detection Capability) (权重: 0.08)
│   ├── C1_2: 信息融合能力 (Information Fusion Capability) (权重: 0.09)
│   └── C1_3: 态势理解能力 (Situation Understanding Capability) (权重: 0.08)
├── C2: 指挥决策能力 (Command & Decision Capability) (权重: 0.20)
│   ├── C2_1: 任务规划能力 (Mission Planning Capability) (权重: 0.07)
│   ├── C2_2: 威胁评估能力 (Threat Assessment Capability) (权重: 0.07)
│   └── C2_3: 决策响应能力 (Decision Response Capability) (权重: 0.06)
├── C3: 行动打击能力 (Action & Strike Capability) (权重: 0.25)
│   ├── C3_1: 火力打击能力 (Fire Strike Capability) (权重: 0.08)
│   ├── C3_2: 机动占位能力 (Maneuver & Positioning Capability) (权重: 0.09)
│   └── C3_3: 电子对抗能力 (Electronic Warfare Capability) (权重: 0.08)
├── C4: 网络通联能力 (Network & Communication Capability) (权重: 0.15)
│   ├── C4_1: 信息传输能力 (Information Transmission Capability) (权重: 0.05)
│   ├── C4_2: 网络可靠性 (Network Reliability) (权重: 0.05)
│   └── C4_3: 协同作战能力 (Collaborative Operations Capability) (权重: 0.05)
└── C5: 体系生存能力 (System Survivability Capability) (权重: 0.15)
    ├── C5_1: 抗毁能力 (Anti-Destruction Capability) (权重: 0.05)
    ├── C5_2: 任务恢复能力 (Mission Recovery Capability) (权重: 0.05)
    └── C5_3: 持续作战能力 (Sustained Operations Capability) (权重: 0.05)
```

**指标体系详细说明：**

1. **C1: 态势感知能力** - 作战体系的"眼睛"和"前脑"，衡量体系对战场环境中的目标、威胁及自身状态进行探测、识别、融合、理解并形成统一战场态势图景的综合能力
   - 文献支撑：Alberts et al., 2000 (网络中心战)；Boyd, 1987 (OODA环理论)；吴汉荣 et al., 2007；李大鹏 et al., 2012

2. **C2: 指挥决策能力** - 作战体系的"神经中枢"，衡量体系在理解战场态势后，进行自主或半自主的任务规划、威胁评估、火力分配、行动协同并生成具体指令的效率与质量
   - 文献支撑：Alberts et al., 2000 (C4ISR框架)；Boyd, 1987 (OODA环)；吴汉荣 et al., 2007；李大鹏 et al., 2012

3. **C3: 行动打击能力** - 作战体系"拳头"的最终体现，衡量体系在接收指令后，机动、占位并运用火力或电子战等非火力手段，对目标实施精确、有效打击的综合能力
   - 文献支撑：Boyd, 1987 (OODA环理论)；吴汉荣 et al., 2007；费继番 et al., 2016

4. **C4: 网络通联能力** - 作战体系的"血脉"，是实现态势感知、指挥决策和行动打击能力的基础支撑，衡量体系内部各节点之间进行信息安全、可靠、实时交互的能力
   - 文献支撑：Alberts et al., 2000 (网络中心战)；李大鹏 et al., 2012

5. **C5: 体系生存能力** - 作战体系在复杂对抗环境下的"金钟罩"，衡量体系在遭受敌方攻击或内部故障时的鲁棒性、损伤容忍度、任务恢复效率和持续作战能力
   - 文献支撑：费继番 et al., 2016；韩春 et al., 2012

---

## 🛠️ 安装与环境配置

### 系统要求
- **Python**: 3.8+
- **内存**: 最小4GB，推荐8GB
- **存储**: 最小1GB可用空间
- **操作系统**: Windows/Linux/macOS

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd ahp_fce_topsis
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **验证安装**
```bash
python main.py --version
# 应显示: AHP-FCE-TOPSIS-GA 1.0.0
```

### 依赖包清单
```
numpy>=1.21.0        # 矩阵运算
pandas>=1.3.0         # 数据处理
pygad>=2.10.0         # 遗传算法
matplotlib>=3.5.0     # 数据可视化
pyyaml>=6.0           # YAML文件处理
pytest>=7.0           # 单元测试
```

---

## 📁 文件结构说明

### 项目目录结构
```
ahp_fce_topsis/
├── 📄 main.py                    # 主程序入口
├── 📄 requirements.txt           # 依赖包列表
├── 📄 README.md                  # 项目说明文档
├── 📄 USER_MANUAL.md            # 用户使用手册 (本文件)
│
├── 📁 config/                    # 配置文件目录
│   ├── 📄 indicators.yaml        # 指标体系配置
│   └── 📄 fuzzy_sets.yaml        # 模糊评价集配置
│
├── 📁 data/                      # 数据文件目录
│   ├── 📁 expert_judgments/      # 专家判断矩阵
│   │   ├── 📄 primary_capabilities.yaml      # 一级指标判断矩阵
│   │   └── 📁 secondary_indicators/         # 二级指标判断矩阵
│   │       ├── 📄 c1_indicators.yaml
│   │       ├── 📄 c2_indicators.yaml
│   │       ├── 📄 c3_indicators.yaml
│   │       ├── 📄 c4_indicators.yaml
│   │       └── 📄 c5_indicators.yaml
│   ├── 📁 scenarios/             # 优化场景配置
│   │   ├── 📄 strait_control.yaml           # 海峡控制场景
│   │   └── 📄 test_scenario.yaml             # 测试场景
│   └── 📁 schemes/               # 体系配置方案
│       ├── 📄 balanced_force.yaml           # 均衡力量配置
│       ├── 📄 high_endurance_force.yaml     # 高续航力量配置
│       ├── 📄 tech_lite_force.yaml          # 技术精简力量配置
│       ├── 📄 baseline_scheme.yaml          # 基准方案
│       ├── 📄 scheme_a.yaml                 # 方案A
│       └── 📄 scheme_b.yaml                 # 方案B
│
├── 📁 modules/                   # 核心算法模块
│   ├── 📄 ahp_module.py           # AHP算法实现
│   ├── 📄 fce_module.py           # FCE算法实现
│   ├── 📄 topsis_module.py        # TOPSIS算法实现
│   ├── 📄 ga_optimizer.py         # 遗传算法优化
│   └── 📄 evaluator.py            # 评估流程编排
│
├── 📁 utils/                     # 工具函数
│   ├── 📄 consistency_check.py    # 一致性检验
│   ├── 📄 normalization.py       # 数据标准化
│   ├── 📄 validation.py          # 数据验证
│   └── 📄 visualization.py       # 数据可视化
│
├── 📁 tests/                     # 测试文件
│   ├── 📁 unit/                   # 单元测试
│   ├── 📁 integration/            # 集成测试
│   └── 📁 fixtures/               # 测试数据
│
└── 📁 outputs/                   # 输出文件目录
    ├── 📁 outputs/results/               # 评估结果 (JSON格式 + PNG图表)
    ├── 📁 reports/               # 评估报告 (Markdown格式)
    └── 📁 plots/                 # 图表文件 (PNG格式，已迁移到outputs/results/)
```

---

## ⚙️ 配置文件详解

### 1. 指标体系配置 (`config/indicators.yaml`)

**文件位置**: `config/indicators.yaml`

**配置说明**:
```yaml
# 一级指标配置 (基于无人作战体系效能评估一级指标体系的设定)
primary_capabilities:
  C1:
    name: "态势感知能力 (Situational Awareness Capability)"
    description: "作战体系的'眼睛'和'前脑'，衡量体系对战场环境中的目标、威胁及自身状态进行探测、识别、融合、理解并形成统一战场态势图景的综合能力"
    weight: 0.25                    # 权重值，总和应为1.0
    literature_reference: "Alberts et al., 2000, Network Centric Warfare; Boyd, 1987, OODA Loop Theory; 吴汉荣 et al., 2007; 李大鹏 et al., 2012"

  C2:
    name: "指挥决策能力 (Command & Decision Capability)"
    description: "作战体系的'神经中枢'，衡量体系在理解战场态势后，进行自主或半自主的任务规划、威胁评估、火力分配、行动协同并生成具体指令的效率与质量"
    weight: 0.20
    literature_reference: "Alberts et al., 2000, C4ISR Framework; Boyd, 1987, OODA Loop; 吴汉荣 et al., 2007; 李大鹏 et al., 2012"

  C3:
    name: "行动打击能力 (Action & Strike Capability)"
    description: "作战体系'拳头'的最终体现，衡量体系在接收指令后，机动、占位并运用火力或电子战等非火力手段，对目标实施精确、有效打击的综合能力"
    weight: 0.25
    literature_reference: "Boyd, 1987, OODA Loop Theory; 吴汉荣 et al., 2007; 费继番 et al., 2016"

  C4:
    name: "网络通联能力 (Network & Communication Capability)"
    description: "作战体系的'血脉'，是实现态势感知、指挥决策和行动打击能力的基础支撑，衡量体系内部各节点之间进行信息安全、可靠、实时交互的能力"
    weight: 0.15
    literature_reference: "Alberts et al., 2000, Network Centric Warfare; 李大鹏 et al., 2012"

  C5:
    name: "体系生存能力 (System Survivability Capability)"
    description: "作战体系在复杂对抗环境下的'金钟罩'，衡量体系在遭受敌方攻击或内部故障时的鲁棒性、损伤容忍度、任务恢复效率和持续作战能力"
    weight: 0.15
    literature_reference: "费继番 et al., 2016; 韩春 et al., 2012"

# 二级指标配置示例 (每个一级指标下包含3个二级指标)
secondary_indicators:
  C1_1:
    name: "侦察探测能力 (Reconnaissance & Detection Capability)"
    description: "对战场环境中目标、威胁进行全方位探测和识别的能力"
    primary_capability: "C1"        # 所属一级指标
    unit: "capability_score"        # 单位
    type: "benefit"                 # 指标类型: benefit(效益型) 或 cost(成本型)
    fuzzy_evaluation: true          # 是否使用模糊评价
    weight: 0.08                    # 权重值
    literature_reference: "Alberts et al., 2000; ISR Performance Standards 2020"

  C1_2:
    name: "信息融合能力 (Information Fusion Capability)"
    description: "将多源信息进行融合处理，形成统一战场态势图景的能力"
    primary_capability: "C1"
    unit: "fusion_score"
    type: "benefit"
    fuzzy_evaluation: true
    weight: 0.09
    literature_reference: "Data Fusion Engineering Handbook 2019; 多源信息融合理论"

  C1_3:
    name: "态势理解能力 (Situation Understanding Capability)"
    description: "对战场态势进行深度理解、分析和预测的综合能力"
    primary_capability: "C1"
    unit: "understanding_score"
    type: "benefit"
    fuzzy_evaluation: true
    weight: 0.08
    literature_reference: "Boyd 1987; 认知科学在军事态势理解中的应用"
```

**修改指南**:
1. **权重调整**: 修改`weight`值，确保同层级权重总和为1.0
2. **指标增减**: 可根据需要增减二级指标
3. **文献引用**: 更新`literature_reference`字段
4. **模糊设置**: `fuzzy_evaluation: true`表示使用语言变量评估

### 2. 模糊评价集配置 (`config/fuzzy_sets.yaml`)

**文件位置**: `config/fuzzy_sets.yaml`

**配置说明**:
```yaml
# 模糊语言变量定义
linguistic_scale:
  差:
    value: 0.25                   # 对应数值
    description: "Poor"
  中:
    value: 0.50
    description: "Medium"
  良:
    value: 0.75
    description: "Good"
  优:
    value: 1.00
    description: "Excellent"

# 适用指标列表
applicable_indicators:
  - "C1_1"
  - "C1_2"
  # ... 所有使用模糊评价的指标ID
```

### 3. 专家判断矩阵 (`data/expert_judgments/`)

#### 一级指标判断矩阵 (`data/expert_judgments/primary_capabilities.yaml`)

**文件位置**: `data/expert_judgments/primary_capabilities.yaml`

**配置说明**:
```yaml
matrix_id: "primary_capabilities"
expert_id: "expert_001"
expert_qualification: "军事系统分析师"
assessment_date: "2025-10-25"
dimension: 5                     # 矩阵维度

# 判断矩阵 (5×5)
# 行列顺序: C1, C2, C3, C4, C5
# 数值含义: 1-同等重要, 3-中等重要, 5-比较重要, 7-非常重要, 9-极端重要
matrix:
  - [1.0, 2.0, 3.0, 4.0, 5.0]  # C1行
  - [0.5, 1.0, 1.5, 2.0, 2.5]  # C2行 (注意互反性)
  - [0.333, 0.667, 1.0, 1.333, 1.667]  # C3行
  - [0.25, 0.5, 0.75, 1.0, 1.25]  # C4行
  - [0.2, 0.4, 0.6, 0.8, 1.0]   # C5行

# 系统计算结果
calculated_cr: 0.0000            # 一致性比率，应<0.1
weights: [0.30, 0.15, 0.30, 0.10, 0.15]  # 计算出的权重
validation_status: "valid"        # 验证状态
```

**配置规则**:
1. **对角线**: 必须为1.0 (自身比较)
2. **互反性**: A[i][j] = 1/A[j][i]
3. **一致性**: 计算出的CR值应<0.1
4. **专家信息**: 填写真实的专家资质信息

#### 二级指标判断矩阵 (`data/expert_judgments/secondary_indicators/c*_indicators.yaml`)

**配置示例** (C1指标):
```yaml
matrix_id: "c1_secondary_indicators"
primary_capability: "C1"
dimension: 3                     # C1有3个二级指标

# 判断矩阵 (3×3)
# 行列顺序: C1_1, C1_2, C1_3
matrix:
  - [1.0, 1.0, 0.5]            # C1_1 vs 其他
  - [1.0, 1.0, 0.5]            # C1_2 vs 其他
  - [2.0, 2.0, 1.0]            # C1_3 vs 其他

calculated_cr: 0.0
weights: [0.25, 0.25, 0.50]      # C1的三个二级指标权重
validation_status: "valid"
```

### 4. 体系配置方案 (`data/schemes/`)

**文件位置**: `data/schemes/[scheme_name].yaml`

**配置示例**:
```yaml
# 方案基本信息
scheme_id: "balanced_force"
scheme_name: "均衡多域力量"
scheme_description: "提供全面能力的均衡配置"

# 指挥信息
command_authority: "联合部队司令部"
geographic_scope: "近海作战区域"
threat_level: "中等"
mission_type: "多域防御"

# 平台清单
platform_inventory:
  USV_Unmanned_Surface_Vessel:
    count: 12                     # 平台数量
    types:
      surveillance_usv: 6        # 侦察型无人水面艇
      strike_usv: 4              # 攻击型无人水面艇
      mine_hunting_usv: 2        # 反水雷无人水面艇

  UAV_Unmanned_Aerial_Vehicle:
    count: 8
    types:
      surveillance_uav: 4        # 侦察型无人机
      attack_uav: 2              # 攻击型无人机
      ew_uav: 2                  # 电子战无人机

  UUV_Unmanned_Underwater_Vessel:
    count: 6
    types:
      surveillance_uuv: 3        # 侦察型无人潜航器
      mine_hunting_uuv: 2        # 反水雷无人潜航器
      attack_uuv: 1              # 攻击型无人潜航器

# 部署计划
deployment_plan:
  primary_sector:
    coordinates: [25.5, -80.5]    # 中心坐标 [纬度, 经度]
    radius_km: 150                # 作战半径
  secondary_sectors:
    - coordinates: [26.0, -80.0]
      radius_km: 100

# 巡逻路线
patrol_routes:
  - route_id: "alpha_picket"
    waypoints: [[25.3, -80.3], [25.7, -80.7], [25.3, -80.3]]
    patrol_type: "circular"
    asset_assignment: ["USV_1", "USV_2", "UAV_1"]

# 任务分配
task_assignments:
  surveillance_operations:
    primary_assets: ["surveillance_usv", "surveillance_uav", "surveillance_uuv"]
    coverage_requirement: 0.85    # 覆盖率要求
    endurance_hours: 72           # 持续时间
    update_frequency_min: 15      # 更新频率

# 操作约束
operational_constraints:
  total_platforms: 26            # 平台总数
  max_budget_million_usd: 850    # 最大预算
  deployment_area_km2: 70650    # 部署面积
  endurance_hours: 96           # 持续作战时间
  communication_range_km: 200    # 通信距离

# 专家评估
expert_assessments:
  C1_1_Detection_Range:
    linguistic_term: "良"         # 语言变量: 差/中/良/优
    confidence: 0.85              # 置信度 [0-1]
    justification: "现代化传感器套件"
  # ... 其他指标的专家评估
```

---

## 🎯 场景感知评估使用

### 场景感知评估概述
场景感知评估是v1.1.0版本的核心功能，使评估结果能够真实反映具体作战环境下的体系效能。不同作战场景对体系能力的要求不同，场景感知评估会动态调整：

1. **指标基础值**：根据场景类型调整指标计算基础值
2. **权重分配**：根据场景任务重点调整AHP权重
3. **模糊评价阈值**：根据场景需求调整定性指标评价标准
4. **约束条件**：应用场景特定的约束限制
5. **成功标准**：计算场景特定的任务达成度

### 场景感知评估的优势

| 评估方式 | 传统评估 | 场景感知评估 | 优势 |
|----------|----------|--------------|------|
| **通用性** | ✅ 统一标准 | ❌ 场景特定 | 适合比较性研究 |
| **针对性** | ❌ 一刀切 | ✅ 差异化设计 | 符合实战需求 |
| **准确性** | ❌ 可能偏差 | ✅ 精确反映 | 提高决策质量 |
| **实用性** | ❌ 脱离实际 | ✅ 贴近实战 | 支撑实战应用 |

### 使用场景感知评估

#### 单方案场景评估
```bash
# 使用近岸水下侦察监视场景评估方案
python main.py evaluate --schemes data/schemes/balanced_force.yaml \
  --scenario data/scenarios/operational/nearshore_underwater_recon.yaml

# 输出示例：
# Loading operational scenario: nearshore_underwater_recon.yaml
# Loaded scenario: 近岸水下侦察监视作战
# Ci Score: 0.9106
# 场景成功评分: 0.85
# vs Baseline: better
```

#### 多方案批量评估
```bash
# 在海峡要道控守场景下比较多个方案
python main.py evaluate \
  --schemes data/schemes/balanced_force.yaml data/schemes/*.yaml \
  --scenario data/scenarios/operational/strait_control_defense.yaml \
  --batch

# 输出示例：
# Total schemes evaluated: 2
# Rankings:
#   1. high_endurance_force: Ci = 0.8723
#   2. balanced_force: Ci = 0.6541
```

#### GA优化场景应用
```bash
# 基于登陆场通道清扫场景进行优化
python main.py optimize \
  --scenario data/scenarios/operational/amphibious_landing_clearance.yaml \
  --population 50 --generations 100 \
  --output outputs/results/amphibious_optimization.json

# 输出示例：
# Best Configuration Fitness: 0.8234
# Scenario Success Score: 0.89
# Total Platforms: 32
# Estimated Cost: $96.0M
```

### 场景对比分析

用户可以通过切换不同场景来评估同一方案在不同作战环境下的表现：

```bash
# 方案在不同场景下的表现对比
echo "=== 方案多场景适应性分析 ===" && \
echo "1. 通用评估: " && \
python main.py evaluate --schemes data/schemes/balanced_force.yaml | grep "Ci Score" && \
echo "2. 近岸侦察: " && \
python main.py evaluate --schemes data/schemes/balanced_force.yaml \
  --scenario data/scenarios/operational/nearshore_underwater_recon.yaml | grep "Ci Score" && \
echo "3. 海峡控守: " && \
python main.py evaluate --schemes data/schemes/balanced_force.yaml \
  --scenario data/scenarios/operational/strait_control_defense.yaml | grep "Ci Score" && \
echo "4. 登陆清扫: " && \
python main.py evaluate --schemes data/schemes/balanced_force.yaml \
  --scenario data/scenarios/operational/amphibious_landing_clearance.yaml | grep "Ci Score"
```

### 场景评估结果解读

#### 场景评估输出字段
```json
{
  "scheme_id": "balanced_force",
  "scenario_id": "nearshore_underwater_recon",
  "scenario_type": "reconnaissance_surveillance",
  "ci_score": 0.9106,
  "rank": 1,
  "evaluation_metadata": {
    "scenario_success_score": 0.85,
    "scenario_aware_evaluation": true,
    "performance_vs_baseline": "better",
    "validation_passed": true
  }
}
```

#### 关键指标解释

- **Ci Score**: 综合效能得分（0-1），越高越好
- **Scenario Success Score**: 场景特定任务达成度（0-1）
- **Performance vs Baseline**: 相对于基准方案的表现

### 场景配置文件使用

#### 创建自定义场景
```bash
# 复制现有场景模板
cp data/scenarios/operational/nearshore_underwater_recon.yaml \
   data/scenarios/operational/my_custom_scenario.yaml

# 编辑场景参数
# - 调整威胁环境 (threat_environment)
# - 修改任务目标 (mission_objectives)
# - 更新约束条件 (constraints)
# - 设定评估权重 (objective_weights)
```

#### 场景文件关键配置
```yaml
# 场景基本信息
scenario_id: "custom_scenario"
scenario_name: "自定义作战场景"
scenario_type: "area_control_defense"

# 威胁环境定义
threat_environment:
  primary_threats:
    - type: "敌方潜艇"
      quantity: "3-5艘"
      capability: "常规动力潜艇"
    - type: "水面威胁"
      quantity: "2-4艘"
      capability: "导弹攻击艇"

# 任务目标设定
mission_objectives:
  primary:
    - objective: "区域控制"
      weight: 0.40
      success_criteria: "控制率≥90%，响应时间≤15分钟"

# 遗传算法权重
objective_weights:
  surveillance_effectiveness: 0.30
  strike_capability: 0.40
  anti_submarine_capability: 0.30
```

---

## 🚀 核心功能使用

### 1. 命令行界面概览

```bash
python main.py --help
```

**可用命令**:
- `evaluate` - 评估体系配置方案
- `optimize` - 遗传算法优化
- `sensitivity` - 敏感性分析
- `visualize` - 数据可视化
- `report` - 生成评估报告
- `validate` - 配置文件验证
- `setup` - 创建示例配置文件

### 2. 体系配置评估

#### 2.1 单方案评估
```bash
python main.py evaluate --schemes data/schemes/balanced_force.yaml --scenario data/scenarios/operational/nearshore_underwater_recon.yaml
```

**输出示例**:
```
Starting evaluation...
Loading configurations...
Loaded 1 scheme(s) for evaluation

Evaluating scheme 1/1: balanced_force
  Ci Score: 0.5292
  Rank: 1
  Validation: PASSED

Evaluation completed successfully!
```

#### 2.2 多方案比较评估
```bash
python main.py evaluate --schemes data/schemes/balanced_force.yaml data/schemes/high_endurance_force.yaml data/schemes/tech_lite_force.yaml --scenario data/scenarios/operational/nearshore_underwater_recon.yaml
```

#### 2.3 批量评估和排序
```bash
python main.py evaluate --schemes data/schemes/*.yaml --batch --output outputs/results/batch_evaluation.json
```

**输出示例**:
```
============================================================
EVALUATION RESULTS
============================================================
Total schemes evaluated: 3
Best scheme: high_endurance_force (Ci: 0.5752)

Rankings:
  1. high_endurance_force: Ci = 0.5752
  2. balanced_force: Ci = 0.5292
  3. tech_lite_force: Ci = 0.4369
```

#### 2.4 评估结果保存
```bash
python main.py evaluate --schemes data/schemes/balanced_force.yaml --output outputs/results/my_evaluation.json
```

### 3. 配置文件验证

#### 3.1 验证方案配置
```bash
python main.py validate --scheme data/schemes/balanced_force.yaml
```

**输出示例**:
```
Validating configuration files...
Validating scheme: data/schemes/balanced_force.yaml
✓ Scheme configuration is valid
```

#### 3.2 验证AHP判断矩阵
```bash
python main.py validate --ahp-matrix data/expert_judgments/primary_capabilities.yaml
```

**输出示例**:
```
Validating configuration files...
Validating AHP matrix: data/expert_judgments/primary_capabilities.yaml
✓ AHP matrix is valid
  Consistency Ratio (CR): 0.0000
  Lambda max: 5.0000
  Valid: True
```

### 4. 敏感性分析

```bash
python main.py sensitivity --baseline-results outputs/results/evaluation.json --perturbation 0.2 --iterations 100 --output outputs/results/sensitivity.json
```

**参数说明**:
- `--baseline-results`: 基准评估结果文件
- `--perturbation`: 权重扰动范围 (0-1)
- `--iterations`: 迭代次数
- `--output`: 输出文件路径

### 5. 数据可视化

#### 5.1 生成对比图表
```bash
python main.py visualize --plot-type comparison --input outputs/results/evaluation.json --output outputs/results/comparison.png
```

#### 5.2 生成雷达图
```bash
python main.py visualize --plot-type radar --input outputs/results/evaluation.json --output outputs/results/radar.png
```

#### 5.3 生成收敛曲线
```bash
python main.py visualize --plot-type convergence --input outputs/results/optimization.json --output outputs/results/convergence.png
```

### 6. 报告生成

#### 6.1 生成基础报告
```bash
python main.py report --results outputs/results/evaluation.json --format md --output outputs/reports/evaluation_report.md
```

#### 6.2 生成包含方法论和敏感性分析的完整报告
```bash
python main.py report --results outputs/results/evaluation.json --include-methodology --include-sensitivity --format md --output outputs/reports/comprehensive_report.md
```

---

## 🏗️ 体系构建配置

### 1. 创建新的体系配置

#### 步骤1: 复制模板文件
```bash
cp data/schemes/balanced_force.yaml data/schemes/my_custom_scheme.yaml
```

#### 步骤2: 编辑配置文件
```yaml
# 修改基本信息
scheme_id: "my_custom_scheme"
scheme_name: "我的自定义方案"
scheme_description: "根据特定需求定制的配置"

# 调整平台配置
platform_inventory:
  USV_Unmanned_Surface_Vessel:
    count: 15                     # 根据需要调整数量
    types:
      surveillance_usv: 8        # 调整各类型数量
      strike_usv: 5
      mine_hunting_usv: 2

# 修改部署计划
deployment_plan:
  primary_sector:
    coordinates: [30.0, -70.0]    # 根据作战区域调整
    radius_km: 200                # 调整作战半径

# 更新专家评估
expert_assessments:
  C1_1_Detection_Range:
    linguistic_term: "优"         # 根据实际情况评估
    confidence: 0.90
    justification: "配备了最新一代传感器"
```

### 2. 体系配置参数详解

#### 2.1 平台类型说明
```yaml
USV_Unmanned_Surface_Vessel:
  surveillance_usv: "侦察型 - 主要负责ISR任务"
  strike_usv: "攻击型 - 配备武器系统"
  mine_hunting_usv: "反水雷型 - 扫雷和排雷任务"
  support_usv: "支援型 - 后勤和支援任务"
  multirole_usv: "多功能型 - 具备多种能力"

UAV_Unmanned_Aerial_Vehicle:
  surveillance_uav: "侦察无人机"
  attack_uav: "攻击无人机"
  ew_uav: "电子战无人机"
  transport_uav: "运输无人机"
  multirole_uav: "多功能无人机"

UUV_Unmanned_Underwater_Vessel:
  surveillance_uuv: "侦察无人潜航器"
  mine_hunting_uuv: "反水雷无人潜航器"
  attack_uuv: "攻击无人潜航器"
  support_uuv: "支援无人潜航器"
  endurance_uuv: "长续航无人潜航器"
```

#### 2.2 部署计划配置
```yaml
deployment_plan:
  primary_sector:
    coordinates: [纬度, 经度]     # 作战中心点
    radius_km: 数值                # 作战半径(公里)

  secondary_sectors:              # 辅助作战区域
    - coordinates: [纬度, 经度]
      radius_km: 数值

  patrol_routes:                  # 巡逻路线
    - route_id: "路线ID"
      waypoints: [[纬度1, 经度1], [纬度2, 经度2], ...]
      patrol_type: "circular" | "figure_8" | "random"
      asset_assignment: ["平台ID1", "平台ID2", ...]
```

#### 2.3 任务分配配置
```yaml
task_assignments:
  surveillance_operations:
    primary_assets: ["平台类型列表"]
    coverage_requirement: 0.0-1.0   # 覆盖率要求
    endurance_hours: 数值           # 持续时间(小时)
    update_frequency_min: 数值      # 更新频率(分钟)

  anti_submarine_warfare:
    primary_assets: ["平台类型列表"]
    detection_probability: 0.0-1.0  # 探测概率要求
    patrol_density: 0.0-1.0        # 巡逻密度
    response_time_min: 数值        # 响应时间(分钟)

  mine_countermeasures:
    primary_assets: ["平台类型列表"]
    clearance_rate: 0.0-1.0        # 清除率要求
    area_coverage_km2: 数值        # 覆盖面积
    safety_radius_km: 数值          # 安全半径

  command_control:
    primary_assets: ["平台类型列表"]
    network_redundancy: 数值        # 网络冗余度
    bandwidth_mbps: 数值           # 带宽要求
    encryption_level: "加密级别"

  logistics_support:
    primary_assets: ["平台类型列表"]
    resupply_interval_hours: 数值   # 补给间隔
    fuel_autonomy_days: 数值       # 燃料自持力
    maintenance_spare_capacity: 数值 # 维修备件容量
```

#### 2.4 操作约束配置
```yaml
operational_constraints:
  total_platforms: 数值            # 平台总数限制
  max_budget_million_usd: 数值     # 最大预算(百万美元)
  deployment_area_km2: 数值        # 部署面积(平方公里)
  endurance_hours: 数值            # 持续作战时间(小时)
  communication_range_km: 数值     # 通信距离(公里)
  risk_tolerance: "LOW" | "MODERATE" | "HIGH"  # 风险容忍度
  rules_of_engagement: "交战规则"
  weather_limitations:             # 天气限制
    max_wind_speed_knots: 数值
    max_wave_height_m: 数值
    min_visibility_km: 数值
```

### 3. 专家评估配置

#### 3.1 指标评估格式
```yaml
expert_assessments:
  # 一级指标对应的二级指标评估
  C1_1_Detection_Range:           # 指标ID
    linguistic_term: "良"          # 语言变量: 差/中/良/优
    confidence: 0.85               # 置信度 [0.0-1.0]
    justification: "评估理由说明"

  C1_2_Coverage_Area:
    linguistic_term: "优"
    confidence: 0.90
    justification: "多平台协同覆盖"

  # ... 其他指标评估
```

#### 3.2 语言变量对应表
```
差 (Poor): 0.25
中 (Medium): 0.50
良 (Good): 0.75
优 (Excellent): 1.00
```

### 4. 配置验证

创建新配置后，务必进行验证：
```bash
# 验证方案配置
python main.py validate --scheme data/schemes/my_custom_scheme.yaml

# 验证后进行评估测试
python main.py evaluate --schemes data/schemes/my_custom_scheme.yaml --output outputs/results/my_custom_evaluation.json
```

---

## 🧬 遗传算法优化

### 1. 优化场景配置

#### 1.1 创建优化场景
**文件位置**: `data/scenarios/strait_control.yaml`

```yaml
scenario_id: "strait_control_optimization"
scenario_name: "海峡控制优化场景"
description: "针对海峡控制任务的体系配置优化"

# 操作约束
constraints:
  platform_limits:
    min: 10                       # 最小平台数量
    max: 30                       # 最大平台数量
  budget:
    max_budget_million_usd: 100.0 # 最大预算
  area_of_operations:
    description: "关键海峡区域"
    size_km2: 5000                # 作战区域面积
  duration_days: 30               # 任务持续时间

# 环境条件
environmental_conditions:
  sea_state: "rough"              # 海况: calm/moderate/rough
  visibility: "poor"              # 能见度: good/moderate/poor
  weather_impact_factor: 0.6     # 天气影响因子

# 任务需求
mission_requirements:
  primary_tasks:
    - surveillance                # 主要任务类型
    - anti_submarine_warfare
  secondary_tasks:
    - mine_countermeasures
  patrol_hours_per_day: 20        # 每日巡逻小时数
  response_time_minutes: 15       # 响应时间要求

# 威胁环境
threat_environment:
  threat_level: "high"            # 威胁等级: low/medium/high
  threat_types:
    - nuclear_submarines          # 威胁类型
    - missile_boats
    - naval_mines
  threat_density: "high"          # 威胁密度
```

### 2. 遗传算法参数配置

#### 2.1 基本优化命令
```bash
python main.py optimize --scenario data/scenarios/strait_control.yaml --population 20 --generations 50 --output outputs/results/optimization.json
```

#### 2.2 高级参数配置
```bash
python main.py optimize \
  --scenario data/scenarios/strait_control.yaml \
  --population 30 \                # 种群大小
  --generations 100 \              # 迭代代数
  --crossover-rate 0.8 \           # 交叉率
  --mutation-rate 0.1 \            # 变异率
  --elite-size 2 \                  # 精英个体数量
  --output outputs/results/advanced_optimization.json
```

### 3. 优化过程监控

#### 3.1 实时进度显示
优化过程中会显示实时进度：
```
Generation   5/ 50 | Best Fitness: 0.0010 | Avg Fitness: 0.0010 | Diversity: 0.549
Generation  10/ 50 | Best Fitness: 0.0015 | Avg Fitness: 0.0012 | Diversity: 0.476
Generation  15/ 50 | Best Fitness: 0.0020 | Avg Fitness: 0.0015 | Diversity: 0.423
...
Generation  50/ 50 | Best Fitness: 0.0035 | Avg Fitness: 0.0028 | Diversity: 0.387
```

**显示指标说明**:
- `Best Fitness`: 当前最佳适应度值 (越高越好)
- `Avg Fitness`: 平均适应度值
- `Diversity`: 种群多样性 (应保持>0.3)

#### 3.2 优化结果分析
```
============================================================
OPTIMIZATION RESULTS
============================================================
Best Configuration Fitness: 0.0035
Total Generations: 50
Converged: False
Monotonic Improvement: True
Final Population Diversity: 0.387

Best Configuration:
  Total Platforms: 22
  Deployment: [25.3, -80.7]
  Estimated Cost: $78.5M

Final Evaluation:
  Ci Score: 0.6234
  Rank: 1
  Validation: PASSED
```

### 4. 优化参数调优指南

#### 4.1 种群大小 (Population Size)
- **小规模问题** (变量<20): 20-30
- **中等规模问题** (变量20-50): 30-50
- **大规模问题** (变量>50): 50-100

#### 4.2 迭代代数 (Generations)
- **快速原型**: 20-50代
- **标准优化**: 50-100代
- **精细优化**: 100-200代

#### 4.3 交叉率 (Crossover Rate)
- **推荐范围**: 0.6-0.9
- **保守设置**: 0.6-0.7
- **激进设置**: 0.8-0.9

#### 4.4 变异率 (Mutation Rate)
- **推荐范围**: 0.01-0.2
- **保守设置**: 0.01-0.05
- **激进设置**: 0.1-0.2

#### 4.5 精英策略 (Elite Size)
- **推荐设置**: 种群大小的5-10%
- **小种群**: 1-2个精英
- **大种群**: 3-5个精英

### 5. 优化结果应用

#### 5.1 提取最优配置
优化完成后，结果文件中包含最优配置信息：
```json
{
  "best_configuration": {
    "platform_counts": {
      "USV_Unmanned_Surface_Vessel": 15,
      "UAV_Unmanned_Aerial_Vehicle": 10,
      "UUV_Unmanned_Underwater_Vessel": 8
    },
    "deployment_coordinates": [25.3, -80.7],
    "total_cost": 78.5,
    "fitness_score": 0.0035
  }
}
```

#### 5.2 转换为标准方案配置
手动将优化结果转换为标准的方案配置文件：
```yaml
scheme_id: "optimized_strait_control"
scheme_name: "优化后的海峡控制配置"
platform_inventory:
  USV_Unmanned_Surface_Vessel:
    count: 15
    types:
      surveillance_usv: 8
      strike_usv: 5
      mine_hunting_usv: 2
  # ... 其他平台配置
deployment_plan:
  primary_sector:
    coordinates: [25.3, -80.7]
    radius_km: 150
# ... 其他配置
```

### 6. 优化性能监控

#### 6.1 收敛性检查
- **收敛判断**: 连续10代无显著改善
- **多样性维持**: 种群多样性>0.3
- **单调改进**: 理想情况下适应度应单调提升

#### 6.2 性能基准
- **运行时间**: <5分钟 (标准参数)
- **内存使用**: <500MB
- **收敛代数**: 通常在50-100代内收敛

---

## 📊 结果文件说明

### 1. 输出文件结构

```
outputs/
├── outputs/results/                       # 评估结果文件 (JSON格式 + PNG图表)
│   ├── evaluation_*.json         # 单方案评估结果
│   ├── batch_evaluation.json     # 批量评估结果
│   ├── optimization_*.json       # 优化结果
│   ├── sensitivity_*.json        # 敏感性分析结果
│   ├── *_convergence.png         # 收敛曲线图
│   ├── comparison.png            # 方案对比图
│   ├── radar.png                 # 雷达图
│   └── sensitivity.png           # 敏感性分析图
├── reports/                       # 评估报告文件 (Markdown格式)
│   ├── evaluation_report.md      # 基础评估报告
│   ├── comprehensive_report.md   # 综合评估报告
│   └── sensitivity_report.md     # 敏感性分析报告
├── plots/                         # 图表文件 (PNG格式) [已迁移到outputs/results/]
└── DIRECTORY_STRUCTURE.md        # 目录结构说明文档
```

**注意**: 为统一管理，所有评估结果（包括JSON文件和图表）现在都存储在 `outputs/results/` 目录中。`plots/` 目录保留用于临时图表文件。

### 2. 评估结果文件详解

#### 2.1 单方案评估结果 (`outputs/results/evaluation_*.json`)
```json
{
  "scheme_id": "balanced_force",
  "scenario_id": "unknown",
  "ci_score": 0.5292,                    // TOPSIS得分
  "rank": 1,                             // 排名
  "indicator_values": {                  // 原始指标值
    "C1_1": 130.0,
    "C1_2": 0.25,
    // ... 其他指标
  },
  "normalized_values": [                 // 标准化值
    0.9333, 0.4472, // ...
  ],
  "weighted_values": [                   // 加权值
    0.2333, 0.0894, // ...
  ],
  "audit_trail": {                       // 审计轨迹
    "transformation_count": 3,
    "transformations": [
      {
        "stage": "AHP",
        "timestamp": "2025-10-25T13:48:34",
        "description": "AHP权重计算"
      },
      // ... 其他转换步骤
    ]
  },
  "validation": {
    "passed": true,
    "errors": [],
    "warnings": []
  },
  "evaluation_metadata": {
    "execution_time": 0.12,
    "algorithm_version": "1.0.0",
    "timestamp": "2025-10-25T13:48:34"
  }
}
```

#### 2.2 批量评估结果 (`outputs/results/batch_evaluation.json`)
```json
{
  "evaluation_summary": {
    "total_schemes": 3,
    "best_scheme": "high_endurance_force",
    "best_score": 0.5752,
    "evaluation_time": 0.35
  },
  "individual_results": {
    "balanced_force": {
      "ci_score": 0.5292,
      "rank": 2,
      // ... 详细结果 (同单方案格式)
    },
    "high_endurance_force": {
      "ci_score": 0.5752,
      "rank": 1,
      // ... 详细结果
    },
    "tech_lite_force": {
      "ci_score": 0.4369,
      "rank": 3,
      // ... 详细结果
    }
  },
  "ranking_analysis": {
    "score_distribution": {
      "mean": 0.5138,
      "std_dev": 0.0692,
      "min": 0.4369,
      "max": 0.5752
    },
    "ranking_stability": "stable"
  }
}
```

### 3. 优化结果文件详解

#### 3.1 遗传算法优化结果 (`outputs/results/optimization_*.json`)
```json
{
  "optimization_summary": {
    "scenario_id": "test_scenario_001",
    "total_generations": 50,
    "population_size": 15,
    "best_fitness": 0.0010,
    "converged": false,
    "execution_time": 45.2
  },
  "best_configuration": {
    "fitness_score": 0.0010,
    "platform_counts": {
      "USV_Unmanned_Surface_Vessel": 6,
      "UAV_Unmanned_Aerial_Vehicle": 8,
      "UUV_Unmanned_Underwater_Vessel": 5
    },
    "deployment_coordinates": [44.05, 57.99],
    "estimated_cost": 18.0,
    "constraint_satisfaction": {
      "platform_limit": "passed",
      "budget_limit": "passed",
      "area_constraint": "passed"
    }
  },
  "final_evaluation": {
    "ci_score": 0.4395,
    "rank": 1,
    "validation": "PASSED",
    "detailed_scores": {
      "C1_score": 0.4523,
      "C2_score": 0.4121,
      "C3_score": 0.3897,
      "C4_score": 0.4678,
      "C5_score": 0.4756
    }
  },
  "convergence_analysis": {
    "generations_to_convergence": null,
    "monotonic_improvement": true,
    "final_diversity": 0.525,
    "improvement_rate": 0.85
  },
  "generation_history": [
    {
      "generation": 1,
      "best_fitness": 0.0005,
      "avg_fitness": 0.0004,
      "diversity": 0.720
    },
    // ... 每代历史记录
    {
      "generation": 50,
      "best_fitness": 0.0010,
      "avg_fitness": 0.0008,
      "diversity": 0.525
    }
  ],
  "algorithm_parameters": {
    "crossover_rate": 0.8,
    "mutation_rate": 0.1,
    "elite_size": 2,
    "parent_selection_type": "sss"
  }
}
```

### 4. 敏感性分析结果详解

#### 4.1 敏感性分析结果 (`outputs/results/sensitivity_*.json`)
```json
{
  "analysis_summary": {
    "baseline_config": "balanced_force",
    "perturbation_level": 0.2,
    "iterations": 100,
    "ranking_stability": 0.87,
    "score_variance": 0.0234
  },
  "ranking_stability_analysis": {
    "original_rank": 1,
    "stable_iterations": 87,
    "stability_percentage": 87.0,
    "rank_changes": {
      "maintained_original": 87,
      "changed": 13
    }
  },
  "score_variation_analysis": {
    "baseline_score": 0.5292,
    "min_score": 0.4876,
    "max_score": 0.5623,
    "mean_score": 0.5289,
    "std_deviation": 0.0187,
    "coefficient_of_variation": 0.0354
  },
  "indicator_sensitivity": {
    "C1": {
      "sensitivity_index": 0.234,
      "impact_rank": 1,
      "weight_variations": [0.23, 0.27]
    },
    "C2": {
      "sensitivity_index": 0.189,
      "impact_rank": 2,
      "weight_variations": [0.18, 0.22]
    },
    // ... 其他指标敏感性
  },
  "robustness_metrics": {
    "overall_robustness": "high",
    "critical_indicators": ["C1", "C3"],
    "stable_indicators": ["C4", "C5"],
    "recommendations": [
      "重点关注C1和C3指标的权重设定",
      "C4和C5指标权重对结果影响较小"
    ]
  }
}
```

### 5. 评估报告文件详解

#### 5.1 Markdown报告 (`reports/comprehensive_report.md`)
报告包含以下章节：

```markdown
# AHP-FCE-TOPSIS-GA评估报告

## 执行摘要
- 评估目标和范围
- 主要发现和建议
- 关键性能指标

## 评估方法
### AHP层次分析法
- 权重计算过程
- 一致性检验结果
- 专家判断矩阵

### FCE模糊综合评价
- 语言变量定义
- 隶属度函数
- 评估结果

### TOPSIS排序方法
- 标准化过程
- 理想解识别
- 相对贴近度计算

## 评估结果
### 方案排名
| 排名 | 方案ID | Ci得分 | 状态 |
|------|--------|--------|------|

### 详细分析
- 各方案优势分析
- 指标表现对比
- 敏感性分析结果

## 敏感性分析
- 权重扰动影响
- 排名稳定性
- 关键指标识别

## 结论与建议
- 主要结论
- 改进建议
- 后续研究方向
```

### 6. 图表文件详解

#### 6.1 方案对比图 (`plots/comparison.png`)
- **图表类型**: 柱状图
- **内容**: 各方案Ci得分对比
- **用途**: 直观展示方案优劣

#### 6.2 雷达图 (`plots/radar.png`)
- **图表类型**: 雷达图
- **内容**: 多维度能力对比
- **用途**: 展示方案在不同指标上的表现

#### 6.3 收敛曲线图 (`plots/convergence.png`)
- **图表类型**: 折线图
- **内容**: 优化过程收敛情况
- **用途**: 分析算法性能

### 7. 结果文件使用指南

#### 7.1 查看评估结果
```bash
# 查看JSON结果
cat outputs/results/evaluation_balanced_force.json | jq '.ci_score'

# 查看报告
cat outputs/reports/comprehensive_report.md
```

#### 7.2 结果导出
```bash
# 导出为CSV格式
python -c "
import json, pandas as pd
data = json.load(open('outputs/results/batch_evaluation.json'))
df = pd.DataFrame(data['individual_results']).T
df.to_csv('outputs/results/evaluation_summary.csv')
"
```

#### 7.3 结果可视化
```python
import matplotlib.pyplot as plt
import json

# 加载结果
with open('outputs/results/batch_evaluation.json') as f:
    data = json.load(f)

# 提取数据
schemes = list(data['individual_results'].keys())
scores = [data['individual_results'][s]['ci_score'] for s in schemes]

# 绘制图表
plt.figure(figsize=(10, 6))
plt.bar(schemes, scores)
plt.title('方案评估结果对比')
plt.ylabel('Ci得分')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

---

## ❓ 常见问题解答

### Q1: 安装问题时如何解决？

**问题**: `ModuleNotFoundError: No module named 'numpy'`

**解决方案**:
```bash
# 重新安装依赖
pip install -r requirements.txt

# 或者使用conda
conda install numpy pandas matplotlib pyyaml
```

### Q2: AHP一致性检验失败怎么办？

**问题**: `Consistency Ratio (CR) >= 0.1, matrix rejected`

**解决方案**:
1. 检查判断矩阵是否满足互反性
2. 重新评估专家判断，减少逻辑不一致
3. 使用以下命令验证矩阵：
```bash
python main.py validate --ahp-matrix data/expert_judgments/primary_capabilities.yaml
```

### Q3: 评估结果Ci得分超出[0,1]范围？

**问题**: Ci得分不在预期范围内

**解决方案**:
1. 检查指标类型设置 (benefit/cost)
2. 验证权重归一化
3. 确认数据标准化正确性

### Q4: 遗传算法不收敛怎么办？

**问题**: 优化过程未收敛或结果不佳

**解决方案**:
1. 增加种群大小和迭代代数
2. 调整交叉率和变异率
3. 检查约束条件是否合理
```bash
# 使用更保守的参数
python main.py optimize --scenario data/scenarios/test_scenario.yaml \
  --population 50 --generations 200 --crossover-rate 0.7 --mutation-rate 0.05
```

### Q5: 如何添加新的评估指标？

**解决方案**:
1. 在`config/indicators.yaml`中添加新指标
2. 更新相应的专家判断矩阵
3. 在方案配置中添加专家评估
4. 重新运行评估验证

### Q6: 内存不足如何处理？

**问题**: 运行大数据集时内存不足

**解决方案**:
1. 减少种群大小和迭代代数
2. 分批处理评估方案
3. 清理输出目录中的临时文件

### Q7: 如何解释评估结果？

**指南**:
- **Ci得分**: 越接近1.0表示方案越优
- **排名**: 1表示最优方案
- **一致性比率**: CR<0.1表示判断矩阵有效
- **约束满足**: "PASSED"表示所有约束条件满足

### Q8: 如何自定义模糊评价集？

**解决方案**:
编辑`config/fuzzy_sets.yaml`:
```yaml
linguistic_scale:
  很差: {value: 0.0, description: "Very Poor"}
  差: {value: 0.25, description: "Poor"}
  中: {value: 0.5, description: "Medium"}
  良: {value: 0.75, description: "Good"}
  优: {value: 1.0, description: "Excellent"}
  很优: {value: 1.0, description: "Very Excellent"}
```

---

## 🎯 高级使用技巧

### 1. 批量处理自动化

#### 1.1 批量评估脚本
```bash
#!/bin/bash
# 批量评估脚本: batch_evaluate.sh

SCHEMES_DIR="data/schemes"
OUTPUT_DIR="outputs/results/batch_$(date +%Y%m%d_%H%M%S)"
mkdir -p $OUTPUT_DIR

echo "开始批量评估..."
count=0

for scheme in $SCHEMES_DIR/*.yaml; do
    if [[ -f "$scheme" ]]; then
        scheme_name=$(basename "$scheme" .yaml)
        echo "评估方案: $scheme_name"

        python main.py evaluate --schemes "$scheme" \
            --output "$OUTPUT_DIR/${scheme_name}_evaluation.json"

        ((count++))
    fi
done

echo "批量评估完成，共评估 $count 个方案"
echo "结果保存在: $OUTPUT_DIR"
```

#### 1.2 参数敏感性分析
```bash
#!/bin/bash
# 参数敏感性分析脚本: sensitivity_analysis.sh

BASE_SCHEME="data/schemes/balanced_force.yaml"
OUTPUT_DIR="outputs/results/sensitivity_$(date +%Y%m%d_%H%M%S)"
mkdir -p $OUTPUT_DIR

echo "开始敏感性分析..."

# 测试不同的扰动水平
for perturbation in 0.1 0.15 0.2 0.25 0.3; do
    echo "扰动水平: $perturbation"

    python main.py evaluate --schemes $BASE_SCHEME \
        --output "$OUTPUT_DIR/base_evaluation.json"

    python main.py sensitivity --baseline-results "$OUTPUT_DIR/base_evaluation.json" \
        --perturbation $perturbation --iterations 50 \
        --output "$OUTPUT_DIR/sensitivity_pert_${perturbation}.json"
done

echo "敏感性分析完成"
```

### 2. 结果对比分析

#### 2.1 Python脚本进行结果分析
```python
# results_analysis.py
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_evaluation_results(results_file):
    """分析评估结果"""
    with open(results_file) as f:
        data = json.load(f)

    if 'individual_results' in data:
        # 批量评估结果
        df = pd.DataFrame.from_dict(data['individual_results'], orient='index')

        print("=== 评估结果分析 ===")
        print(f"总方案数: {len(df)}")
        print(f"平均得分: {df['ci_score'].mean():.4f}")
        print(f"得分标准差: {df['ci_score'].std():.4f}")
        print(f"最高得分: {df['ci_score'].max():.4f}")
        print(f"最低得分: {df['ci_score'].min():.4f}")

        # 绘制得分分布
        plt.figure(figsize=(12, 8))

        # 子图1: 得分分布直方图
        plt.subplot(2, 2, 1)
        plt.hist(df['ci_score'], bins=10, alpha=0.7, edgecolor='black')
        plt.xlabel('Ci得分')
        plt.ylabel('方案数量')
        plt.title('得分分布')

        # 子图2: 得分排序
        plt.subplot(2, 2, 2)
        sorted_scores = df['ci_score'].sort_values(ascending=False)
        plt.bar(range(len(sorted_scores)), sorted_scores.values)
        plt.xlabel('方案排名')
        plt.ylabel('Ci得分')
        plt.title('方案得分排序')

        # 子图3: 累积分布
        plt.subplot(2, 2, 3)
        sorted_scores = df['ci_score'].sort_values()
        cumulative = np.arange(1, len(sorted_scores) + 1) / len(sorted_scores)
        plt.plot(sorted_scores, cumulative, marker='o')
        plt.xlabel('Ci得分')
        plt.ylabel('累积概率')
        plt.title('累积分布函数')

        # 子图4: 箱线图
        plt.subplot(2, 2, 4)
        plt.boxplot(df['ci_score'])
        plt.ylabel('Ci得分')
        plt.title('得分分布箱线图')

        plt.tight_layout()
        plt.savefig('analysis_results.png', dpi=300, bbox_inches='tight')
        plt.show()

        return df

    else:
        # 单方案评估结果
        print("=== 单方案评估结果 ===")
        print(f"方案ID: {data['scheme_id']}")
        print(f"Ci得分: {data['ci_score']:.4f}")
        print(f"排名: {data['rank']}")

        return None

if __name__ == "__main__":
    import sys
    results_file = sys.argv[1] if len(sys.argv) > 1 else "outputs/results/batch_evaluation.json"
    analyze_evaluation_results(results_file)
```

### 3. 自定义评估指标

#### 3.1 扩展指标体系
```yaml
# 在 config/indicators.yaml 中添加新指标
secondary_indicators:
  # C1 新增指标
  C1_4:
    name: "多源数据融合能力"
    description: "融合多源数据形成统一态势的能力"
    primary_capability: "C1"
    unit: "fusion_score"
    type: "benefit"
    fuzzy_evaluation: true
    weight: 0.06
    literature_reference: "数据融合技术 2023"

  # C2 新增指标
  C2_4:
    name: "智能决策支持能力"
    description: "AI辅助决策的能力"
    primary_capability: "C2"
    unit: "ai_score"
    type: "benefit"
    fuzzy_evaluation: true
    weight: 0.05
    literature_reference: "军事人工智能 2024"
```

#### 3.2 更新专家判断矩阵
```yaml
# 对应更新 data/expert_judgments/secondary_indicators/c1_indicators.yaml
matrix_id: "c1_secondary_indicators_updated"
dimension: 4  # 从3增加到4

# 更新4x4判断矩阵
matrix:
  - [1.0, 1.0, 0.5, 0.8]  # C1_1行，新增C1_4列
  - [1.0, 1.0, 0.5, 0.8]  # C1_2行
  - [2.0, 2.0, 1.0, 1.5]  # C1_3行
  - [1.25, 1.25, 0.67, 1.0]  # C1_4行

# 更新权重分布
weights: [0.22, 0.22, 0.30, 0.26]  # 重新分配权重
```

### 4. 性能优化技巧

#### 4.1 并行处理
```python
# parallel_evaluation.py
import multiprocessing as mp
import subprocess
import os

def evaluate_scheme(scheme_file):
    """单个方案评估"""
    try:
        output_file = f"outputs/results/{os.path.basename(scheme_file).replace('.yaml', '.json')}"
        cmd = f"python main.py evaluate --schemes {scheme_file} --output {output_file}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return scheme_file, result.returncode == 0
    except Exception as e:
        return scheme_file, False

def parallel_evaluate(scheme_files, num_processes=4):
    """并行评估多个方案"""
    with mp.Pool(num_processes) as pool:
        results = pool.map(evaluate_scheme, scheme_files)

    successful = [r[0] for r in results if r[1]]
    failed = [r[0] for r in results if not r[1]]

    print(f"成功评估: {len(successful)} 个方案")
    print(f"评估失败: {len(failed)} 个方案")

    return successful, failed

if __name__ == "__main__":
    import glob
    scheme_files = glob.glob("data/schemes/*.yaml")
    parallel_evaluate(scheme_files)
```

#### 4.2 内存优化
```python
# memory_optimized_evaluation.py
import gc
import json

def memory_efficient_evaluation(scheme_files):
    """内存优化的批量评估"""
    results = {}

    for i, scheme_file in enumerate(scheme_files):
        print(f"评估方案 {i+1}/{len(scheme_files)}: {scheme_file}")

        # 评估单个方案
        result = evaluate_single_scheme(scheme_file)
        results[scheme_file] = result

        # 定期清理内存
        if i % 10 == 0:
            gc.collect()

        # 保存中间结果
        if i % 5 == 0:
            with open(f"outputs/results/intermediate_{i}.json", 'w') as f:
                json.dump(results, f, indent=2)

    return results
```

### 5. 结果导出和分享

#### 5.1 生成Excel报告
```python
# export_to_excel.py
import pandas as pd
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.chart import BarChart, Reference

def create_excel_report(evaluation_file, output_file):
    """创建Excel格式的评估报告"""
    # 加载数据
    with open(evaluation_file) as f:
        data = json.load(f)

    if 'individual_results' not in data:
        print("需要批量评估结果文件")
        return

    # 创建Excel工作簿
    wb = Workbook()
    ws = wb.active
    ws.title = "评估结果"

    # 写入数据
    results = data['individual_results']
    rows = []
    for scheme_id, result in results.items():
        rows.append({
            '方案ID': scheme_id,
            'Ci得分': result['ci_score'],
            '排名': result['rank'],
            '验证状态': 'PASSED' if result['validation']['passed'] else 'FAILED'
        })

    df = pd.DataFrame(rows)
    df = df.sort_values('排名')

    # 写入工作表
    for r in dataframe_to_rows(df):
        ws.append(r)

    # 设置样式
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")

    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill

    # 创建图表
    chart = BarChart()
    data = Reference(ws, min_col=2, min_row=1, max_row=len(df)+1, max_col=2)
    categories = Reference(ws, min_col=1, min_row=2, max_row=len(df)+1)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categories)
    chart.title = "方案评估结果对比"

    ws.add_chart(chart, "G2")

    # 保存文件
    wb.save(output_file)
    print(f"Excel报告已保存: {output_file}")

if __name__ == "__main__":
    create_excel_report("outputs/results/batch_evaluation.json", "reports/evaluation_report.xlsx")
```

---

## 📞 技术支持

### 联系方式
- **项目仓库**: [GitHub链接]
- **问题反馈**: 通过Issues提交
- **技术文档**: 参见README.md和代码注释

### 常用命令快速参考
```bash
# 系统信息
python main.py --version

# 配置验证
python main.py validate --scheme data/schemes/balanced_force.yaml
python main.py validate --ahp-matrix data/expert_judgments/primary_capabilities.yaml

# 基础评估
python main.py evaluate --schemes data/schemes/balanced_force.yaml --output outputs/results/balanced_evaluation.json
python main.py evaluate --schemes data/schemes/*.yaml --batch --output outputs/results/batch_evaluation.json

# 场景化评估（v1.1.0新增）
python main.py evaluate --schemes data/schemes/balanced_force.yaml --scenario data/scenarios/operational/nearshore_underwater_recon.yaml --output outputs/results/scenario_evaluation.json

# 优化分析
python main.py optimize --scenario data/scenarios/operational/nearshore_underwater_recon.yaml --population 20 --generations 50 --output outputs/results/optimization.json

# 可视化和报告
python main.py visualize --plot-type comparison --input outputs/results/evaluation.json --output outputs/results/comparison_chart.png
python main.py report --results outputs/results/evaluation.json --include-methodology --output outputs/reports/comprehensive_report.md

# 敏感性分析
python main.py sensitivity --baseline-results outputs/results/evaluation.json --perturbation 0.2 --output outputs/results/sensitivity_analysis.json

# 创建示例配置
python main.py setup
```

---

## 🔧 故障排除与最佳实践

### 常见问题解决

#### 1. 评估结果异常
**问题**: 所有方案获得相同的Ci Score
**解决方案**:
- 检查指标数据是否正确输入
- 验证AHP判断矩阵的一致性（CR < 0.1）
- 确认TOPSIS权重归一化是否正确

```bash
# 验证AHP矩阵
python main.py validate --ahp-matrix data/expert_judgments/primary_capabilities.yaml

# 查看详细评估过程
python main.py evaluate --schemes data/schemes/balanced_force.yaml --verbose
```

#### 2. 场景化评估问题
**问题**: 场景化评估与通用评估结果相同
**解决方案**:
- 确认场景文件路径正确
- 检查场景配置中的适用指标设置
- 验证场景权重调整是否生效

```bash
# 验证场景配置
python main.py validate --scenario data/scenarios/operational/nearshore_underwater_recon.yaml

# 比较评估结果
python main.py evaluate --schemes data/schemes/balanced_force.yaml --output generic_result.json
python main.py evaluate --schemes data/schemes/balanced_force.yaml --scenario data/scenarios/operational/nearshore_underwater_recon.yaml --output scenario_result.json
```

#### 3. 遗传算法优化问题
**问题**: 优化过程收敛过早或结果不理想
**解决方案**:
- 增加种群大小和迭代次数
- 调整变异率和交叉率参数
- 检查约束条件是否合理

```bash
# 使用更大参数运行优化
python main.py optimize --scenario data/scenarios/operational/nearshore_underwater_recon.yaml \
  --population 50 --generations 100 --mutation-rate 0.15 --crossover-rate 0.8
```

#### 4. 输出文件问题
**问题**: 结果文件生成失败或格式错误
**解决方案**:
- 确保输出目录存在且有写权限
- 检查磁盘空间是否充足
- 验证输入配置文件格式正确

### 系统性能优化

#### 1. 大规模评估优化
- 使用批量评估模式减少重复计算
- 启用多进程处理（`--parallel`参数）
- 合理设置GA算法参数避免过早收敛

#### 2. 内存使用优化
- 及时清理大型数据集
- 使用分块处理处理多方案比较
- 监控内存使用情况

### 数据验证建议

#### 1. AHP判断矩阵验证
```python
# 检查一致性比例
CR = calculate_consistency_ratio(matrix)
if CR > 0.1:
    print("警告：判断矩阵一致性不足，建议调整")
```

#### 2. 指标数据验证
```python
# 检查数据完整性和合理性
def validate_indicators(data):
    for key, value in data.items():
        if value <= 0 or not isinstance(value, (int, float)):
            raise ValueError(f"指标 {key} 数值异常: {value}")
```

### 模型使用建议

#### 1. 场景选择指导
- **近岸水下侦察**: 优先配置侦察平台和水下装备
- **海峡要道控守**: 重点配置防空和反舰能力
- **登陆场通道清扫**: 加强反潜和反水雷能力
- **要害目标封锁**: 均衡配置攻击和防御能力

#### 2. 参数调优策略
- 根据任务重要性调整AHP权重
- 根据环境特点选择模糊评价标准
- 根据预算约束设置GA优化目标

#### 3. 结果解释建议
- 关注Ci Score的相对排序而非绝对值
- 结合评估审计日志分析关键因素
- 考虑场景适应性对结果的影响

---

**版本**: 1.1.0
**最后更新**: 2025-10-26
**文档维护**: kai