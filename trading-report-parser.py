import xml.etree.ElementTree as ET
import pandas as pd
import os
import glob
from datetime import datetime

def parse_trading_report(xml_file):
    """特定口座年間取引報告書XMLファイルを解析する関数"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # 証券会社情報を取得
    company_info = {}
    company_elem = root.find('.//SecuritiesCompany')
    if company_elem is not None:
        company_info['name'] = company_elem.findtext('Name', '')
        company_info['code'] = company_elem.findtext('Code', '')

    # 口座所有者情報を取得
    account_holder = {}
    holder_elem = root.find('.//AccountHolder')
    if holder_elem is not None:
        account_holder['name'] = holder_elem.findtext('Name', '')
        account_holder['address'] = holder_elem.findtext('Address', '')
        account_holder['account_number'] = holder_elem.findtext('AccountNumber', '')
    
    # 取引データを取得
    transactions = []
    for transaction in root.findall('.//Transaction'):
        tx_data = {
            'date': transaction.findtext('Date', ''),
            'security_code': transaction.findtext('SecurityCode', ''),
            'security_name': transaction.findtext('SecurityName', ''),
            'transaction_type': transaction.findtext('TransactionType', ''),
            'quantity': float(transaction.findtext('Quantity', '0')),
            'price': float(transaction.findtext('Price', '0')),
            'amount': float(transaction.findtext('Amount', '0')),
            'commission': float(transaction.findtext('Commission', '0')),
            'tax': float(transaction.findtext('Tax', '0')),
            'acquisition_cost': float(transaction.findtext('AcquisitionCost', '0')),
            'profit_loss': float(transaction.findtext('ProfitLoss', '0')),
        }
        transactions.append(tx_data)
    
    # 配当情報を取得
    dividends = []
    for dividend in root.findall('.//Dividend'):
        div_data = {
            'date': dividend.findtext('PaymentDate', ''),
            'security_code': dividend.findtext('SecurityCode', ''),
            'security_name': dividend.findtext('SecurityName', ''),
            'amount': float(dividend.findtext('Amount', '0')),
            'tax_withheld': float(dividend.findtext('TaxWithheld', '0')),
        }
        dividends.append(div_data)
    
    return {
        'company_info': company_info,
        'account_holder': account_holder,
        'transactions': transactions,
        'dividends': dividends
    }

def generate_summary(data_list):
    """複数の報告書データから確定申告用のサマリーを生成する関数"""
    all_transactions = []
    all_dividends = []
    
    for data in data_list:
        all_transactions.extend(data['transactions'])
        all_dividends.extend(data['dividends'])
    
    # 取引データをDataFrameに変換
    if all_transactions:
        tx_df = pd.DataFrame(all_transactions)
        # 日付を適切なフォーマットに変換
        tx_df['date'] = pd.to_datetime(tx_df['date'])
        tx_df['year'] = tx_df['date'].dt.year
    else:
        tx_df = pd.DataFrame()
    
    # 配当データをDataFrameに変換
    if all_dividends:
        div_df = pd.DataFrame(all_dividends)
        # 日付を適切なフォーマットに変換
        div_df['date'] = pd.to_datetime(div_df['date'])
        div_df['year'] = div_df['date'].dt.year
    else:
        div_df = pd.DataFrame()
    
    # 年度別の集計結果
    summary = {}
    
    # 取引データの集計（年度別、取引タイプ別）
    if not tx_df.empty:
        years = tx_df['year'].unique()
        
        for year in years:
            year_tx = tx_df[tx_df['year'] == year]
            
            # 売却取引のみを抽出
            sales = year_tx[year_tx['transaction_type'].str.contains('売却', na=False)]
            
            # 各銘柄ごとの損益計算
            by_security = sales.groupby('security_code').agg({
                'security_name': 'first',
                'amount': 'sum',
                'acquisition_cost': 'sum',
                'profit_loss': 'sum',
                'commission': 'sum',
                'tax': 'sum'
            }).reset_index()
            
            total_profit_loss = sales['profit_loss'].sum()
            total_sales = sales['amount'].sum()
            total_acquisition_cost = sales['acquisition_cost'].sum()
            total_commission = sales['commission'].sum()
            total_tax = sales['tax'].sum()
            
            summary[year] = {
                'total_profit_loss': total_profit_loss,
                'total_sales': total_sales,
                'total_acquisition_cost': total_acquisition_cost,
                'total_commission': total_commission,
                'total_tax': total_tax,
                'by_security': by_security.to_dict('records')
            }
    
    # 配当データの集計
    if not div_df.empty:
        years = div_df['year'].unique()
        
        for year in years:
            year_div = div_df[div_df['year'] == year]
            
            # 各銘柄ごとの配当集計
            div_by_security = year_div.groupby('security_code').agg({
                'security_name': 'first',
                'amount': 'sum',
                'tax_withheld': 'sum'
            }).reset_index()
            
            total_dividend = year_div['amount'].sum()
            total_tax_withheld = year_div['tax_withheld'].sum()
            
            if year in summary:
                summary[year].update({
                    'total_dividend': total_dividend,
                    'total_tax_withheld': total_tax_withheld,
                    'dividend_by_security': div_by_security.to_dict('records')
                })
            else:
                summary[year] = {
                    'total_dividend': total_dividend,
                    'total_tax_withheld': total_tax_withheld,
                    'dividend_by_security': div_by_security.to_dict('records')
                }
    
    return summary

def export_to_excel(summary, output_file):
    """集計結果をExcelファイルに出力する関数"""
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    
    for year, data in summary.items():
        # 株式等の譲渡損益の集計シート
        if 'by_security' in data:
            securities_df = pd.DataFrame(data['by_security'])
            securities_df.to_excel(writer, sheet_name=f'{year}年_株式譲渡', index=False)
            
            # サマリー情報を追加
            summary_data = {
                '項目': ['総売却金額', '総取得費', '総売買手数料', '総税金', '総譲渡損益'],
                '金額（円）': [
                    data.get('total_sales', 0),
                    data.get('total_acquisition_cost', 0),
                    data.get('total_commission', 0),
                    data.get('total_tax', 0),
                    data.get('total_profit_loss', 0)
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name=f'{year}年_株式譲渡サマリー', index=False)
        
        # 配当所得の集計シート
        if 'dividend_by_security' in data:
            dividend_df = pd.DataFrame(data['dividend_by_security'])
            dividend_df.to_excel(writer, sheet_name=f'{year}年_配当', index=False)
            
            # サマリー情報を追加
            div_summary_data = {
                '項目': ['総配当金額', '総源泉徴収税額', '差引手取金額'],
                '金額（円）': [
                    data.get('total_dividend', 0),
                    data.get('total_tax_withheld', 0),
                    data.get('total_dividend', 0) - data.get('total_tax_withheld', 0)
                ]
            }
            div_summary_df = pd.DataFrame(div_summary_data)
            div_summary_df.to_excel(writer, sheet_name=f'{year}年_配当サマリー', index=False)
        
        # 確定申告用まとめシート
        tax_return_data = {
            '所得の種類': ['株式等の譲渡所得', '配当所得'],
            '収入金額': [
                data.get('total_sales', 0),
                data.get('total_dividend', 0)
            ],
            '必要経費/取得費': [
                data.get('total_acquisition_cost', 0) + data.get('total_commission', 0),
                0
            ],
            '所得金額': [
                data.get('total_profit_loss', 0),
                data.get('total_dividend', 0)
            ],
            '源泉徴収税額': [
                data.get('total_tax', 0),
                data.get('total_tax_withheld', 0)
            ]
        }
        tax_return_df = pd.DataFrame(tax_return_data)
        tax_return_df.to_excel(writer, sheet_name=f'{year}年_確定申告用', index=False)
    
    writer.close()

def main():
    """メイン関数"""
    # カレントディレクトリ内のXMLファイルを検索
    xml_files = glob.glob('*.xml')
    
    if not xml_files:
        print("XMLファイルが見つかりません。XMLファイルをスクリプトと同じディレクトリに配置してください。")
        return
    
    print(f"{len(xml_files)}件のXMLファイルを処理します...")
    
    # 全XMLファイルを解析
    data_list = []
    for xml_file in xml_files:
        try:
            data = parse_trading_report(xml_file)
            data_list.append(data)
            print(f"処理完了: {xml_file}")
        except Exception as e:
            print(f"エラー: {xml_file} の処理中に問題が発生しました: {e}")
    
    if not data_list:
        print("処理可能なデータがありませんでした。")
        return
    
    # 集計処理
    summary = generate_summary(data_list)
    
    # 現在の年月日を取得してファイル名に追加
    date_str = datetime.now().strftime('%Y%m%d')
    output_file = f'確定申告用証券取引集計_{date_str}.xlsx'
    
    # Excelファイルに出力
    export_to_excel(summary, output_file)
    
    print(f"処理が完了しました。結果は {output_file} に保存されました。")

if __name__ == "__main__":
    main()
