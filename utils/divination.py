"""卜卦核心服务 - 正宗梅花易数时间起卦法"""

import datetime
import random
import hashlib
import traceback
import logging
from typing import Dict, Tuple

# 获取logger
logger = logging.getLogger(__name__)

try:
    from borax.calendars.lunardate import LunarDate
    HAS_BORAX = True
except ImportError:
    HAS_BORAX = False

from ..data.divination_data import (
    BAGUA_DATA, XIANTIAN_BAGUA, TRIGRAM_LINES, LINES_TO_TRIGRAM,
    HEXAGRAM_64, WUXING_SHENG, WUXING_KE, FORTUNE_ADVICE,
    DIZHI_SEQUENCE, DIZHI_NUM,
)


class DivinationService:
    """正宗梅花易数时间起卦服务"""

    # 时辰序数映射  hour → (时辰名, 序数)
    # 子时跨午夜：23点 和 0点 均为子时=1
    _SHICHEN: Dict[int, Tuple[str, int]] = {
        0:  ("子", 1),  1:  ("丑", 2),  2:  ("丑", 2),
        3:  ("寅", 3),  4:  ("寅", 3),  5:  ("卯", 4),
        6:  ("卯", 4),  7:  ("辰", 5),  8:  ("辰", 5),
        9:  ("巳", 6),  10: ("巳", 6),  11: ("午", 7),
        12: ("午", 7),  13: ("未", 8),  14: ("未", 8),
        15: ("申", 9),  16: ("申", 9),  17: ("酉", 10),
        18: ("酉", 10), 19: ("戌", 11), 20: ("戌", 11),
        21: ("亥", 12), 22: ("亥", 12), 23: ("子", 1),
    }

    # ── 时间信息获取 ───────────────────────────────

    @staticmethod
    def _get_time_info() -> Dict:
        """获取当前公历 + 农历时间信息"""
        if not HAS_BORAX:
            raise RuntimeError(
                "缺少依赖库 borax，请在插件目录下执行：\n"
                "  pip install borax>=4.0.0\n"
                "安装完成后重启 AstrBot 即可。"
            )

        now   = datetime.datetime.now()
        today = now.date()
        lunar = LunarDate.from_solar_date(today.year, today.month, today.day)

        # 年地支：甲子年(year=4CE) 为基准，每12年一循环
        dizhi_index = ((lunar.year - 4) % 60) % 12
        dizhi       = DIZHI_SEQUENCE[dizhi_index]
        dizhi_num   = DIZHI_NUM[dizhi]

        shichen_name, shichen_num = DivinationService._SHICHEN[now.hour]

        return {
            "solar":          now,
            "lunar_year":     lunar.year,
            "lunar_month":    lunar.month,
            "lunar_day":      lunar.day,
            "is_leap_month":  bool(lunar.leap),
            "year_dizhi":     dizhi,
            "year_dizhi_num": dizhi_num,
            "shichen":        shichen_name,
            "shichen_num":    shichen_num,
        }

    # ── 起卦算法 ───────────────────────────────────

    @staticmethod
    def _mod8(n: int) -> int:
        """除8取余，余0则取8（坤）"""
        r = n % 8
        return r if r != 0 else 8

    @staticmethod
    def _mod6(n: int) -> int:
        """除6取余，余0则取6"""
        r = n % 6
        return r if r != 0 else 6

    # ── 三卦推导 ───────────────────────────────────

    @staticmethod
    def _all_lines(upper: str, lower: str) -> list:
        """返回六爻爻型列表，从下往上：[爻1, 爻2, 爻3, 爻4, 爻5, 爻6]"""
        return list(TRIGRAM_LINES[lower]) + list(TRIGRAM_LINES[upper])

    @staticmethod
    def _mutual_hexagram(upper: str, lower: str) -> Tuple[str, str]:
        """求互卦：爻2-3-4 → 互下卦；爻3-4-5 → 互上卦"""
        lines = DivinationService._all_lines(upper, lower)
        mu_lower = LINES_TO_TRIGRAM[tuple(lines[1:4])]
        mu_upper = LINES_TO_TRIGRAM[tuple(lines[2:5])]
        return mu_upper, mu_lower

    @staticmethod
    def _changed_hexagram(upper: str, lower: str, moving_line: int) -> Tuple[str, str]:
        """求变卦：将第 moving_line 爻（1-6）阴阳互换"""
        lines = DivinationService._all_lines(upper, lower)
        lines[moving_line - 1] ^= 1  # 0↔1
        ch_lower = LINES_TO_TRIGRAM[tuple(lines[0:3])]
        ch_upper = LINES_TO_TRIGRAM[tuple(lines[3:6])]
        return ch_upper, ch_lower

    # ── 体用生克分析 ───────────────────────────────

    @staticmethod
    def _tiyong_analysis(upper: str, lower: str, moving_line: int) -> Dict:
        """
        体用判断：
          动爻在下卦（1-3） → 用=下卦，体=上卦
          动爻在上卦（4-6） → 用=上卦，体=下卦
        """
        if moving_line <= 3:
            yong_gua, ti_gua = lower, upper
        else:
            yong_gua, ti_gua = upper, lower

        ti_elem   = BAGUA_DATA[ti_gua]["five_elements"]
        yong_elem = BAGUA_DATA[yong_gua]["five_elements"]

        if ti_elem == yong_elem:
            relation, verdict = "比和", "中平"
            desc = "体用比和，势均力衡，守成可利"
        elif WUXING_SHENG.get(yong_elem) == ti_elem:
            relation, verdict = "用生体", "大吉"
            desc = "用生体，外力扶助，事多顺遂"
        elif WUXING_SHENG.get(ti_elem) == yong_elem:
            relation, verdict = "体生用", "小凶"
            desc = "体生用，耗散自身心力，内耗为患"
        elif WUXING_KE.get(ti_elem) == yong_elem:
            relation, verdict = "体克用", "中吉"
            desc = "体克用，主动有力，可制外境"
        else:  # WUXING_KE[yong_elem] == ti_elem
            relation, verdict = "用克体", "大凶"
            desc = "用克体，受制于外，处境被动"

        return {
            "ti_gua":   ti_gua,   "ti_elem":   ti_elem,
            "yong_gua": yong_gua, "yong_elem": yong_elem,
            "relation": relation, "desc": desc, "verdict": verdict,
        }

    # ── 主起卦入口 ─────────────────────────────────

    @staticmethod
    def _topic_to_num(topic: str) -> int:
        """将主题文本拆解映射为 1-64 之间的确定性数值。

        对主题内容取 MD5 哈希后模 64，保证：
          · 同一主题始终得到相同的数值（可重复）
          · 不同主题（即使字数相同）几乎总能得到不同数值
          · 空主题返回 1
        """
        stripped = topic.strip()
        if not stripped:
            return 1
        topic_hash = int(hashlib.md5(stripped.encode("utf-8")).hexdigest(), 16)
        return (topic_hash % 64) + 1  # 范围 1-64

    @staticmethod
    def cast_hexagram(topic: str = "", user_id: str = "anonymous") -> Dict:
        """
        正宗梅花易数时间起卦。

        公式（先天八卦序：1乾2兑3离4震5巽6坎7艮8坤）：
          上卦 = (N + M + D + C + U)       % 8  （余0取8）
          下卦 = (N + M + D + T + U)       % 8  （余0取8）
          动爻 = (N + M + D + T + C + U)   % 6  （余0取6）

        N=年地支序数, M=农历月, D=农历日, T=时辰序数,
        C=主题哈希数(1-64), U=用户ID哈希值(1-12)

        C 由主题内容 MD5 哈希映射到 1-64，不同主题产生不同上卦与动爻，
        而下卦仅受时间与用户影响，三者各有侧重。
        """
        ti    = DivinationService._get_time_info()
        N, M, D, T = (ti["year_dizhi_num"], ti["lunar_month"],
                      ti["lunar_day"],      ti["shichen_num"])

        # 主题数：内容哈希映射到 1-64，不同主题产生不同卦象
        C = DivinationService._topic_to_num(topic)

        # 用户数：用户ID哈希映射到 1-12，确保不同用户得到不同结果
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        U = (user_hash % 12) + 1

        upper_sum  = N + M + D + C + U      # C 参与上卦，主题影响本卦卦象
        lower_sum  = N + M + D + T + U      # 纯时间+用户，下卦反映当下时机
        moving_sum = N + M + D + T + C + U  # C+T 共同决定动爻

        upper_num   = DivinationService._mod8(upper_sum)
        lower_num   = DivinationService._mod8(lower_sum)
        moving_line = DivinationService._mod6(moving_sum)

        upper_name = XIANTIAN_BAGUA[upper_num]
        lower_name = XIANTIAN_BAGUA[lower_num]

        # 本卦
        ben_data = HEXAGRAM_64.get(
            (upper_num, lower_num),
            {"name": f"{upper_name}{lower_name}", "title": "演化之卦",
             "fortune": "中平", "keyword": "演化之中", "description": "卦象演化，需仔细观察变化趋势。"},
        )

        # 互卦
        hu_upper, hu_lower = DivinationService._mutual_hexagram(upper_name, lower_name)
        hu_u_num, hu_l_num = BAGUA_DATA[hu_upper]["num"], BAGUA_DATA[hu_lower]["num"]
        hu_data = HEXAGRAM_64.get(
            (hu_u_num, hu_l_num),
            {"name": "互卦", "title": "互卦", "fortune": "中平", "keyword": "", "description": ""},
        )

        # 变卦
        ch_upper, ch_lower = DivinationService._changed_hexagram(upper_name, lower_name, moving_line)
        ch_u_num, ch_l_num = BAGUA_DATA[ch_upper]["num"], BAGUA_DATA[ch_lower]["num"]
        ch_data = HEXAGRAM_64.get(
            (ch_u_num, ch_l_num),
            {"name": "变卦", "title": "变卦", "fortune": "中平", "keyword": "", "description": ""},
        )

        # 体用生克
        tiyong = DivinationService._tiyong_analysis(upper_name, lower_name, moving_line)

        return {
            "topic":      topic or "综合运势",
            "time_info":  ti,
            "formula":    {"N": N, "M": M, "D": D, "T": T, "C": C, "U": U,
                           "upper_sum": upper_sum, "upper_num": upper_num,
                           "lower_sum": lower_sum, "lower_num": lower_num,
                           "moving_sum": moving_sum, "moving_line": moving_line},
            "upper_name": upper_name,
            "lower_name": lower_name,
            "ben_gua":    ben_data,
            "hu_gua":     {"upper": hu_upper, "lower": hu_lower, "data": hu_data},
            "bian_gua":   {"upper": ch_upper, "lower": ch_lower, "data": ch_data},
            "moving_line": moving_line,
            "tiyong":     tiyong,
        }

    # ── AI 断解 ────────────────────────────────────

    @staticmethod
    def _generate_llm_prompt(topic: str, ben_data: Dict, tiyong: Dict, bian_data: Dict, time_info: Dict) -> str:
        """生成用于LLM分析的提示词"""
        ben_name = ben_data.get('name', '未知')
        ben_desc = ben_data.get('description', '')
        ben_keyword = ben_data.get('keyword', '')
        ben_fortune = ben_data.get('fortune', '待定')
        
        bian_name = bian_data.get('name', '未知')
        bian_keyword = bian_data.get('keyword', '')
        
        ti_elem = tiyong.get('ti_elem', '未知')
        yong_elem = tiyong.get('yong_elem', '未知')
        relation = tiyong.get('relation', '未知')
        desc = tiyong.get('desc', '')
        
        system_prompt = "你是古代易学大师，精通梅花易数与卦象解读。请根据卦象信息提供专业、深邃的占卜解读。"
        
        user_message = f"""【用户问题】{topic or '综合运势'}

【卦象信息】
本卦：{ben_name}卦
· 卦辞：{ben_desc}
· 关键词：{ben_keyword}
· 运势：{ben_fortune}

变卦（发展方向）：{bian_name}卦
· 关键词：{bian_keyword}

【五行分析】
体卦五行属{ti_elem}
用卦五行属{yong_elem}
生克关系：{relation}（{desc}）

【要求】
1. 基于上述卦象与五行生克，分析用户问题的当前形势与未来发展
2. 阐述变卦所示的发展方向
3. 给出具体的建议或注意事项
4. 用词专业深刻，富有易学哲理
5. 限制在150字以内，直接给出解读内容（无需前缀说明）"""
        
        return system_prompt, user_message

    @staticmethod
    async def get_llm_advice_via_event(event, context, llm_system_prompt: str, llm_user_message: str) -> str:
        """通过 provider.text_chat() 调用 LLM

        Args:
            event: AstrMessageEvent 对象
            context: Star 的 context 对象，用于获取当前 provider
            llm_system_prompt: 系统提示词
            llm_user_message: 用户消息

        Returns:
            LLM 生成的建议文本，或 None 如果失败
        """
        try:
            logger.debug("[卜卦LLM] 获取 LLM provider...")
            provider = context.get_using_provider(umo=event.unified_msg_origin)

            logger.debug("[卜卦LLM] 通过 provider.text_chat() 调用...")
            response = await provider.text_chat(
                prompt=llm_user_message,
                system_prompt=llm_system_prompt,
            )

            advice = (response.completion_text or "").strip()
            if not advice:
                logger.warning("[卜卦LLM] provider.text_chat() 返回空文本")
                return None

            if len(advice) > 150:
                advice = advice[:147] + "..."

            logger.info(f"[卜卦LLM] 成功，长度: {len(advice)}字")
            return advice

        except Exception as e:
            logger.warning(f"[卜卦LLM] 调用失败: {type(e).__name__}: {e}")
            return None

    @staticmethod
    def _ai_advice(topic: str, ben_data: Dict, tiyong: Dict, bian_data: Dict, time_info: Dict = None) -> Tuple:
        """根据卦象与主题生成建议及 LLM prompts
        
        Returns:
            (模板方案文本, llm_system_prompt, llm_user_message)
            即使使用模板，也返回 LLM prompts 供后续调用
        """
        # 先构建 LLM prompts（供 event.request_llm() 使用）
        prompt_tuple = DivinationService._generate_llm_prompt(topic, ben_data, tiyong, bian_data, time_info or {})
        llm_system_prompt, llm_user_message = prompt_tuple
        
        # 模板方案：生成基础建议
        _TOPIC_KEYWORDS = {
            "学业": ["学", "考", "读", "书", "成绩", "课", "大学", "研究", "论文", "作业"],
            "财运": ["钱", "财", "收入", "工资", "投资", "赚", "股票", "生意", "创业"],
            "感情": ["爱", "情", "恋", "婚", "感情", "喜欢", "交往", "约会", "追", "表白"],
            "工作": ["工作", "职", "升职", "跳槽", "项目", "业绩", "领导", "同事", "面试"],
            "健康": ["健康", "身体", "病", "医", "康复", "锻炼", "睡眠", "饮食"],
        }
        _ADVICE_TABLE = {
            "学业": {
                "大吉": "学业运势极旺，此刻专注学习，考试或作业可望取得优异成绩。",
                "中吉": "学业进展顺利，保持专注认真，稳步提升。",
                "小吉": "学业稳定，注意查漏补缺，细节决定成败。",
                "中平": "学业平稳，需加强努力，避免松懈。",
                "小凶": "学业面临挑战，宜静心专注，减少外部干扰。",
                "大凶": "学业压力较大，调整心态，及时寻求帮助，切勿放弃。",
            },
            "财运": {
                "大吉": "财运旺盛，可积极把握投资或增收机会，量力而行。",
                "中吉": "财运渐入佳境，稳健理财可获收益。",
                "小吉": "财运小有斩获，量入为出，不宜冒进。",
                "中平": "财运持平，守成为宜，暂缓大额支出。",
                "小凶": "财运欠佳，谨慎消费，防止意外损失。",
                "大凶": "财运不利，切勿冒险投资，保守守财为上。",
            },
            "感情": {
                "大吉": "感情运势极佳，主动表达真心，感情可望升温。",
                "中吉": "感情顺遂，以真诚之心相待，关系将更进一步。",
                "小吉": "感情稳定，多沟通理解，细水长流。",
                "中平": "感情平淡，需主动营造，避免感情冷却。",
                "小凶": "感情有阻，冷静沟通化解误解。",
                "大凶": "感情动荡，宜冷静面对，避免冲动。",
            },
            "工作": {
                "大吉": "工作运势极旺，展现才能，升职加薪可期。",
                "中吉": "工作顺利，积极进取，团队协作可获认可。",
                "小吉": "工作平稳，踏实完成任务，积累经验。",
                "中平": "工作平平，注意效率，与同事保持良好沟通。",
                "小凶": "工作有阻，谨慎处理人际关系，避免冲突。",
                "大凶": "工作压力较大，保持冷静，从容应对挑战。",
            },
            "健康": {
                "大吉": "身体状态极佳，继续保持良好作息与运动习惯。",
                "中吉": "健康良好，规律作息，注重营养均衡。",
                "小吉": "健康平稳，注意防寒保暖，别忽视小毛病。",
                "中平": "健康一般，多休息，减少熬夜与过度劳累。",
                "小凶": "健康稍差，注意调理，必要时及时就医。",
                "大凶": "健康欠佳，务必重视身体信号，及时休养就诊。",
            },
            "综合": {
                "大吉": "整体运势大吉，把握机遇积极行动，诸事顺遂。",
                "中吉": "整体运势良好，循序渐进，稳中有进。",
                "小吉": "整体运势尚可，认真对待，可获小成。",
                "中平": "整体运势平平，稳字当先，不宜冒进。",
                "小凶": "整体运势稍弱，谨慎行事，待时而动。",
                "大凶": "整体运势不利，守静内省，等待时机逆转。",
            },
        }

        topic_type = "综合"
        for t, kws in _TOPIC_KEYWORDS.items():
            if any(kw in topic for kw in kws):
                topic_type = t
                break

        fortune      = ben_data.get("fortune", "中平")
        relation     = tiyong.get("relation", "比和")
        bian_keyword = bian_data.get("keyword", "")

        fortune_prefix = {"大吉": "卦象大吉，", "中吉": "卦象顺遂，",
                          "小吉": "卦象尚可，", "中平": "卦象持平，",
                          "小凶": "卦象示警，", "大凶": "卦象不利，"}.get(fortune, "")
        tiyong_comment = {"用生体": "外力扶助，", "体克用": "主动有力，",
                          "比和":   "势均力衡，", "体生用": "内耗为虑，",
                          "用克体": "受制为患，"}.get(relation, "")

        specific = _ADVICE_TABLE.get(topic_type, _ADVICE_TABLE["综合"]).get(
            fortune, "保持平常心，随遇而安。"
        )

        advice = f"{fortune_prefix}{tiyong_comment}{specific}"
        if bian_keyword:
            advice += f"变卦示意{bian_keyword}，未来走向值得关注。"

        final_advice = advice[:150] if len(advice) > 150 else advice
        # 返回元组: (模板文本, llm_system_prompt, llm_user_message)
        return final_advice, llm_system_prompt, llm_user_message

    # ── 输出格式化 ─────────────────────────────────

    @staticmethod
    def format_result(result: Dict) -> Tuple:
        """将起卦结果格式化为透明可读的文本
        
        Returns:
            (格式化文本字符串, llm_system_prompt, llm_user_message)
            三部分可分别使用，格式化文本用于直接展示，prompt用于 event.request_llm()
        """
        ti  = result["time_info"]
        f   = result["formula"]
        up  = result["upper_name"]
        lo  = result["lower_name"]
        ben = result["ben_gua"]
        hu  = result["hu_gua"]
        ch  = result["bian_gua"]
        ty  = result["tiyong"]
        mv  = result["moving_line"]

        solar_str = ti["solar"].strftime("%Y年%m月%d日  %H:%M")
        leap_str  = "（闰月）" if ti["is_leap_month"] else ""
        lunar_str = (f"{ti['lunar_year']}年（{ti['year_dizhi']}年）"
                     f"  农历{ti['lunar_month']}月{ti['lunar_day']}日{leap_str}")

        # 六爻爻型可视化（从上往下显示）
        lines = result["formula"]
        all_lines = (list(TRIGRAM_LINES[lo]) + list(TRIGRAM_LINES[up]))  # 爻1→爻6
        yao_rows = []
        pos_label = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
        for i in range(5, -1, -1):  # 从上往下
            is_yang   = bool(all_lines[i])
            is_moving = (i + 1 == mv)
            bar = "━━━━━━━" if is_yang else "━━━  ━━━"
            dot = " ●" if is_moving else ""
            yao_rows.append(f"    {bar}{dot}  {pos_label[i]}")

        # 卦象符号行
        up_sym = BAGUA_DATA[up]["symbol"]
        lo_sym = BAGUA_DATA[lo]["symbol"]
        hu_up_sym = BAGUA_DATA[hu["upper"]]["symbol"]
        hu_lo_sym = BAGUA_DATA[hu["lower"]]["symbol"]
        ch_up_sym = BAGUA_DATA[ch["upper"]]["symbol"]
        ch_lo_sym = BAGUA_DATA[ch["lower"]]["symbol"]

        # 五行符号
        elem_sym = {"金": "⊙", "木": "✦", "水": "≋", "火": "▲", "土": "◆"}
        ti_sym   = elem_sym.get(ty["ti_elem"],   "·")
        yo_sym   = elem_sym.get(ty["yong_elem"], "·")

        # 生成 LLM prompts（供后续调用）
        prompt_tuple = DivinationService._generate_llm_prompt(
            result["topic"], ben, ty, ch["data"], ti
        )
        llm_system_prompt, llm_user_message = prompt_tuple

        # 余数显示（mod8/mod6 显示原始余数）
        up_rem = f["upper_sum"] % 8
        lo_rem = f["lower_sum"] % 8
        mv_rem = f["moving_sum"] % 6

        rows = [
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"✦ 梅花易数时间起卦   主题：{result['topic']}",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "【起卦排盘】",
            f"  公历：{solar_str}",
            f"  农历：{lunar_str}",
            f"  时辰：{ti['shichen']}时  （T = {ti['shichen_num']}）",
            f"  年支：{ti['year_dizhi']}   （N = {ti['year_dizhi_num']}）",
            "",
            "【卦象演化】",
            f"  本卦（现状）：{up_sym}{lo_sym}  {ben['title']}  ·  {ben['name']}卦",
            f"  互卦（过程）：{hu_up_sym}{hu_lo_sym}  {hu['data']['title']}  ·  {hu['data']['name']}卦",
            f"  变卦（结局）：{ch_up_sym}{ch_lo_sym}  {ch['data']['title']}  ·  {ch['data']['name']}卦",
            "",
            f"  六爻爻型（● = 第{mv}爻动）：",
        ] + yao_rows + [
            "",
            f"  本卦关键词：{ben['keyword']}",
            f"  运势评级  ：{ben['fortune']}",
            f"  卦辞摘要  ：{ben['description']}",
            "",
            "【五行分析】",
            f"  体卦：{ty['ti_gua']}卦  {BAGUA_DATA[ty['ti_gua']]['symbol']}  五行属{ty['ti_elem']} {ti_sym}",
            f"  用卦：{ty['yong_gua']}卦  {BAGUA_DATA[ty['yong_gua']]['symbol']}  五行属{ty['yong_elem']} {yo_sym}",
            f"  生克：{ty['relation']}  ──  {ty['desc']}",
            f"  综合判断：{ty['verdict']}",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]

        formatted_text = "\n".join(rows)
        return formatted_text, llm_system_prompt, llm_user_message
