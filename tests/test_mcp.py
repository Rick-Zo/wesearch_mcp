#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '.')

from modules.weixin_search import WeixinSearch
from modules.article_processor import ArticleProcessor


async def test_search():
    print("=" * 60)
    print("测试 1: 搜索微信文章")
    print("=" * 60)
    
    try:
        query = "人工智能"
        print(f"\n搜索关键词: {query}")
        results = await WeixinSearch.search(query, num=2)
        
        if results:
            print(f"\n✅ 成功找到 {len(results)} 篇文章:\n")
            for i, article in enumerate(results, 1):
                print(f"{i}. {article['title']}")
                print(f"   公众号: {article['gzh_name']}")
                print(f"   链接: {article['url'][:60]}...")
                print(f"   摘要: {article['abstract'][:50]}..." if article['abstract'] else "   摘要: (无)")
                print()
        else:
            print("\n❌ 未找到文章")
        
        return results
        
    except Exception as e:
        print(f"\n❌ 搜索失败: {e}")
        return []


async def test_fetch_articles(search_results):
    print("=" * 60)
    print("测试 2: 抓取文章内容")
    print("=" * 60)
    
    if not search_results:
        print("\n⚠️  跳过测试 (无搜索结果)")
        return
    
    try:
        print("\n开始抓取文章内容...")
        articles = await ArticleProcessor.fetch_all(search_results)
        
        if articles:
            print(f"\n✅ 成功抓取 {len(articles)} 篇文章:\n")
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article['title']}")
                content_preview = article['content'][:100].replace('\n', ' ')
                print(f"   内容预览: {content_preview}...")
                print(f"   内容长度: {len(article['content'])} 字符")
                print()
        else:
            print("\n❌ 未能抓取到文章内容")
            
    except Exception as e:
        print(f"\n❌ 抓取失败: {e}")


async def test_full_workflow():
    print("\n" + "=" * 60)
    print("测试 3: 完整工作流程")
    print("=" * 60)
    
    try:
        query = "claude mcp"
        count = 1
        
        print(f"\n搜索关键词: {query}")
        print(f"文章数量: {count}")
        
        search_results = await WeixinSearch.search(query, num=count)
        
        if not search_results:
            print("\n❌ 未找到相关文章")
            return
        
        articles = await ArticleProcessor.fetch_all(search_results)
        
        if articles:
            print(f"\n✅ 完整流程测试成功!")
            print(f"\n最终输出格式预览:\n")
            print(f"# 微信文章搜索结果\n")
            print(f"**搜索关键词**: {query}")
            print(f"**找到文章数**: {len(articles)}\n")
            print("---\n")
            
            for i, article in enumerate(articles, 1):
                print(f"## 文章 {i}: {article['title']}\n")
                print(f"**公众号**: {article['gzh_name']}")
                print(f"**链接**: {article['url']}\n")
                print(f"### 正文内容\n")
                print(f"{article['content'][:200]}...\n")
                print("---\n")
        else:
            print("\n❌ 完整流程测试失败: 无法获取文章内容")
            
    except Exception as e:
        print(f"\n❌ 完整流程测试失败: {e}")


async def main():
    print("\n🚀 开始测试微信文章搜索 MCP")
    print()
    
    search_results = await test_search()
    
    await test_fetch_articles(search_results)
    
    await test_full_workflow()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)
    print()


if __name__ == "__main__":
    asyncio.run(main())
