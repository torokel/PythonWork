import xml.etree.ElementTree as ET
import os

# XMLファイルのパス（カレントディレクトリ内のXMLファイルを探す）
xml_files = [f for f in os.listdir() if f.endswith(".xml")]
if not xml_files:
    print("⚠ XMLファイルが見つかりません！")
    exit()
xml_file_path = xml_files[0]

# XMLを解析
tree = ET.parse(xml_file_path)
root = tree.getroot()

# 出力ファイルを作成
debug_file = "xml_debug_output.txt"

# タグとその中身をすべて保存
with open(debug_file, "w", encoding="utf-8") as f:
    for elem in root.iter():
        f.write(f"タグ: {elem.tag}, 値: {elem.text}\n")

print(f"\n✅ XMLデータの内容を '{debug_file}' に保存しました！")
