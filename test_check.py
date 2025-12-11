"""
図面チェックAI テストスクリプト
実際の図面PDFでテスト実行
"""

import sys
from pathlib import Path

# srcモジュールをインポートできるようにパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from src.pdf_parser import PDFParser
from src.checkers import CheckEngine


def test_pdf_parsing(pdf_path: str):
    """PDF解析のテスト"""
    print(f"\n{'='*80}")
    print(f"PDF解析テスト: {pdf_path}")
    print('='*80)
    
    parser = PDFParser()
    try:
        drawing_data = parser.parse(pdf_path)
        
        print(f"\n✓ 解析成功")
        print(f"  ページ数: {drawing_data.metadata.get('num_pages', 0)}")
        print(f"  タイトル: {drawing_data.metadata.get('title', 'N/A')}")
        print(f"  作成者: {drawing_data.metadata.get('author', 'N/A')}")
        
        # 各ページのテキストを表示（最初の500文字）
        for page_num, text in drawing_data.extracted_text.items():
            print(f"\n--- Page {page_num} (最初の500文字) ---")
            print(text[:500])
            if len(text) > 500:
                print("...")
        
        return drawing_data
    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_checking(drawing_data):
    """チェック機能のテスト"""
    print(f"\n{'='*80}")
    print("チェック機能テスト")
    print('='*80)
    
    check_engine = CheckEngine()
    try:
        results = check_engine.check_all(drawing_data)
        summary = check_engine.get_summary(results)
        
        print(f"\n✓ チェック完了")
        print(f"  総チェック数: {summary['total']}")
        print(f"  OK: {summary['ok']}")
        print(f"  NG: {summary['ng']}")
        print(f"  警告: {summary['warning']}")
        print(f"  必須項目NG: {summary['required_ng']}")
        print(f"  全体ステータス: {summary['status']}")
        
        if results:
            print(f"\n指摘事項:")
            for i, result in enumerate(results, 1):
                if result.status.value != "OK":
                    print(f"  {i}. [{result.category}] {result.item}: {result.message}")
        
        return results, summary
    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def main():
    # テスト対象のPDFファイル
    test_files = [
        "【仮実施図】藤原台Ⅲ25号地0911(書き込み有).pdf",
        "【藤原台Ⅲ25号地】チェックリスト0917.pdf",
        "創建工事長ヒアリングドキュメント.pdf"
    ]
    
    print("図面チェックAI テスト実行")
    print("="*80)
    
    for pdf_file in test_files:
        pdf_path = Path(pdf_file)
        if not pdf_path.exists():
            print(f"\n⚠ ファイルが見つかりません: {pdf_file}")
            continue
        
        # PDF解析テスト
        drawing_data = test_pdf_parsing(str(pdf_path))
        
        if drawing_data:
            # チェックテスト
            results, summary = test_checking(drawing_data)
        
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()

