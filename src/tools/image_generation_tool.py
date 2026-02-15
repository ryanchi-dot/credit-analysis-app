"""
图像生成工具 - 用于生成报表图表
"""
import os
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import ImageGenerationClient
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def generate_chart_image(
    prompt: str,
    chart_type: str = "bar",
    size: str = "2K",
    runtime: ToolRuntime = None
) -> str:
    """
    生成图表图像
    
    适用于生成柱状图、折线图、趋势图等简单图表，用于报告中数据可视化展示。
    
    Args:
        prompt (str): 图表的详细描述，应包含：
            - 图表类型（柱状图、折线图、趋势图等）
            - 数据内容（具体数值、年份、指标等）
            - 样式要求（颜色、字体、布局等）
            例如："生成一张柱状图，展示腾讯2022-2024年的营收对比，数据分别为：2022年5546亿元，2023年6090亿元，2024年6603亿元。使用蓝色柱状图，清晰标注年份和金额，风格专业商务"
        chart_type (str, optional): 图表类型，可选值：bar（柱状图）、line（折线图）、trend（趋势图）、pie（饼图）、architecture（架构图）
        size (str, optional): 图像尺寸，可选值：2K、4K，或自定义尺寸如 "3840x2160"，默认为 "2K"
        runtime (ToolRuntime, optional): LangChain 工具运行时上下文
    
    Returns:
        str: 生成的图像URL列表（JSON字符串），或错误信息
    
    示例:
        >>> generate_chart_image("生成一张柱状图，展示阿里巴巴2022-2024年营收对比：2022年8500亿元，2023年9200亿元，2024年9800亿元", chart_type="bar")
    """
    try:
        ctx = runtime.context if runtime else new_context(method="generate_chart_image")
        
        # 创建客户端
        client = ImageGenerationClient(ctx=ctx)
        
        # 构建完整的提示词
        full_prompt = f"生成一张专业的{chart_type}图表。{prompt}。要求：风格专业商务，清晰易读，适合银行信贷报告使用。"
        
        # 调用图像生成API
        response = client.generate(
            prompt=full_prompt,
            size=size,
            watermark=False,  # 报告图表不需要水印
            response_format="url"
        )
        
        if response.success:
            image_urls = response.image_urls
            # 返回URL列表的JSON字符串
            import json
            return json.dumps({
                "success": True,
                "image_urls": image_urls,
                "count": len(image_urls),
                "size": size
            }, ensure_ascii=False, indent=2)
        else:
            import json
            return json.dumps({
                "success": False,
                "error": "图表生成失败",
                "details": response.error_messages
            }, ensure_ascii=False, indent=2)
    
    except Exception as e:
        import json
        return json.dumps({
            "success": False,
            "error": "图表生成异常",
            "details": str(e)
        }, ensure_ascii=False, indent=2)
