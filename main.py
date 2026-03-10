"""中式卜卦 - AstrBot卜卦插件（梅花易数时间起卦版）"""

import random
import hashlib
from datetime import datetime
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

from .utils.divination import DivinationService


@register("bugua", "AstrBot", "梅花易数时间起卦插件 - 正宗先天八卦推演", "2.0.0")
class BuguaPlugin(Star):
    """
    梅花易数时间起卦插件。
    使用当前服务器农历时间 + 主题字数，按先天八卦序推演：
      上卦 / 下卦 / 动爻 → 本卦 · 互卦 · 变卦 → 体用生克 → AI断解
    """

    def __init__(self, context: Context):
        super().__init__(context)
        self._svc = DivinationService()
        self._ready = False

    async def initialize(self):
        """初始化插件，检查依赖"""
        try:
            from borax.calendars.lunardate import LunarDate  # noqa: F401
            self._ready = True
            logger.info("卜卦插件初始化完成 ✦")
        except ImportError:
            logger.error(
                "卜卦插件初始化失败：缺少 borax 库。\n"
                "请执行：pip install borax>=4.0.0  后重启 AstrBot。"
            )
            self._ready = False

    @staticmethod
    def _get_stable_user_id(event: AstrMessageEvent) -> str:
        """从事件中稳定地获取用户ID"""
        # 按优先级尝试多个可能的用户ID属性名
        # 避免使用group_id/source等共享属性
        
        potential_ids = [
            'uid',          # 常见用户ID
            'user_id',      # 常见用户ID
            'sender_id',    # 发送者ID
            'qq',           # QQ号
            'qid',          # QQ相关ID
            'openid',       # 开放平台ID
            'member_openid',# 成员openid
            'peer',         # 用户对等ID
            'peer_id',      # 用户对等ID
            'user',         # 用户对象的ID属性
        ]
        
        for attr_name in potential_ids:
            value = getattr(event, attr_name, None)
            if value is not None:
                id_str = str(value)
                # 过滤掉明显不是用户ID的值（如0或"0"）
                if id_str and id_str != '0':
                    logger.debug(f"用户ID来源: {attr_name} = {id_str}")
                    return id_str
        
        # 最后尝试获取事件的__dict__来看有哪些属性
        # 并查找看起来像用户ID的属性
        if hasattr(event, '__dict__'):
            event_dict = event.__dict__
            for key, value in event_dict.items():
                # 查找看起来像用户ID的属性（名称中包含id或user）
                if ('id' in key.lower() or 'user' in key.lower()) and value:
                    id_str = str(value)
                    # 过滤掉group/group_id等群组相关属性
                    if 'group' not in key.lower() and 'source' not in key.lower() and id_str != '0':
                        logger.debug(f"用户ID来源（动态查找）: {key} = {id_str}")
                        return id_str
        
        # 最后的默认值
        logger.warning(f"无法获取用户ID，使用默认值。事件类型: {type(event)}")
        return "anonymous"

    # ── 主卜卦命令 ────────────────────────────────

    @filter.regex(r"^(卜卦|bugua|八卦|六爻)(\s+(.*))?$")
    async def zhanbu_cmd(self, event: AstrMessageEvent):
        """主卜卦命令：卜卦 [主题] 或 /卜卦 [主题]

        例：卜卦 期末考试
            卜卦 感情
            卜卦        （不填主题则测综合运势）
            /卜卦 期末考试
        """
        if not self._ready:
            yield event.plain_result(
                "❌ 插件未就绪，缺少依赖库 borax。\n"
                "请执行：pip install borax>=4.0.0  后重启 AstrBot。"
            )
            return

        msg = event.message_str.strip()
        # 移除命令关键词，提取主题
        for cmd in ["卜卦", "bugua", "八卦", "六爻"]:
            if msg.startswith(cmd):
                topic = msg[len(cmd):].strip()
                break
        else:
            topic = ""

        try:
            # 获取用户ID并进行起卦
            user_id = self._get_stable_user_id(event)
            result = DivinationService.cast_hexagram(topic, user_id)
            
            # 得到格式化文本和 LLM prompts
            formatted_text, llm_system_prompt, llm_user_message = DivinationService.format_result(result)
            
            # 调用 LLM 获取专业解读
            logger.debug("[卜卦] 正在调用 LLM 生成专业解读...")
            
            # 使用 event.request_llm() 调用 LLM（推荐方案，不需要 chat_provider_id）
            llm_advice = await DivinationService.get_llm_advice_via_event(
                event, self.context, llm_system_prompt, llm_user_message
            )
            
            # 如果 LLM 调用成功，将解读追加到格式化文本中
            if llm_advice:
                full_response = f"{formatted_text}\n\n【AI 专业解读】\n{llm_advice}"
            else:
                # LLM 失败则直接使用格式化文本
                logger.warning("[卜卦] LLM 调用失败，使用卦象信息")
                full_response = formatted_text
            
            yield event.plain_result(full_response)
        except RuntimeError as e:
            yield event.plain_result(f"❌ {e}")
        except Exception as e:
            logger.error(f"卜卦出错: {e}")
            yield event.plain_result(f"❌ 卜卦出错，请稍后重试：{e}")

    # ── 帮助命令 ──────────────────────────────────

    @filter.command("卜卦帮助|bugua_help")
    async def help_cmd(self, event: AstrMessageEvent):
        """显示使用帮助"""
        help_text = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✦ 梅花易数时间起卦  ·  使用帮助
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▶ 主命令
  /卜卦 [主题]
  /八卦 [主题]   （同上，别名）
  /六爻 [主题]   （同上，别名）

  示例：
    /卜卦 期末考试
    /卜卦 近期财运
    /卜卦 感情
    /卜卦            ← 不填则测综合运势

