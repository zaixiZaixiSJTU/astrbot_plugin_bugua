"""测试birthday_topic_divination方法"""

from utils.divination import DivinationService

# 测试用例
test_cases = [
    ("2000-01-15", "求财"),
    ("1995-06-20", "感情运势"),
    ("2005-12-25", "工作事业"),
    ("1990-03-10", "学习成长"),
]

print("=" * 60)
print("生日主题卜卦测试")
print("=" * 60)

for birthday, topic in test_cases:
    print(f"\n测试: 生日={birthday}, 主题={topic}")
    print("-" * 60)
    
    result = DivinationService.birthday_topic_divination(birthday, topic)
    
    print(f"卦位序号: {result['hexagram_num']}")
    print(f"五行属性: {result['element']}")
    print(f"对应卦象: {result['bagua']}")
    print(f"运势等级: {result['fortune']}")
    print("\n完整回应：")
    print(result['response'])
    print("-" * 60)

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
