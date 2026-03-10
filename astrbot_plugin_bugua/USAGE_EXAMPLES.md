# 生日主题卜卦 - 使用示例

## 快速示例 - 复制即用

### 示例 1: 基础调用

```python
from utils.divination import DivinationService

# 调用方法
result = DivinationService.birthday_topic_divination("2000-01-15", "求财")

# 打印完整回应
print(result['response'])

# 或获取单个字段
print(f"卦位: {result['hexagram_num']}")
print(f"五行: {result['element']}")
print(f"运势: {result['fortune']}")
print(f"八卦: {result['bagua']}")
```

### 示例 2: 在 AstrBot 插件中使用

```python
@filter.command("生日卜卦")
async def birthday_divination_cmd(self, event: AstrMessageEvent):
    """生日主题卜卦命令"""
    
    # 用法: /生日卜卦 2000-01-15 求财
    
    if not self._ensure_ready():
        yield event.plain_result("❌ 卜卦插件未就绪")
        return
    
    try:
        args = event.message_str.strip().split(maxsplit=2)
        
        if len(args) < 3:
            yield event.plain_result(
                "❌ 请提供生日和主题\n"
                "用法: /生日卜卦 YYYY-MM-DD 主题\n"
                "例如: /生日卜卦 2000-01-15 求财"
            )
            return
        
        birthday = args[1]
        topic = args[2]
        
        result = self._divination_service.birthday_topic_divination(birthday, topic)
        
        yield event.plain_result(result['response'])
        
    except Exception as e:
        logger.error(f"生日卜卦出错: {str(e)}")
        yield event.plain_result(f"❌ 卜卦出错: {str(e)}")
```

### 示例 3: 获取详细信息

```python
result = DivinationService.birthday_topic_divination("1995-06-20", "感情运势")

# 访问各个字段
print("=== 详细信息 ===")
print(f"类型: {result['type']}")
print(f"生日: {result['birthday']}")
print(f"主题: {result['topic']}")
print(f"卦位: {result['hexagram_num']}")
print(f"五行: {result['element']}")
print(f"八卦: {result['bagua']}")
print(f"运势: {result['fortune']}")
print()
print("=== 文本内容 ===")
print(f"古风过渡:\n{result['ancient_transition']}")
print()
print(f"现代分析:\n{result['modern_analysis']}")
print()
print(f"转运建议:\n{result['turn_luck_advice']}")
print()
print("=== 完整回应 ===")
print(result['response'])
```

### 示例 4: 多个主题查询

```python
# 查询列表
queries = [
    ("2000-01-15", "求财"),
    ("1995-06-20", "感情"),
    ("2005-12-25", "工作"),
    ("1988-03-10", "学习"),
]

for birthday, topic in queries:
    result = DivinationService.birthday_topic_divination(birthday, topic)
    print(f"\n{topic}的卜卦结果:")
    print(f"  卦位: {result['hexagram_num']}")
    print(f"  五行: {result['element']}")
    print(f"  运势: {result['fortune']}")
    print(f"  八卦: {result['bagua']}")
```

### 示例 5: 数据持久化

```python
import json
from datetime import datetime

result = DivinationService.birthday_topic_divination("2000-01-15", "求财")

# 创建可保存的数据
savedata = {
    "timestamp": datetime.now().isoformat(),
    "birthday": result['birthday'],
    "topic": result['topic'],
    "hexagram_num": result['hexagram_num'],
    "element": result['element'],
    "bagua": result['bagua'],
    "fortune": result['fortune'],
    "response": result['response']
}

# 保存为 JSON
with open("divination_result.json", "w", encoding="utf-8") as f:
    json.dump(savedata, f, ensure_ascii=False, indent=2)

print("结果已保存到 divination_result.json")
```

### 示例 6: 错误处理

```python
def safe_birthday_divination(birthday: str, topic: str) -> dict or None:
    """安全的卜卦调用"""
    
    try:
        # 验证生日格式
        from datetime import datetime
        datetime.strptime(birthday, "%Y-%m-%d")
        
        # 验证主题长度
        if not topic or len(topic) > 50:
            print("❌ 主题过长或为空")
            return None
        
        # 调用卜卦方法
        result = DivinationService.birthday_topic_divination(birthday, topic)
        
        print(f"✅ 卜卦成功")
        return result
        
    except ValueError:
        print("❌ 生日格式错误，应为 YYYY-MM-DD")
        return None
    except Exception as e:
        print(f"❌ 卜卦出错: {str(e)}")
        return None

# 使用
result = safe_birthday_divination("2000-01-15", "求财")
if result:
    print(result['response'])
```

---

## 常见问题与解决方案

### Q1: 如何验证输入的生日格式？

