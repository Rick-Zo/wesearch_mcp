import httpx
from lxml import html
import re
from urllib.parse import quote
import asyncio
from typing import List, Dict, Optional
import config


class WeixinSearch:
    
    @staticmethod
    async def search(query: str, num: int = 3) -> List[Dict[str, str]]:
        encoded_query = quote(query)
        search_url = f"https://weixin.sogou.com/weixin?type=2&query={encoded_query}"
        
        headers = {
            "User-Agent": config.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": f"https://weixin.sogou.com/weixin?query={quote(query)}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT, follow_redirects=True) as client:
                response = await client.get(search_url, headers=headers)
                response.raise_for_status()
                
                tree = html.fromstring(response.text)
                
                article_nodes = tree.xpath('//ul[@class="news-list"]/li')
                if not article_nodes:
                    article_nodes = tree.xpath('//ul[@class="news-list2"]/li')
                
                results = []
                for article_node in article_nodes[:num]:
                    try:
                        title_elem = article_node.xpath('.//h3/a')
                        if not title_elem:
                            continue
                        
                        title = title_elem[0].text_content().strip()
                        sogou_url = title_elem[0].get('href')
                        
                        if not sogou_url:
                            continue
                        
                        if not sogou_url.startswith('http'):
                            sogou_url = 'https://weixin.sogou.com' + sogou_url
                        
                        gzh_elem = article_node.xpath('.//span[@class="all-time-y2"]')
                        if not gzh_elem:
                            gzh_elem = article_node.xpath('.//a[contains(@class, "account") or @uigs="account_name_0"]')
                        gzh_name = gzh_elem[0].text_content().strip() if gzh_elem else "未知公众号"
                        
                        abstract_elem = article_node.xpath('.//p[@class="txt-info"]')
                        abstract = abstract_elem[0].text_content().strip() if abstract_elem else ""
                        
                        real_url = await WeixinSearch._get_real_url(sogou_url, headers, client)
                        
                        final_url = real_url if real_url else sogou_url
                        
                        results.append({
                            'title': title,
                            'url': final_url,
                            'sogou_url': sogou_url,
                            'gzh_name': gzh_name,
                            'abstract': abstract
                        })
                        
                        if len(results) >= num:
                            break
                            
                    except Exception as e:
                        print(f"解析文章节点失败: {e}")
                        continue
                
                return results
                
        except httpx.TimeoutException:
            raise Exception(f"搜索请求超时,请稍后重试")
        except httpx.HTTPStatusError as e:
            raise Exception(f"搜索请求失败: HTTP {e.response.status_code}")
        except Exception as e:
            raise Exception(f"搜索过程中出错: {str(e)}")
    
    @staticmethod
    async def _get_real_url(sogou_url: str, headers: dict, client: httpx.AsyncClient) -> Optional[str]:
        try:
            if 'mp.weixin.qq.com' in sogou_url:
                return sogou_url
            
            response = await client.get(sogou_url, headers=headers, follow_redirects=True)
            
            if response.status_code in [301, 302]:
                location = response.headers.get('Location')
                if location and 'mp.weixin.qq.com' in location:
                    return location
            
            content = response.text
            
            start_index = content.find("url += '")
            if start_index != -1:
                url_parts = []
                search_start = start_index
                
                while True:
                    part_start = content.find("url += '", search_start)
                    if part_start == -1:
                        break
                    part_end = content.find("'", part_start + len("url += '"))
                    if part_end == -1:
                        break
                    part = content[part_start + len("url += '"):part_end]
                    url_parts.append(part)
                    search_start = part_end + 1
                
                if url_parts:
                    full_url = ''.join(url_parts).replace("@", "")
                    if full_url:
                        if not full_url.startswith('http'):
                            real_url = "https://mp." + full_url
                        else:
                            real_url = full_url
                        if 'mp.weixin.qq.com' in real_url:
                            return real_url
            
            pattern = r'var url = ["\']([^"\']+)["\']'
            match = re.search(pattern, content)
            if match:
                real_url = match.group(1)
                real_url = real_url.replace('\\/', '/')
                if 'mp.weixin.qq.com' in real_url:
                    return real_url
            
            pattern2 = r'window\.location\.href=["\']([^"\']+)["\']'
            match2 = re.search(pattern2, content)
            if match2:
                real_url = match2.group(1)
                real_url = real_url.replace('\\/', '/')
                if 'mp.weixin.qq.com' in real_url:
                    return real_url
            
            final_url = str(response.url)
            if 'mp.weixin.qq.com' in final_url:
                return final_url
            
            return None
            
        except Exception as e:
            print(f"获取真实链接失败: {e}")
            return None
