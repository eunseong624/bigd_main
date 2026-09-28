"""
종목 하나의 현재가를 네이버 API로 조회해 텔레그램 메시지로 보내는 스크립트.

지난주에는 "안녕하세요" 같은 고정된 문구를 보냈지만, 이번주부터는 조회해서 얻은 값을
메시지에 담아 보낸다. 관심종목을 여러 개로 늘리는 것은 다음에 한다.

`python notify_stock_price.py`로 직접 실행한다.
"""
import os
import time
import requests
from dotenv import load_dotenv

# 조회할 종목코드. 지금은 여기 직접 적어 두고, 나중에 파일에서 읽어오도록 바꾼다.
STOCK_CODE = "005930"  # 삼성전자

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def fetch_naver_current_price(code: str, retries: int = 2) -> dict:
    """네이버 증권 API로 종목의 현재가 정보를 조회합니다."""
    url = f"https://m.stock.naver.com/api/stock/{code}/basic"
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=3)
            if response.status_code != 200:
                print(f"❌ [{code}] 네이버 현재가 조회 실패 (응답 코드: {response.status_code}, {attempt}/{retries}번째 시도)")
            else:
                data = response.json()
                price_str = data.get("closePrice", "0").replace(",", "")
                price = int(price_str) if price_str.isdigit() else 0
                if price <= 0:
                    print(f"❌ [{code}] 가격을 숫자로 읽지 못했습니다 (closePrice: {data.get('closePrice')!r}, {attempt}/{retries}번째 시도)")
                else:
                    return {
                        "code": code,
                        "name": data.get("stockName", "알 수 없음"),
                        "price": price,
                        "rate": float(data.get("fluctuationsRatio", "0") or "0"),
                        "is_open": data.get("marketStatus") == "OPEN",
                        "traded_at": data.get("localTradedAt"),
                    }
        except Exception as e:
            print(f"❌ [{code}] 네이버 현재가 조회 중 오류 발생: {e} ({attempt}/{retries}번째 시도)")
        if attempt < retries:
            time.sleep(1)
    return None


def send_telegram_message(text: str) -> bool:
    """텔레그램 sendMessage API로 텍스트 메시지를 전송합니다."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=data, timeout=15)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 텔레그램 메시지 전송 중 오류 발생: {e}")
        return False


def format_rate_badge(price: int, rate: float) -> str:
    """가격과 등락률을 보기 좋은 문자열로 포맷합니다."""
    prefix = f"{price:,}원"
    if rate > 0:
        return f"{prefix} 🔺 +{rate}%"
    if rate < 0:
        return f"{prefix} ▼ {rate}%"
    return f"{prefix} ▫️▫️ 0.0%"


info = fetch_naver_current_price(STOCK_CODE)
if info is None:
    print("❌ 현재가를 가져오지 못했습니다. 네이버 API 상태를 확인해 주세요.")
else:
    telegram_message = (
        f"📈 {info['name']} ({STOCK_CODE})"
        f"\n{format_rate_badge(info['price'], info['rate'])}"
    )
    if send_telegram_message(telegram_message):
        print("✅ 현재가 메시지를 텔레그램으로 전송했습니다!")
    else:
        print("❌ 현재가 메시지 전송에 실패했습니다.")