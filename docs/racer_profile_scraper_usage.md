# レーサープロファイル スクレイパー 使用例

## 概要

`RacerScraper`は、ボートレースの公式サイトから特定の選手（レーサー）の情報を取得するためのスクレイパーです。

## 基本的な使用法

```python
from selenium import webdriver
from pyjpboatrace.scraper import RacerScraper

# WebDriverの設定
driver = webdriver.Chrome()  # Chrome WebDriverを使用

# スクレイパーの初期化
scraper = RacerScraper(driver)

# 登録番号（toban）を指定してレーサー情報を取得
toban = "2538"  # 例：高橋二朗選手
racer_data = scraper.get(toban)

# データの取得
racer_info = racer_data["racer_info"]
upcoming_races = racer_data["upcoming_races"]

print(f"選手名: {racer_info['name']}")
print(f"登録番号: {racer_info['registration_number']}")
print(f"生年月日: {racer_info['birth_date']}")

# 出場予定レースの情報
for race in upcoming_races:
    print(f"開催期間: {race['date_range']}")
    print(f"会場: {race['venue']}")
    print(f"レース名: {race['title']}")

# WebDriverを閉じる
driver.quit()
```

## 取得できる情報

### レーサー基本情報（`racer_info`）
- `name`: 選手名
- `name_kana`: 選手名（カナ）
- `registration_number`: 登録番号
- `birth_date`: 生年月日
- `height`: 身長
- `weight`: 体重
- `blood_type`: 血液型
- `branch`: 支部
- `birthplace`: 出身地
- `registration_period`: 登録期
- `class`: 級別

### 出場予定レース（`upcoming_races`）
- `date_range`: 開催期間
- `venue`: 会場
- `title`: レース名
- `race_url`: レース詳細ページのURL
- `race_type`: レース種別のリスト（例：["nighter", "morning", "summer"]）

## URLの構築

URLは以下のフォーマットで構築されます：

```
https://www.boatrace.jp/owpc/pc/data/racersearch/profile?toban={toban}
```

例：
- toban=2538の場合：`https://www.boatrace.jp/owpc/pc/data/racersearch/profile?toban=2538`

## 注意事項

1. WebDriverが必要です（Chrome、Firefox等）
2. インターネット接続が必要です
3. ボートレース公式サイトの構造変更により、動作しなくなる可能性があります
4. アクセス頻度に注意してください（サイトに負荷をかけないよう適切な間隔を設けること）

## エラーハンドリング

```python
try:
    racer_data = scraper.get("2538")
    print("データ取得成功")
except Exception as e:
    print(f"エラーが発生しました: {e}")
```
