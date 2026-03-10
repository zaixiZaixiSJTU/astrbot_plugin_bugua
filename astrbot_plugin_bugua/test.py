"""卜卦插件单元测试"""

import unittest
from utils.divination import DivinationService


class TestDivinationService(unittest.TestCase):
    """测试卜卦服务"""

    def setUp(self):
        """测试初始化"""
        self.service = DivinationService()

    def test_bagua_divination(self):
        """测试八卦卜卦"""
        result = self.service.bagua_divination("工作")
        self.assertIn("type", result)
        self.assertEqual(result["type"], "八卦卜卦")
        self.assertIn("main_bagua", result)
        self.assertIn("fortune", result)
        print("✓ 八卦卜卦测试通过")

    def test_coin_divination(self):
        """测试硬币卜卦"""
        result = self.service.coin_divination("爱情")
        self.assertIn("type", result)
        self.assertEqual(result["type"], "硬币卜卦")
        self.assertIn("coin_results", result)
        self.assertEqual(len(result["coin_results"]), 3)
        print("✓ 硬币卜卦测试通过")

    def test_liuyao_divination(self):
        """测试六爻卜卦"""
        result = self.service.liuyao_divination("财运")
        self.assertIn("type", result)
        self.assertEqual(result["type"], "六爻卜卦")
        self.assertIn("yaos", result)
        self.assertEqual(len(result["yaos"]), 6)
        print("✓ 六爻卜卦测试通过")

    def test_birth_prediction(self):
        """测试生日运势预测"""
        result = self.service.birth_prediction(2000, 1, 15)
        self.assertIn("type", result)
        self.assertEqual(result["type"], "生日运势预测")
        self.assertIn("bagua", result)
        self.assertIn("fortune", result)
        print("✓ 生日运势预测测试通过")

    def test_weekly_forecast(self):
        """测试周运势预报"""
        result = self.service.weekly_forecast()
        self.assertIn("type", result)
        self.assertEqual(result["type"], "周运势预报")
        self.assertIn("forecast", result)
        self.assertEqual(len(result["forecast"]), 7)
        print("✓ 周运势预报测试通过")

    def test_tarot_single(self):
        """测试单张塔罗卜卦"""
        result = self.service.tarot_like_divination("single")
        self.assertIn("type", result)
        self.assertEqual(result["type"], "塔罗式卜卦")
        self.assertIn("card", result)
        print("✓ 单张塔罗卜卦测试通过")

    def test_tarot_past_present_future(self):
        """测试过去-现在-未来塔罗卜卦"""
        result = self.service.tarot_like_divination("past_present_future")
        self.assertIn("type", result)
        self.assertEqual(result["type"], "塔罗式卜卦")
        self.assertIn("cards", result)
        print("✓ 过去-现在-未来卜卦测试通过")

    def test_format_result(self):
        """测试结果格式化"""
        result = self.service.bagua_divination("测试")
        formatted = self.service.format_result(result, "详细")
        self.assertIsInstance(formatted, str)
        self.assertIn("✨", formatted)
        print("✓ 结果格式化测试通过")


if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━")
    print("运行卜卦插件测试...")
    print("━━━━━━━━━━━━━━━━━━━━━\n")
    
    unittest.main(verbosity=2)
