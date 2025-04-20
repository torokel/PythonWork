import os
import xml.etree.ElementTree as ET
import pandas as pd

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

# 外国配当金データを抽出
foreign_dividends = []
for transaction in root.findall(".//ZLG00020"):  # 全ての配当データを取得
    stock_name = transaction.find("ZLG00040").text if transaction.find("ZLG00040") is not None else ""
    dividend_amount = transaction.find("ZLG00060").text if transaction.find("ZLG00060") is not None else ""

    # データの取得結果をデバッグ用に表示
    print(f"DEBUG: 銘柄={stock_name}, 配当={dividend_amount}")

    # 米国株（ETF含む）を判定
    if stock_name and dividend_amount:
        try:
            dividend_amount = float(dividend_amount)
            tax_withheld = dividend_amount * 0.10  # 米国源泉徴収税10%
            foreign_dividends.append([stock_name, dividend_amount, tax_withheld])
        except ValueError:
            continue

# データフレーム化
dividends_df = pd.DataFrame(foreign_dividends, columns=["銘柄", "配当金額（税引前）", "米国源泉徴収税額"])

# 結果を表示
print("\n=== 外国配当金データ ===")
print(dividends_df)

# 1行しかない場合のデバッグ
if dividends_df.shape[0] <= 1:
    print("⚠ データが1行しかありません。XMLの構造を確認してください！")

# CSVとして保存（Excelで開きやすい Shift_JIS で保存）
output_file = "外国配当金リスト.csv"
dividends_df.to_csv(output_file, index=False, encoding="shift_jis")
print(f"\n✅ CSVファイル '{output_file}' を Shift_JIS で作成しました！")
