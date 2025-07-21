

import os
import requests
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

# 從環境變數中獲取 API 金鑰
gnews_api_key = os.getenv("GNEWS_API_KEY")

print("--- GNews API 連線測試 ---")

# 檢查 API 金鑰是否存在
if not gnews_api_key or gnews_api_key == "YOUR_GNEWS_API_KEY":
    print("錯誤：在 .env 檔案中找不到 GNEWS_API_KEY，或其仍為預設值。")
    print("請確認您的 .env 檔案中包含有效的金鑰，例如：GNEWS_API_KEY=\"your_actual_api_key\"")
else:
    # 為了安全，只顯示金鑰的最後四個字元
    print(f"找到 API 金鑰：...{gnews_api_key[-4:]}")
    
    # 建立 API 請求 URL
    search_query = "Taiwan"
    url = f"https://gnews.io/api/v4/search?q={search_query}&lang=zh-TW&country=tw&max=1&token={gnews_api_key}"
    
    # 為了安全，不在日誌中顯示完整的 URL
    print(f"正在向 GNews 發送請求...")

    try:
        # 發送請求
        response = requests.get(url)
        
        # 輸出結果
        print("\n--- 伺服器回應 ---")
        print(f"HTTP 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            print("成功！API 連線正常。")
            print("回應內容 (JSON):")
            print(response.json())
        elif response.status_code == 401:
            print("錯誤 (401): 未授權。您的 API 金鑰無效或已被停用。")
        elif response.status_code == 403:
            print("錯誤 (403): 禁止存取。您可能已超出每日請求限制，或帳戶存取權限有問題。")
        elif response.status_code == 429:
             print("錯誤 (429): 請求過多。您已超出請求頻率限制。")
        else:
            print(f"發生未預期的錯誤。伺服器回應文本：")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"\n--- 網路錯誤 ---")
        print(f"無法連線至 GNews API。請檢查您的網路連線。")
        print(f"錯誤詳情: {e}")

print("\n--- 測試結束 ---")

