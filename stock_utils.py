def resolve_today_price(price: int, is_open: bool, intraday_minutes: list,
                        daily_closes: list) -> int:
    """분봉/현재가 조회 결과로 build_price_chart()에 넘길 "오늘" 가격을 결정합니다. 장이
    닫혀있고(is_open=False) 분봉도 없으면(장마감 후~다음 장 시작 전) 지금 조회한 가격은
    DB의 마지막 종가와 같은 값이 필연적이므로 None을 돌려줘, "오늘" 점을 따로 안 그리게
    합니다. 단 daily_closes(과거 종가)가 하나도 없으면 비교할 대상 자체가 없으므로 이 예외는
    적용하지 않고 현재가를 그대로 살립니다. notify_stock_price.py/dashboard.py가 공유합니다."""
    # 삼항 표현식(조건부 표현식): "조건이 참이면 price, 거짓이면 None"을 한 줄로 쓴 것.
    # is_open이 True(장중)면 무조건 살아있는 값이라 그대로 쓰고, is_open이 False라도
    # intraday_minutes가 비어있지 않으면(장마감 직후라 분봉은 남아있는 경우) 마찬가지로 살려둔다.
    # 세 번째 조건(not daily_closes)은 "지금 가격은 마지막 종가와 중복이라 뺀다"는 위 근거가
    # 언제 성립하는지를 따진 것이다 — 비교할 과거 종가가 하나도 없으면 중복될 값 자체가 없으므로
    # 그 근거가 성립하지 않는다. 이때 현재가는 그 종목의 유일한 데이터이므로 반드시 살려야 하고,
    # 버리면 그릴 점이 하나도 없어 축과 격자만 있는 빈 그래프가 만들어진다. 새로 추가한 종목이나
    # collect_daily_close.py가 아직 한 번도 실행되지 않은 최초 실행에서 이 상황이 생긴다.
    # 위 셋 다 아니면(장마감 후~다음 장 시작 전, 히스토리는 있음) None을 돌려준다. 빈 리스트([])는
    # 파이썬에서 False로 취급되므로 intraday_minutes/daily_closes만 써도 "비어있는지" 확인이 된다.
    return price if (is_open or intraday_minutes or not daily_closes) else None

def load_price_history() -> dict:
    """Turso DB에서 종목별 종가 히스토리를 읽어 {code: [{"date": "YYYYMMDD", "close": 가격}, ...]}
    형태(날짜 오름차순)로 반환합니다. 예전에는 이 함수가 price_history.json 파일을 읽었지만,
    Turso로 옮긴 뒤로는 DB에서 직접 SELECT한다."""
    try:
        # with 문(컨텍스트 매니저): 블록이 끝나면(정상 종료든 예외든) client.close()가 자동으로
        # 호출되어 DB 연결이 확실히 정리된다 — 파일을 open()으로 열었을 때와 같은 원리다.
        with get_turso_client() as client:
            # ORDER BY code, date: 종목코드 순으로, 같은 종목 안에서는 날짜 오름차순으로 정렬해서
            # 받아온다 (그래프를 그릴 때 날짜순 정렬이 이미 돼 있어야 하므로 여기서 미리 정렬한다).
            result = client.execute("SELECT code, date, close FROM price_history ORDER BY code, date")
    except Exception as e:
        print(f"❌ Turso DB에서 종가 히스토리를 읽지 못했습니다: {e}")
        return {}

    history: dict = {}
    # result.rows는 (code, date, close) 튜플들의 목록이다. for 문에서 (code, date, close)로 바로
    # 풀어서(unpacking) 받는다.
    for code, date, close in result.rows:
        # dict.setdefault(key, [])는 "key가 이미 있으면 그 값을 그대로 쓰고, 없으면 빈 리스트를
        # 새로 만들어 넣은 뒤 그걸 반환"한다 — 종목별로 리스트를 매번 존재 확인하며 만드는 코드
        # (if code not in history: history[code] = []) 를 한 줄로 줄인 것이다.
        history.setdefault(code, []).append({"date": date, "close": close})
    return history