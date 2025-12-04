# AHP-FCE-TOPSIS-GA 无人作战体系效能评估系统
## 简易用户手册

### 📁 项目目录结构

```
ahp_fce_topsis/
├── 📄 main.py                          # 主程序入口
├── 📄 requirements.txt                 # 依赖包列表
├── 📄 USER_MANUAL.md                  # 详细用户手册
│
├── 📁 config/                          # 配置文件目录
│   ├── 📄 indicators.yaml             # 指标体系配置
│   └── 📄 fuzzy_sets.yaml             # 模糊评价集配置
│
├── 📁 data/                            # 数据文件目录
│   ├── 📁 expert_judgments/           # 专家判断矩阵
│   ├── 📁 scenarios/                   # 场景配置目录
│   │   ├── 📄 strait_control.yaml              # 示例场景
│   │   └── 📁 operational/                     # 作战场景
│   │       ├── 📄 nearshore_underwater_recon.yaml    # 近岸水下侦察监视
│   │       ├── 📄 strait_control_defense.yaml          # 海峡要道控守
│   │       ├── 📄 amphibious_landing_clearance.yaml    # 登陆场通道清扫
│   │       ├── 📄 high_value_target_blockade.yaml      # 要害目标封锁
│   │       └── 📄 README.md                           # 场景说明
│   └── 📁 schemes/                    # 体系配置方案
│       ├── 📄 balanced_force.yaml           # 均衡力量配置
│       ├── 📄 high_endurance_force.yaml     # 高续航力量配置
│       ├── 📄 tech_lite_force.yaml          # 技术精简力量配置
│       ├── 📄 simple_template.yaml          # 简单模板
│       └── 📄 template_scheme.yaml          # 详细模板
│
├── 📁 modules/                         # 核心算法模块
├── 📁 utils/                           # 工具函数
├── 📁 tests/                           # 测试文件
└── 📁 outputs/                         # 输出结果目录
    └── 📁 results/                      # 评估结果文件
```

### 🚀 常见使用命令

#### 1. 环境安装
```bash
# 安装依赖
pip install -r requirements.txt

# 检查安装
python main.py --help
```

#### 2. 方案评估

**单方案评估（无场景）**
```bash
python main.py evaluate --schemes data/schemes/balanced_force.yaml
```

**单方案评估（带场景）**
```bash
# 近岸水下侦察监视场景
python main.py evaluate --schemes data/schemes/balanced_force.yaml \
  --scenario data/scenarios/operational/nearshore_underwater_recon.yaml

# 海峡要道控守场景
python main.py evaluate --schemes data/schemes/balanced_force.yaml \
  --scenario data/scenarios/operational/strait_control_defense.yaml
```

**多方案批量评估**
```bash
# 带场景的批量评估
python main.py evaluate --schemes scheme1.yaml scheme2.yaml scheme3.yaml \
  --scenario data/scenarios/operational/nearshore_underwater_recon.yaml --batch

# 无场景的批量评估
python main.py evaluate --schemes data/schemes/balanced_force.yaml \
  data/schemes/high_endurance_force.yaml data/schemes/tech_lite_force.yaml --batch
```

**输出到文件**
```bash
python main.py evaluate --schemes data/schemes/balanced_force.yaml \
  --output outputs/results/balanced_evaluation.json
```

#### 3. 遗传算法优化

**基础优化**
```bash
python main.py optimize --scenario data/scenarios/operational/nearshore_underwater_recon.yaml \
  --population 30 --generations 50 --output outputs/results/optimization.json
```

**高级优化**
```bash
# 大规模优化
python main.py optimize --scenario data/scenarios/operational/strait_control_defense.yaml \
  --population 50 --generations 100 --output outputs/results/advanced_optimization.json

# 快速测试
python main.py optimize --scenario data/scenarios/operational/amphibious_landing_clearance.yaml \
  --population 20 --generations 20
```

#### 4. 敏感性分析
```bash
# 基于已有结果进行敏感性分析
python main.py sensitivity --baseline-results outputs/results/balanced_evaluation.json \
  --perturbation 0.2 --iterations 100 --output outputs/results/sensitivity.json
```

#### 5. 配置文件操作

**验证配置文件**
```bash
python main.py validate --schemes data/schemes/balanced_force.yaml
```

**创建示例配置**
```bash
python main.py setup --type template
```

### 🎯 四类作战场景

| 场景类型 | 文件 | 特点 |
|----------|------|------|
| **近岸水下侦察监视** | `nearshore_underwater_recon.yaml` | 侦察能力优先 |
| **海峡要道控守** | `strait_control_defense.yaml` | 防御打击优先 |
| **登陆场通道清扫** | `amphibious_landing_clearance.yaml` | 清障作业优先 |
| **要害目标封锁** | `high_value_target_blockade.yaml` | 监视拦截优先 |

### 📊 输出结果文件

系统会生成以下输出文件：
- **JSON结果文件**：包含详细的评估数据
- **收敛图**：PNG格式的优化收敛曲线
- **审计日志**：完整的评估过程记录

### ⚠️ 常见问题

**Q: 所有场景给出相同的Ci Score怎么办？**
A: 这是正常的，说明方案在各个场景下都表现良好。可以尝试不同的方案配置来观察差异。

**Q: 如何自定义方案？**
A: 复制 `data/schemes/simple_template.yaml` 并修改参数，或者参考 `data/schemes/` 目录下的示例。

**Q: 评估结果在哪里？**
A: 默认输出到 `outputs/results/` 目录，可以使用 `--output` 参数指定位置。

### 🔧 快速开始示例

```bash
# 1. 安装环境
pip install -r requirements.txt

# 2. 测试单方案评估
python main.py evaluate --schemes data/schemes/balanced_force.yaml

# 3. 测试场景化评估
python main.py evaluate --schemes data/schemes/balanced_force.yaml \
  --scenario data/scenarios/operational/nearshore_underwater_recon.yaml

# 4. 测试GA优化
python main.py optimize --scenario data/scenarios/operational/nearshore_underwater_recon.yaml \
  --population 30 --generations 10

# 5. 测试批量评估
python main.py evaluate --schemes data/schemes/balanced_force.yaml \
  data/schemes/high_endurance_force.yaml --batch
```

---
**版本**: 1.0 | **更新日期**: 2025-10-25