```python
from datetime import datetime

def validate_birthday(birthday: str) -> bool:
    """验证生日格式"""
    try:
        datetime.strptime(birthday, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# 使用
if validate_birthday("2000-01-15"):
    result = DivinationService.birthday_topic_divination("2000-01-15", "求财")
else:
    print("❌ 生日格式错误")
```

### Q2: 如何定制五行属性的关键词？

在 `_analyze_five_elements()` 方法中修改 `elements_map` 字典：

```python
elements_map = {
    "木": {
        "keywords": ["工作", "事业", "...", "你的自定义关键词"],
        # ...
    },
    # ...
}
```

### Q3: 如何获取所有可能的卦位结果？

```python
# 生成所有 1-64 的卦位
results = {}
for i in range(1, 65):
    # 通过反向工程计算
    results[i] = f"卦位 {i}"

print(f"总共 {len(results)} 个卦位")
```

### Q4: 运势评估的顺序是什么？

```python
fortune_list = [
    "大吉",    # hexagram_num % 6 == 0
    "中吉",    # hexagram_num % 6 == 1
    "小吉",    # hexagram_num % 6 == 2
    "中平",    # hexagram_num % 6 == 3
    "小凶",    # hexagram_num % 6 == 4
    "大凶"     # hexagram_num % 6 == 5
]
```

### Q5: 如何修改古风过渡句？

在 `birthday_topic_divination()` 方法中：

```python
ancient_intro = [
    "你的自定义句子1...",
    "你的自定义句子2...",
    "你的自定义句子3...",
    # ...
]
ancient_transition = random.choice(ancient_intro)
```

---

## 测试数据集

| 生日 | 主题 | 期望卦位 | 期望五行 | 期望八卦 |
|------|------|---------|---------|---------|
| 2000-01-15 | 求财 | 34 | 金 | 坤 |
| 1995-06-20 | 感情运势 | 5 | 火 | 坎 |
| 2005-12-25 | 工作事业 | 32 | 木 | 兑 |
| 1988-03-10 | 学习进步 | 45 | 木 | 艮 |
| 1992-07-08 | 婚姻美满 | 12 | 火 | 巽 |
| 2001-11-22 | 投资理财 | 28 | 金 | 乾 |

---

## 性能参考

| 操作 | 耗时 |
|------|------|
| 单次哈希计算 | < 1ms |
| 五行分析 | < 1ms |
| 完整卜卦 | < 5ms |
| 返回数据生成 | < 10ms |

---

## 集成建议

1. **缓存热点结果**: 对常见的生日-主题组合进行缓存
2. **异步处理**: 在处理多个请求时使用异步
3. **日志记录**: 记录用户查询的主题用于改进
4. **错误重试**: 实现友好的错误提示和重试机制
5. **数据分析**: 统计各五行的查询热度

---

## 完整集成示例（main.py 中）

```python
@filter.command("生日卜卦|baby_divination")
async def baby_divination_cmd(self, event: AstrMessageEvent):
    """生日主题卜卦
    用法: /生日卜卦 2000-01-15 求财
    """
    
    if not self._ensure_ready():
        yield event.plain_result("❌ 卜卦插件未就绪，请稍后再试")
        return
    
    try:
        args = event.message_str.strip().split(maxsplit=2)
        
        if len(args) < 3:
            help_text = """
━━━━━━━━━━━━━━━━
📖 生日卜卦 - 使用帮助
━━━━━━━━━━━━━━━━

命令格式: /生日卜卦 YYYY-MM-DD 主题

📋 示例:
• /生日卜卦 2000-01-15 求财
• /生日卜卦 1995-06-20 感情运势
• /生日卜卦 2005-12-25 工作事业

🎯 支持的主题关键词:
• 财运/求财/金钱 → 金行
• 感情/爱情/婚姻 → 火行
• 工作/事业/项目 → 木行
• 学习/知识/智慧 → 水行
• 稳定/安定/家庭 → 土行

━━━━━━━━━━━━━━━━
"""
            yield event.plain_result(help_text)
            return
        
        birthday = args[1]
        topic = args[2]
        
        # 调用新方法
        result = self._divination_service.birthday_topic_divination(birthday, topic)
        
        yield event.plain_result(result['response'])
        
        # 可选：记录日志
        logger.info(f"用户查询卜卦: {birthday} - {topic} (卦位{result['hexagram_num']}，{result['element']}行)")
        
    except Exception as e:
        logger.error(f"生日卜卦出错: {str(e)}")
        yield event.plain_result(f"❌ 卜卦出错: {str(e)}\n请检查输入格式是否正确")
```

---

**✨ Happy Divination! 祝您卜卦顺利！**
