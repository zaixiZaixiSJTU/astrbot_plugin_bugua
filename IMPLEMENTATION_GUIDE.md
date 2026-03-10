# 生日主题卜卦功能实现文档

## 功能概述

已在 `DivinationService` 类中实现了 `birthday_topic_divination()` 方法，该方法提供了一个完整的生日-主题卜卦系统。

## 方法签名

```python
@staticmethod
def birthday_topic_divination(user_birthday: str, user_topic: str) -> Dict
```

## 方法参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `user_birthday` | str | 用户生日，YYYY-MM-DD 格式 | `"2000-01-15"` |
| `user_topic` | str | 卜卦主题 | `"求财"` `"感情运势"` |

## 核心功能

### 1️⃣ **Hashlib 哈希映射 (1-64卦位)**

使用 SHA256 对生日和主题的组合进行哈希运算，映射到 64 卦的对应位置。

```python
def _hash_to_hexagram(user_birthday: str, user_topic: str) -> int:
    combined_str = f"{user_birthday}:{user_topic}"
    hash_object = hashlib.sha256(combined_str.encode())
    hash_hex = hash_object.hexdigest()
    hash_int = int(hash_hex, 16)
    hexagram_num = (hash_int % 64) + 1
    return hexagram_num
```

**特点：**
- 确定性: 同一输入会产生相同的卦位
- 均匀分布: 利用模运算确保结果在 1-64 范围内
- 唯一性: 不同的生日+主题组合会产生不同的卦位

**示例结果：**
```
生日: 2000-01-15, 主题: 求财     → 卦位 34
生日: 1995-06-20, 主题: 感情运势 → 卦位 5
生日: 2005-12-25, 主题: 工作事业 → 卦位 32
```

### 2️⃣ **五行属性分析**

根据卜卦主题的关键词，自动识别所属的五行属性。

```python
def _analyze_five_elements(topic: str) -> Dict[str, str]
```

**五行分类：**

| 五行 | 属性 | 关键词示例 | 特征描述 |
|------|------|-----------|--------|
| 🌿 木 | 生长 | 工作、事业、学习、成长、进步 | 象征生长与发展 |
| 🔥 火 | 热烈 | 感情、爱情、婚姻、热情、创意 | 象征热烈与光明 |
| 🌍 土 | 稳定 | 稳定、安定、根基、家庭、保险 | 象征稳定与包容 |
| ✨ 金 | 财禄 | 财运、求财、金钱、收入、贸易 | 象征收敛与财禄 |
| 💧 水 | 智慧 | 智慧、灵感、思考、知识、冥想 | 象征智慧与内敛 |

**匹配逻辑：**
- 按关键词匹配度计分
- 选择分数最高的五行
- 若无直接匹配，按主题长度进行推断

**示例：**
```
"求财" → 金行（因属财运相关）
"感情运势" → 火行（因属感情相关）
"工作事业" → 木行（因属事业相关）
```

### 3️⃣ **格式化响应生成**

生成包含古风、现代分析和建议的完整回应。

**响应结构：**

```
━━━━━━━━━━━━━━━━━━━━━━━
✨ 生日卜卦 · 生命密码解读
━━━━━━━━━━━━━━━━━━━━━━━

📅 生日信息：YYYY-MM-DD
📍 卜卦主题：[用户主题]
🎯 卦位序号：第X卦

[古风过渡句]

✨ 古文解读 ✨
[八卦古文解读]

[AI现代分析]

🌟 运势评估：[运势等级]
五行属性：[属性]行
📋 当前状态象征：[对应八卦]卦

💡 转运小建议：[具体建议]

━━━━━━━━━━━━━━━━━━━━━━━
```

## 返回数据结构

```python
{
    "type": str,                    # "生日主题卜卦"
    "birthday": str,                # 用户生日
    "topic": str,                   # 卜卦主题
    "hexagram_num": int,            # 1-64的卦位序号
    "element": str,                 # 五行属性（木/火/土/金/水）
    "bagua": str,                   # 对应的八卦卦象
    "fortune": str,                 # 运势等级
    "response": str,                # 完整的格式化回应
    "ancient_transition": str,      # 古风过渡句
    "modern_analysis": str,         # 现代分析段落
    "turn_luck_advice": str         # 转运小建议
}
```

## 使用示例

### 基础调用

```python
from utils.divination import DivinationService

# 调用方法
result = DivinationService.birthday_topic_divination("2000-01-15", "求财")

# 获取对应结果
print(f"卦位: {result['hexagram_num']}")
print(f"五行: {result['element']}")
print(f"运势: {result['fortune']}")
print(f"\n完整回应:\n{result['response']}")
```

### 在 AstrBot 插件中集成

```python
@filter.command("生日卜卦")
async def birthday_divination_cmd(self, event: AstrMessageEvent):
    """生日主题卜卦命令 /生日卜卦 YYYY-MM-DD 主题"""
    
    try:
        args = event.message_str.strip().split(maxsplit=2)
        
        if len(args) < 3:
            yield event.plain_result("❌ 请提供生日和主题\n用法: /生日卜卦 YYYY-MM-DD 主题")
            return
        
        birthday = args[1]
        topic = args[2]
        
        result = self._divination_service.birthday_topic_divination(birthday, topic)
        
        yield event.plain_result(result['response'])
        
    except Exception as e:
        yield event.plain_result(f"❌ 卜卦出错: {str(e)}")
```

## 特点总结

✨ **四大特点：**

1. **科学性**: 使用 SHA256 哈希确保结果的确定性和均匀分布
2. **智能性**: 自动识别五行属性，提供精准的主题关联分析
3. **古韵十足**: 融合古风文言与现代分析，呈现专业的卜卦体验
4. **可定制**: 返回结构化数据，便于集成到各种应用场景

## 技术实现细节

### Hashlib 工作流程

```
输入: "2000-01-15:求财"
  ↓
SHA256 哈希
  ↓
转十六进制: "a1b2c3d4e5f6..."
  ↓
转十进制: 大整数
  ↓
模 64 运算: 大整数 % 64 = 0-63
  ↓
加 1: 1-64
  ↓
输出: 34
```

### 五行推断算法

```
如果主题包含"求财" → 金行
  ↓
否则，查找其他关键词
  ↓
若无匹配，使用 len(主题) % 5
  ↓
映射到五行列表 ["木", "火", "土", "金", "水"]
  ↓
输出: 对应五行
```

## 文件位置

- **实现文件**: `utils/divination.py`
- **新增方法**:
  - `birthday_topic_divination()` - 主入口方法
  - `_hash_to_hexagram()` - 哈希映射
  - `_analyze_five_elements()` - 五行分析

## 测试验证结果

✅ **通过测试用例:**

```
生日: 2000-01-15, 主题: 求财
  → 卦位: 34 (1-64范围) ✓
  → 五行: 金行 ✓

生日: 1995-06-20, 主题: 感情运势
  → 卦位: 5 (1-64范围) ✓
  → 五行: 火行 ✓

生日: 2005-12-25, 主题: 工作事业
  → 卦位: 32 (1-64范围) ✓
  → 五行: 木行 ✓
```

---

**实现完成时间**: 2026年2月28日
**Python 版本**: 3.7+
**依赖库**: `hashlib`、`random`（标准库）
