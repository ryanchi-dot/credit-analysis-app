"""
网络搜索工具 - 获取目标公司的公开信息
"""
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def search_company_info(company_name: str, search_focus: str = "综合信息", runtime: ToolRuntime = None) -> str:
    """
    搜索目标公司的公开信息
    
    Args:
        company_name: 公司名称（如"腾讯控股"、"阿里巴巴集团"）
        search_focus: 搜索重点（如"财务数据"、"业务信息"、"新闻报道"、"公司简介"、"股价表现"）
        runtime: 工具运行时上下文
    
    Returns:
        搜索结果摘要，包括公司相关信息、数据来源和关键发现
    """
    ctx = runtime.context if runtime else new_context(method="search_company_info")
    
    client = SearchClient(ctx=ctx)
    
    # 根据搜索重点构建查询语句
    query_keywords = {
        "综合信息": f"{company_name} 公司简介 业务介绍",
        "财务数据": f"{company_name} 财务报表 营收 利润 年报",
        "业务信息": f"{company_name} 主营业务 产品 服务",
        "新闻报道": f"{company_name} 最新新闻 动态 发展",
        "公司简介": f"{company_name} 成立时间 创始人 发展历程",
        "股价表现": f"{company_name} 股价 市值 投资价值",
        "风险因素": f"{company_name} 风险 负债 债务 经营风险",
        "行业地位": f"{company_name} 行业排名 市场份额 竞争对手"
    }
    
    query = query_keywords.get(search_focus, f"{company_name} {search_focus}")
    
    try:
        # 执行搜索，获取更多结果以获得更全面的信息
        response = client.web_search(
            query=query,
            count=15,
            need_summary=True
        )
        
        if not response.web_items:
            return f"未找到关于【{company_name}】({search_focus})的相关信息，请检查公司名称是否正确。"
        
        # 构建结果摘要
        result_parts = []
        result_parts.append(f"=== {company_name} - {search_focus} 搜索结果 ===\n")
        
        # 如果有 AI 摘要，优先展示
        if response.summary:
            result_parts.append(f"【AI 智能摘要】\n{response.summary}\n")
        
        # 展示搜索结果详情
        result_parts.append(f"【详细搜索结果（共 {len(response.web_items)} 条）】\n")
        
        for idx, item in enumerate(response.web_items[:10], 1):  # 展示前10条最相关结果
            result_parts.append(f"\n{idx}. {item.title}")
            result_parts.append(f"   来源: {item.site_name}")
            
            if item.snippet:
                result_parts.append(f"   摘要: {item.snippet[:200]}")
            
            if item.publish_time:
                result_parts.append(f"   发布时间: {item.publish_time}")
            
            result_parts.append(f"   链接: {item.url}")
        
        return "\n".join(result_parts)
    
    except Exception as e:
        return f"搜索【{company_name}】({search_focus})时发生错误: {str(e)}"


@tool
def search_comprehensive_company_data(company_name: str, runtime: ToolRuntime = None) -> str:
    """
    全面搜索目标公司的关键信息（财务、业务、新闻、风险等）
    
    Args:
        company_name: 公司名称
        runtime: 工具运行时上下文
    
    Returns:
        包含多个维度的公司综合信息
    """
    ctx = runtime.context if runtime else new_context(method="search_comprehensive")
    
    client = SearchClient(ctx=ctx)
    
    # 搜索多个维度的信息
    search_queries = [
        f"{company_name} 公司简介 主营业务",
        f"{company_name} 财务数据 营收 利润 资产负债",
        f"{company_name} 最新新闻 重大事件",
        f"{company_name} 行业地位 市场份额"
    ]
    
    comprehensive_results = []
    
    for query in search_queries:
        try:
            response = client.web_search(query=query, count=8, need_summary=True)
            
            if response.web_items:
                # 提取查询关键词
                query_type = query.replace(company_name, "").strip()
                comprehensive_results.append(f"\n{'='*60}")
                comprehensive_results.append(f"【{query_type}】")
                comprehensive_results.append(f"{'='*60}")
                
                # AI 摘要
                if response.summary:
                    comprehensive_results.append(f"\n摘要: {response.summary}\n")
                
                # 前3条最相关的结果
                for idx, item in enumerate(response.web_items[:3], 1):
                    comprehensive_results.append(f"{idx}. {item.title}")
                    if item.snippet:
                        comprehensive_results.append(f"   {item.snippet[:150]}")
                    comprehensive_results.append(f"   {item.url}")
        
        except Exception as e:
            comprehensive_results.append(f"\n【错误】查询 '{query}' 失败: {str(e)}")
    
    if not comprehensive_results:
        return f"未找到【{company_name}】的任何相关信息，请检查公司名称是否正确。"
    
    return "\n".join(comprehensive_results)
