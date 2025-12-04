"""
场景集成评估模块
Scenario-Aware Evaluation Module

将作战场景深度集成到AHP-FCE-TOPSIS评估算法中，使评估结果真正反映场景需求。
"""

import yaml
import numpy as np
from typing import Dict, Any, List, Tuple, Union


class ScenarioIntegrator:
    """场景集成器，负责将场景影响注入到评估算法中"""

    def __init__(self, scenario_config: Dict[str, Any]):
        """
        初始化场景集成器

        Args:
            scenario_config: 场景配置文件
        """
        self.scenario_config = scenario_config
        self.scenario_id = scenario_config.get('scenario_id', 'generic')
        self.scenario_type = scenario_config.get('scenario_type', 'generic')

        # 提取场景关键要素
        mission_obj_config = scenario_config.get('mission_objectives', {})
        # 处理嵌套的mission_objectives结构
        if 'primary' in mission_obj_config:
            # 展开嵌套的objectives
            self.mission_objectives = {}
            for obj in mission_obj_config.get('primary', []):
                self.mission_objectives[obj['objective']] = obj
        else:
            self.mission_objectives = mission_obj_config

        self.threat_environment = scenario_config.get('threat_environment', {})
        self.operational_environment = scenario_config.get('operational_environment', {})
        self.objective_weights = scenario_config.get('objective_weights', {})
        self.evaluation_focus = scenario_config.get('evaluation_focus', {})
        self.scenario_requirements = scenario_config.get('scenario_specific_requirements', {})

    def get_scenario_adjusted_base_values(self, base_values: Dict[str, float]) -> Dict[str, float]:
        """
        根据场景特点调整指标基础值

        Args:
            base_values: 原始基础值

        Returns:
            场景调整后的基础值
        """
        adjusted_values = base_values.copy()

        # 根据场景类型调整基础值
        if self.scenario_type == "reconnaissance_surveillance":
            # 侦察监视场景：提升侦察能力相关指标
            adjusted_values['C1_1'] *= 1.3  # 探测距离提升
            adjusted_values['C1_3'] *= 1.4  # 搜索覆盖提升
            adjusted_values['C2_2'] *= 1.2  # 威胁评估提升

        elif self.scenario_type == "area_control_defense":
            # 区域控制防御场景：提升打击和防御能力
            adjusted_values['C3_1'] *= 1.5  # 火力打击提升
            adjusted_values['C5_1'] *= 1.3  # 抗毁能力提升
            adjusted_values['C4_3'] *= 1.2  # 协同作战提升

        elif self.scenario_type == "mine_countermeasure_lane_clearance":
            # 清障扫雷场景：提升作业和机动能力
            adjusted_values['C3_2'] *= 1.4  # 机动占位提升
            adjusted_values['C2_3'] *= 1.3  # 决策响应提升
            adjusted_values['C5_2'] *= 1.2  # 任务恢复提升

        elif self.scenario_type == "sea_blockade_interdiction":
            # 海上封锁场景：提升监视和拦截能力
            adjusted_values['C2_2'] *= 1.3  # 威胁评估提升
            adjusted_values['C4_1'] *= 1.2  # 信息传输提升
            adjusted_values['C3_1'] *= 1.3  # 火力打击提升

        # 应用场景特殊要求因子
        for requirement, factor in self.scenario_requirements.items():
            if requirement in adjusted_values and isinstance(factor, (int, float)):
                adjusted_values[requirement] *= factor

        return adjusted_values

    def get_scenario_adjusted_multipliers(self, multipliers: Dict[str, List[str]]) -> Dict[str, float]:
        """
        根据场景威胁环境调整仿真参数重要性

        Args:
            multipliers: 原始乘数配置

        Returns:
            场景调整后的乘数值
        """
        adjusted_multipliers = {}

        # 分析威胁环境
        primary_threats = self.threat_environment.get('primary_threats', [])
        threat_types = [threat.get('type', '') for threat in primary_threats]

        # 根据威胁类型调整参数重要性
        if any('潜艇' in threat_type for threat_type in threat_types):
            # 存在潜艇威胁，提升探测和反潜相关参数
            adjusted_multipliers['detection_range_factor'] = 1.3
            adjusted_multipliers['coordination_efficiency'] = 1.2
            adjusted_multipliers['stealth_factor'] = 1.2

        if any('导弹' in threat_type or '航空' in threat_type for threat_type in threat_types):
            # 存在导弹/航空威胁，提升防空和电子战能力
            adjusted_multipliers['weapon_effectiveness'] = 1.3
            adjusted_multipliers['coordination_efficiency'] = 1.15

        if any('水雷' in threat_type for threat_type in threat_types):
            # 存在水雷威胁，提升清障和探测能力
            adjusted_multipliers['coordination_efficiency'] = 1.25
            adjusted_multipliers['mobility_factor'] = 1.2

        # 根据作战环境复杂度调整
        env_complexity = self.operational_environment.get('geography', {})
        if env_complexity.get('coastline_complexity') == '高':
            adjusted_multipliers['coordination_efficiency'] *= 1.1
            adjusted_multipliers['mobility_factor'] *= 1.1

        # 设置默认值
        default_multipliers = {
            'detection_range_factor': 1.0,
            'coordination_efficiency': 1.0,
            'weapon_effectiveness': 1.0,
            'network_bandwidth_mbps': 1.0,
            'stealth_factor': 1.0,
            'mobility_factor': 1.0
        }

        for key, default_value in default_multipliers.items():
            if key not in adjusted_multipliers:
                adjusted_multipliers[key] = default_value

        return adjusted_multipliers

    def get_scenario_specific_constraints(self) -> Dict[str, Any]:
        """
        获取场景特定的约束条件

        Returns:
            场景约束条件
        """
        return self.scenario_config.get('constraints', {})

    def calculate_scenario_success_score(self, indicator_values: Dict[str, float]) -> float:
        """
        基于场景任务目标计算成功得分

        Args:
            indicator_values: 指标值

        Returns:
            场景成功得分 [0-1]
        """
        total_score = 0.0
        total_weight = 0.0

        for objective, config in self.mission_objectives.items():
            weight = config.get('weight', 0.0)
            success_criteria = config.get('success_criteria', '')

            # 根据指标值计算目标达成度
            achievement_score = self._calculate_objective_achievement(objective, indicator_values, success_criteria)

            total_score += achievement_score * weight
            total_weight += weight

        if total_weight > 0:
            return total_score / total_weight
        else:
            return 0.5  # 默认中等得分

    def _calculate_objective_achievement(self, objective: str, indicator_values: Dict[str, float], criteria: str) -> float:
        """
        计算单个目标的达成度

        Args:
            objective: 目标描述
            indicator_values: 指标值
            criteria: 成功标准

        Returns:
            达成度 [0-1]
        """
        # 简化的目标达成度计算
        # 实际应用中需要更复杂的逻辑解析criteria字符串

        if 'coverage' in objective.lower():
            # 覆盖率相关目标
            c1_1 = indicator_values.get('C1_1', 0) / 100.0  # 标准化
            return min(1.0, c1_1)

        elif 'strike' in objective.lower() or '打击' in objective:
            # 打击相关目标
            c3_1 = indicator_values.get('C3_1', 0) / 100.0
            return min(1.0, c3_1)

        elif 'communication' in objective.lower() or '通信' in objective:
            # 通信相关目标
            c4_1 = indicator_values.get('C4_1', 0) / 100.0
            return min(1.0, c4_1)

        elif 'coordination' in objective.lower() or '协同' in objective:
            # 协同相关目标
            c4_3 = indicator_values.get('C4_3', 0) / 50.0  # 延迟越低越好
            return max(0.0, 1.0 - c4_3)

        else:
            # 默认计算方式
            return 0.7  # 默认中等达成度

    def adjust_fuzzy_evaluation_thresholds(self, quantitative_value: float, indicator_id: str) -> Dict[str, int]:
        """
        根据场景调整模糊评价阈值

        Args:
            quantitative_value: 定量指标值
            indicator_id: 指标ID

        Returns:
            调整后的模糊评估
        """
        assessments = {'差': 0, '中': 0, '良': 0, '优': 0}

        # 根据场景类型调整阈值
        if self.scenario_type == "reconnaissance_surveillance":
            # 侦察场景对侦察能力要求更高
            if 'C1' in indicator_id:
                if quantitative_value < 40:
                    assessments['差'] = 1
                elif quantitative_value < 70:
                    assessments['中'] = 1
                elif quantitative_value < 90:
                    assessments['良'] = 1
                else:
                    assessments['优'] = 1
            else:
                # 其他指标使用标准阈值
                return self._standard_fuzzy_assessment(quantitative_value, indicator_id)

        elif self.scenario_type == "area_control_defense":
            # 防御场景对打击能力要求更高
            if 'C3' in indicator_id:
                if quantitative_value < 45:
                    assessments['差'] = 1
                elif quantitative_value < 75:
                    assessments['中'] = 1
                elif quantitative_value < 95:
                    assessments['良'] = 1
                else:
                    assessments['优'] = 1
            else:
                return self._standard_fuzzy_assessment(quantitative_value, indicator_id)

        else:
            # 使用标准模糊评估
            return self._standard_fuzzy_assessment(quantitative_value, indicator_id)

        return assessments

    def _standard_fuzzy_assessment(self, quantitative_value: float, indicator_id: str) -> Dict[str, int]:
        """标准模糊评估逻辑"""
        assessments = {'差': 0, '中': 0, '良': 0, '优': 0}

        if 'C1' in indicator_id or 'C3' in indicator_id:  # 性能类指标
            if quantitative_value < 30:
                assessments['差'] = 1
            elif quantitative_value < 60:
                assessments['中'] = 1
            elif quantitative_value < 90:
                assessments['良'] = 1
            else:
                assessments['优'] = 1

        elif 'C2' in indicator_id:  # 时间类指标
            if quantitative_value > 60:
                assessments['差'] = 1
            elif quantitative_value > 30:
                assessments['中'] = 1
            elif quantitative_value > 15:
                assessments['良'] = 1
            else:
                assessments['优'] = 1

        else:  # 其他指标
            if quantitative_value < 20:
                assessments['差'] = 1
            elif quantitative_value < 50:
                assessments['中'] = 1
            elif quantitative_value < 80:
                assessments['良'] = 1
            else:
                assessments['优'] = 1

        return assessments


