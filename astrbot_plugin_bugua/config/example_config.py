"""卜卦插件 - 高级配置示例

复制此文件内容到 config/settings.py 中进行自定义配置
"""

class PuguaConfigAdvanced:
    """卜卦插件高级配置类 - 示例"""

    def __init__(self):
        # ============== 卜卦方式配置 ==============
        
        # 八卦卜卦配置
        self.enable_bagua = True              # 启用八卦卜卦
        self.bagua_detail = True              # 显示详细解读
        
        # 六爻卜卦配置
        self.enable_liuyao = True             # 启用六爻卜卦
        self.show_changing_yao = True         # 显示变爻
        
        # 塔罗卜卦配置
        self.enable_tarot = True              # 启用塔罗卜卦
        
        # 硬币卜卦配置
        self.enable_coin = True               # 启用硬币卜卦
        self.show_coin_animation = True       # 显示投掷动画
        
        # ============== 显示配置 ==============
        
        # 返回结果详细程度
        self.detail_level = "详细"            # 可选: "简洁" 或 "详细"
                                              # 简洁: 仅显示运势等级
                                              # 详细: 显示完整解读和建议
        
        # 是否包含建议
        self.show_advice = True               # 显示卜卦建议
        
        # 是否显示运势图表
        self.show_image = True                # 显示运势信息
        
        # 是否显示五行属性
        self.show_five_elements = True        # 显示五行信息
        
        # 是否显示方位信息
        self.show_direction = True            # 显示卦象方位
        
        # ============== 功能配置 ==============
        
        # 启用周运势预报
        self.enable_weekly = True             # 启用周运势功能
        
        # 启用生日运势预测
        self.enable_birthday = True           # 启用生日运势功能
        
        # 启用智能建议
        self.enable_smart_suggestion = True   # 匹配"今天吃什么"等
        
        # 启用帮助命令
        self.enable_help = True               # 启用 /帮助 命令
        
        # ============== 输出格式配置 ==============
        
        # 是否使用Emoji
        self.use_emoji = True                 # 使用表情符号
        
        # 是否显示分隔线
        self.show_separator = True            # 显示装饰分隔线
        
        # 输出颜色
        self.use_color = True                 # 是否支持颜色输出
        
        # ============== 其他配置 ==============
        
        # 缓存卜卦结果
        self.cache_results = False            # 缓存结果以提高速度
        
        # 记录卜卦日志
        self.log_divinations = True           # 记录用户卜卦日志
        
        # 最大缓存数量
        self.max_cache = 1000                 # 最多缓存1000条结果

    def validate(self):
        """验证配置"""
        # 验证detail_level
        if self.detail_level not in ["简洁", "详细"]:
            self.detail_level = "详细"
        
        # 将布尔值转为bool类型
        self.enable_bagua = bool(self.enable_bagua)
        self.enable_liuyao = bool(self.enable_liuyao)
        self.enable_tarot = bool(self.enable_tarot)
        self.enable_coin = bool(self.enable_coin)
        self.show_advice = bool(self.show_advice)
        self.show_image = bool(self.show_image)


# ============== 配置使用示例 ==============

# 1. 最简单的配置（仅八卦卜卦）
class MinimalConfig:
    """最小化配置"""
    def __init__(self):
        self.enable_bagua = True
        self.enable_liuyao = False
        self.enable_tarot = False
        self.enable_coin = False
        self.detail_level = "简洁"
        self.show_advice = False


# 2. 完整功能配置
class FullFeatureConfig:
    """完整功能配置"""
    def __init__(self):
        self.enable_bagua = True
        self.enable_liuyao = True
        self.enable_tarot = True
        self.enable_coin = True
        self.detail_level = "详细"
        self.show_advice = True
        self.show_image = True
        self.enable_weekly = True
        self.enable_birthday = True
        self.enable_smart_suggestion = True


# 3. 娱乐模式配置
class FunModeConfig:
    """娱乐模式（更多Emoji和装饰）"""
    def __init__(self):
        self.enable_bagua = True
        self.detail_level = "详细"
        self.show_advice = True
        self.use_emoji = True
        self.show_separator = True
        self.use_color = True


# ============== 快速切换方法 ==============

def get_config_by_mode(mode: str):
    """根据模式获取配置
    
    Args:
        mode: 配置模式 - minimal/full/fun/advanced
        
    Returns:
        配置对象
    """
    mode_map = {
        "minimal": MinimalConfig,
        "full": FullFeatureConfig,
        "fun": FunModeConfig,
        "advanced": PuguaConfigAdvanced,
    }
    
    config_class = mode_map.get(mode, PuguaConfigAdvanced)
    return config_class()


# ============== 配置环境变量支持 ==============

import os

def get_config_from_env():
    """从环境变量读取配置"""
    config = PuguaConfigAdvanced()
    
    # 从环境变量读取配置
    config.detail_level = os.getenv("PUGUA_DETAIL", "详细")
    config.enable_bagua = os.getenv("PUGUA_BAGUA", "true").lower() == "true"
    config.enable_coin = os.getenv("PUGUA_COIN", "true").lower() == "true"
    config.enable_liuyao = os.getenv("PUGUA_LIUYAO", "true").lower() == "true"
    config.enable_tarot = os.getenv("PUGUA_TAROT", "true").lower() == "true"
    
    return config


if __name__ == "__main__":
    # 测试配置
    print("━━━━━━━━━━━━━━━━━━━━━")
    print("卜卦插件配置示例")
    print("━━━━━━━━━━━━━━━━━━━━━\n")
    
    # 最小化配置
    config1 = MinimalConfig()
    print("✓ 最小化配置已加载")
    print(f"  - 八卦卜卦: {config1.enable_bagua}")
    print(f"  - 详细程度: {config1.detail_level}\n")
    
    # 完整功能配置
    config2 = FullFeatureConfig()
    print("✓ 完整功能配置已加载")
    print(f"  - 启用功能数: 4\n")
    
    # 高级配置
    config3 = PuguaConfigAdvanced()
    print("✓ 高级配置已加载")
    print(f"  - 详细程度: {config3.detail_level}")
    print(f"  - 使用Emoji: {config3.use_emoji}\n")
    
    print("━━━━━━━━━━━━━━━━━━━━━")
    print("配置加载完成！")
    print("━━━━━━━━━━━━━━━━━━━━━")
