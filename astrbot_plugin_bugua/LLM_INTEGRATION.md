# LLM 集成修复说明

## 问题诊断

原代码中 LLM 调用失败的原因：
- ❌ 调用了不存在的方法：`context.llm_response()` 和 `context.call_llm()`
- ❌ Prompt 结构不适配 AstrBot 框架

## 解决方案

### 1. 正确的 LLM 调用方法

根据 AstrBot 框架提供的 API，使用以下正确的调用方式：

```python
# 推荐：普通生成（适合本插件）
llm_resp = await context.llm_generate(
    messages=[...],           # 消息列表
    system_prompt="你是...", # 系统提示词
    temperature=0.7,
    max_tokens=200,
    tools=None                # 不需要函数调用时设为 None
)

# 备选：Agent 方式（需要函数调用）
llm_resp = await context.tool_loop_agent(
    event=event,
    chat_provider_id=provider_id,
    max_tokens=200
)
```

### 2. 实装修复

在 [divination.py](utils/divination.py) 中修改了以下内容：

#### 改进的 Prompt 结构

```python
def _generate_llm_prompt(topic, ben_data, tiyong, bian_data, time_info):
    # 返回元组: (system_prompt, user_message)
    system_prompt = "你是古代易学大师，精通梅花易数与卦象解读。..."
    user_message = """【用户问题】...
【卦象信息】...
【五行分析】...
【要求】..."""
    return system_prompt, user_message
```

#### 更新的 LLM 调用方法

```python
async def _get_llm_advice(context, prompt_tuple):
    system_prompt, user_message = prompt_tuple
    
    llm_resp = await context.llm_generate(
        messages=[{"role": "user", "content": user_message}],
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=200,
        tools=None
    )
    
    # 返回的是直接的文本响应
    return str(llm_resp).strip()
```

### 3. Prompt 设计

#### System Prompt
```
你是古代易学大师，精通梅花易数与卦象解读。请根据卦象信息提供专业、深邃的占卜解读。
```

**作用**：
- 建立角色定位，提升易学专业性
- 引导 LLM 避免通俗化解读

#### User Message 结构
```
【用户问题】{具体问题}

【卦象信息】
本卦：{卦名}卦
· 卦辞：{历史含义}
· 关键词：{核心语义}
· 运势：{吉凶评级}

变卦（发展方向）：{变化后的卦}
· 关键词：{发展趋势}

【五行分析】
体卦五行属{属性}
用卦五行属{属性}
生克关系：{相生/相克}（{具体影响}）

【要求】
1. 基于卦象与五行生克分析形势
2. 指出变卦所示的发展方向
3. 给出具体建议
4. 用词专业深刻
5. 限制150字以内，直接给出内容
```

**优势**：
- ✅ 结构化信息清晰，易于 LLM 解析
- ✅ 包含上下文和约束条件
- ✅ 明确要求格式和字数限制
- ✅ 易学术语规范，避免 LLM 胡编乱造

### 4. 调用耦合处理

在 `_ai_advice()` 中处理事件循环状态：

```python
if context is not None:
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 事件循环已运行时返回 None，使用降级方案
            llm_result = None
        else:
            # 创建新任务等待完成
            llm_result = loop.run_until_complete(
                DivinationService._get_llm_advice(context, prompt_tuple)
            )
    except Exception as e:
        llm_result = None
    
    if llm_result:
        return llm_result

# 降级：使用预设模板（当 LLM 不可用时）
```

## 调试步骤

1. **检查 context 可用性**
   ```python
   logger.debug(f"Context methods: {dir(context)}")
   ```

2. **验证 LLM 连接**
   - 确保在 `initialize()` 方法中正确初始化
   - 检查 AstrBot 的 LLM 配置是否正确

3. **查看日志输出**
   ```
   [卜卦LLM调用] 调用 context.llm_generate()
   [卜卦LLM调用] 成功！返回内容长度: XXX字
   ```

## 使用示例

用户输入：
```
/卜卦 期末考试
```

程序流程：
1. 起卦计算 → 获得「乾中有坎」
2. 生成 prompt（structure'd 格式）
3. 调用 LLM：
   ```
   System: 你是古代易学大师...
   User: 【用户问题】期末考试
        【卦象信息】本卦：豫卦...
        【五行分析】体卦五行属土...
   ```
4. LLM 返回：
   ```
   豫卦现世，象征时宜已至。本卦与坤卦相配，土土相亲...
   ```
5. 格式化输出给用户

## 降级方案

当 LLM 不可用时（无网络、模型故障等），自动使用本地模板：

```python
_ADVICE_TABLE = {
    "学业": {"大吉": "学业运势极旺...", ...},
    "财运": {"大吉": "财运旺盛...", ...},
    ...
}
```

- 仅损失 AI 的创意性，保留占卜功能
- 无需额外依赖，性能更优

## 参考资源

- AstrBot 官方 API 文档
- OpenAI 兼容的 LLM 参数说明
- 梅花易数理论背景

## 后续优化

1. **缓存管理**：缓存相同问题的 LLM 响应
2. **Token 优化**：精简 prompt 以降低成本
3. **并发处理**：支持多用户并发卜卦
4. **响应超时**：设置 LLM 调用超时时间