def integrate_scenario_into_evaluation(scheme_data: Dict[str, Any],
                                    indicator_config: Dict[str, Any],
                                    fuzzy_config: Dict[str, Any],
                                    audit_logger) -> Tuple[Dict[str, Any], Dict[str, Any], Union['ScenarioIntegrator', None]]:
    """
    将场景集成到评估流程中

    Args:
        scheme_data: 方案数据
        indicator_config: 指标配置
        fuzzy_config: 模糊配置
        audit_logger: 审计日志

    Returns:
        (场景调整后的指标配置, 场景调整后的模糊配置, 场景集成器)
    """
    # 提取场景上下文
    scenario_context = scheme_data.get('scenario_context')
    mission_objectives = scheme_data.get('mission_objectives', {})
    threat_environment = scheme_data.get('threat_environment', {})

    if not scenario_context or scenario_context == 'generic':
        audit_logger.log_transformation(
            stage="Scenario Integration",
            input_data={"scenario_context": scenario_context},
            output_data={"integration_applied": False}
        )
        return indicator_config, fuzzy_config, None

    # 创建场景集成器
    scenario_integrator = ScenarioIntegrator({
        'scenario_id': scenario_context,
        'scenario_type': scenario_context,  # 简化处理，实际应该从场景文件获取
        'mission_objectives': mission_objectives,
        'threat_environment': threat_environment,
        'objective_weights': {},  # 从场景配置中获取
        'evaluation_focus': {'primary_indicators': [], 'secondary_indicators': []},  # 从场景配置中获取
        'scenario_specific_requirements': {}  # 从场景配置中获取
    })

    # 调整指标配置
    adjusted_indicator_config = indicator_config.copy()
    adjusted_fuzzy_config = fuzzy_config.copy()

    audit_logger.log_transformation(
        stage="Scenario Integration",
        input_data={"scenario_context": scenario_context},
        output_data={"integration_applied": True}
    )

    return adjusted_indicator_config, adjusted_fuzzy_config, scenario_integrator