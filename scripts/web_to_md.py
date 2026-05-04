import argparse
import os
import sys
from urllib.parse import urlparse

import trafilatura


def get_default_output_dir():
    # 取得目前腳本所在目錄的上一層目錄，並組合 wiki/raw 作為預設路徑
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    output_dir = os.path.join(project_dir, "wiki", "raw")
    
    return output_dir


def extract_content_from_url(url):
    # 下載網頁內容
    downloaded = trafilatura.fetch_url(url)
    
    # 檢查是否成功下載網頁
    if not downloaded:
        print(f"無法下載網頁內容: {url}")
        return None
        
    # 提取文章主體並轉換為 Markdown 格式
    result = trafilatura.extract(
        downloaded,
        output_format="markdown"
    )
    
    return result


def main():
    # 設定命令列參數解析器
    parser = argparse.ArgumentParser(description="將網頁內容轉換為 Markdown 檔案")
    parser.add_argument("url", help="要抓取的網頁網址")
    parser.add_argument("-o", "--output", help="指定的輸出檔案名稱 (可選)")
    args = parser.parse_args()
    
    # 從參數取得網址
    url = args.url
    
    # 呼叫函式執行內容抓取與轉換
    markdown_content = extract_content_from_url(url)
    
    # 檢查轉換結果是否有效
    if not markdown_content:
        print("無法提取網頁正文")
        sys.exit(1)
        
    # 取得預設的輸出目錄路徑
    output_dir = get_default_output_dir()
    
    # 檢查輸出目錄是否存在，若無則自動建立
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 初始化檔案名稱變數
    filename = ""
        
    # 判斷使用者是否指定了輸出檔案名稱
    if args.output:
        filename = args.output
        
        # 確保檔案名稱包含 Markdown 附檔名
        if not filename.endswith(".md"):
            filename = filename + ".md"
            
    else:
        # 解析網址以自動產生檔案名稱
        parsed_url = urlparse(url)
        path = parsed_url.path.strip("/")
        
        # 依據網址路徑或網域來命名檔案
        if path:
            filename = path.replace("/", "_") + ".md"
        else:
            filename = parsed_url.netloc + ".md"
            
    # 組合完整的檔案絕對路徑
    file_path = os.path.join(output_dir, filename)
    
    # 開啟檔案並寫入 Markdown 內容
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    # 輸出執行成功的訊息
    print(f"成功將網頁內容儲存至: {file_path}")


if __name__ == "__main__":
    main()