▶ 起卦原理（梅花易数 · 时间起卦）

  先天八卦序：1乾 2兑 3离 4震 5巽 6坎 7艮 8坤

  变量说明：
    N = 农历年  地支序数（子=1 … 亥=12）
    M = 农历月
    D = 农历日
    T = 当前时辰序数（子=1 … 亥=12）
    C = 主题字数

  公式：
    上卦 = (N+M+D)     ÷ 8  取余（余0→8坤）
    下卦 = (N+M+D+T)   ÷ 8  取余（余0→8坤）
    动爻 = (N+M+D+T+C) ÷ 6  取余（余0→6）

▶ 输出说明

  【起卦排盘】  算式全程透明展示
  【卦象演化】  本卦（现状）→ 互卦（过程）→ 变卦（结局）
  【五行分析】  体卦 vs 用卦 → 生克关系
  【AI 断解】   结合主题给出 ≤150 字专业建议

▶ 其他

  今天吃什么 / 今天穿什么 / 今天做什么  ← 趣味随机建议

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        yield event.plain_result(help_text.strip())

    # ── 趣味随机建议（关键词触发）─────────────────

    @filter.regex(r"今天吃什么|今天穿什么|今天做什么")
    async def random_suggestion_cmd(self, event: AstrMessageEvent):
        """关键词触发：今天吃/穿/做什么（根据用户ID和日期生成固定结果）"""
        msg = event.message_str.strip()
        
        # 获取用户ID和当前日期
        user_id = self._get_stable_user_id(event)
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 根据用户ID和日期生成固定种子
        seed_input = f"{user_id}-{today}"
        seed = int(hashlib.md5(seed_input.encode()).hexdigest(), 16)
        
        # 使用Random实例而不是全局random，避免影响其他部分
        rng = random.Random(seed)

        if "吃什么" in msg:
            foods = ["红烧肉", "番茄鸡蛋", "宫保鸡丁", "麻婆豆腐", "清蒸鱼", "炒青菜", "馄饨汤"]
            suggestion = f"🍽️ 卦象显示：今天适合吃 {rng.choice(foods)}！"
        elif "穿什么" in msg:
            colors = ["红色", "蓝色", "绿色", "黄色", "黑色", "白色", "紫色"]
            suggestion = f"👕 卦象显示：今天穿 {rng.choice(colors)} 运气最好！"
        else:
            activities = ["锻炼身体", "学习新技能", "陪伴家人", "整理房间", "规划未来"]
            suggestion = f"✦ 卦象显示：今天适合 {rng.choice(activities)}！"

        yield event.plain_result(suggestion)
