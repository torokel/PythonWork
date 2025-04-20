import os
import xml.etree.ElementTree as ET
import pandas as pd

# XMLネームスペースの定義
ns = {
    "kyotsu": "http://xml.e-tax.nta.go.jp/XSD/kyotsu",
    "general": "http://xml.e-tax.nta.go.jp/XSD/general"
}

# カレントディレクトリ内のXMLファイルを探す
xml_files = [f for f in os.listdir() if f.endswith(".xml")]
if not xml_files:
    print("⚠ XMLファイルが見つかりません！")
    exit()

# 最初に見つけたXMLファイルを使用
xml_file_path = xml_files[0]
print(f"📂 読み込むXMLファイル: {xml_file_path}")

# XMLを解析
tree = ET.parse(xml_file_path)
root = tree.getroot()

# データを格納するリスト
transactions = []

# 各売却データを取得（売却ごとに日付情報を探す）
for transaction in root.findall(".//kyotsu:*", ns):  
    stock_name = transaction.find("kyotsu:ZLG00040", ns)
    quantity = transaction.find("kyotsu:ZLG00050", ns)
    amount = transaction.find("kyotsu:ZLG00060", ns)

    # 売却ごとの日付を探す（売却データ内の `general` タグを検索）
    date_info = transaction.find(".//general:*", ns)

    era = transaction.find(".//general:era", ns) if transaction.find(".//general:era", ns) is not None else None
    year = transaction.find(".//general:yy", ns) if transaction.find(".//general:yy", ns) is not None else None
    month = transaction.find(".//general:mm", ns) if transaction.find(".//general:mm", ns) is not None else None
    day = transaction.find(".//general:dd", ns) if transaction.find(".//general:dd", ns) is not None else None

    # Noneチェックしてデータを取得
    stock_name = stock_name.text if stock_name is not None else ""
    
    # 数値データの安全な変換
    try:
        quantity = int(quantity.text) if quantity is not None and quantity.text.isdigit() else 0
    except ValueError:
        quantity = 0

    try:
        amount = float(amount.text) if amount is not None and amount.text.replace('.', '').isdigit() else 0.0
    except (ValueError, AttributeError):
        amount = 0.0

    # 売却日を適切に整形（売却ごとに取得する）
    if era is not None and year is not None and month is not None and day is not None:
        date_text = f"令和{era.text}年{year.text}月{month.text}日"
    else:
        date_text = "データなし"

    # デバッグ: 取得したデータを表示
    print(f"DEBUG: 銘柄={stock_name}, 株数={quantity}, 金額={amount}, 売却日={date_text}")

    # 有効なデータを追加
    if stock_name and amount > 0:
        transactions.append([stock_name, quantity, amount, date_text])

# データフレーム化
df = pd.DataFrame(transactions, columns=["銘柄", "株数", "金額", "売却日"])

# 結果を表示
print("\n=== 売却データ ===")
print(df)

# データが1行もない場合のデバッグ
if df.shape[0] == 0:
    print("⚠ データが取得できませんでした。XMLの構造を再確認してください！")

# CSVとして保存（Excelで開きやすい Shift_JIS で保存）
output_file = "売却データ.csv"
if os.path.exists(output_file):
    os.remove(output_file)
df.to_csv(output_file, index=False, encoding="shift_jis")
print(f"\n✅ CSVファイル '{output_file}' を Shift_JIS で作成しました！")
