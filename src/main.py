"""
図面チェックAI メインスクリプト
コマンドラインから実行可能
"""

import sys
import argparse
import json
from pathlib import Path

from .pdf_parser import PDFParser
from .checkers import CheckEngine, CheckStatus, Importance


def format_result(result) -> dict:
    """CheckResultを辞書形式に変換"""
    return {
        'category': result.category,
        'item': result.item,
        'status': result.status.value,
        'message': result.message,
        'importance': result.importance.value,
        'page_number': result.page_number,
        'suggestion': result.suggestion
    }


def main():
    parser = argparse.ArgumentParser(description='図面チェックAIシステム')
    parser.add_argument('pdf_path', type=str, help='チェックするPDFファイルのパス')
    parser.add_argument('--output', '-o', type=str, help='結果を保存するJSONファイルのパス')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='text',
                       help='出力形式 (default: text)')
    
    args = parser.parse_args()
    
    # PDFファイルの存在確認
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"エラー: ファイルが見つかりません: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"図面を読み込んでいます: {pdf_path}")
    
    # PDF解析
    pdf_parser = PDFParser()
    try:
        drawing_data = pdf_parser.parse(str(pdf_path))
        print(f"✓ PDF解析完了 ({drawing_data.metadata.get('num_pages', 0)}ページ)")
    except Exception as e:
        print(f"エラー: PDF解析に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)
    
    # チェック実行
    print("チェックを実行しています...")
    check_engine = CheckEngine()
    try:
        results = check_engine.check_all(drawing_data)
        summary = check_engine.get_summary(results)
    except Exception as e:
        print(f"エラー: チェック実行に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 結果出力
    if args.format == 'json':
        output_data = {
            'file_path': str(pdf_path),
            'summary': summary,
            'results': [format_result(r) for r in results]
        }
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"\n結果を保存しました: {args.output}")
        else:
            print(json.dumps(output_data, ensure_ascii=False, indent=2))
    else:
        # テキスト形式で出力
        print("\n" + "="*80)
        print("チェック結果サマリー")
        print("="*80)
        print(f"総チェック数: {summary['total']}")
        print(f"  OK: {summary['ok']}")
        print(f"  NG: {summary['ng']}")
        print(f"  警告: {summary['warning']}")
        print(f"  必須項目NG: {summary['required_ng']}")
        print(f"  全体ステータス: {summary['status']}")
        print("="*80)
        
        if results:
            print("\n指摘事項:")
            print("-"*80)
            
            # カテゴリごとにグループ化
            by_category = {}
            for result in results:
                if result.status != CheckStatus.OK:
                    if result.category not in by_category:
                        by_category[result.category] = []
                    by_category[result.category].append(result)
            
            for category, category_results in by_category.items():
                print(f"\n【{category}】")
                for i, result in enumerate(category_results, 1):
                    status_symbol = "✗" if result.status == CheckStatus.NG else "!"
                    importance_symbol = "【必須】" if result.importance == Importance.REQUIRED else "【推奨】"
                    print(f"  {i}. {status_symbol} {importance_symbol} {result.item}")
                    print(f"     {result.message}")
                    if result.suggestion:
                        print(f"     → {result.suggestion}")
                    print()
        else:
            print("\n指摘事項はありませんでした。")
        
        if args.output:
            # テキスト形式でもファイルに保存
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("チェック結果サマリー\n")
                f.write("="*80 + "\n")
                f.write(f"総チェック数: {summary['total']}\n")
                f.write(f"  OK: {summary['ok']}\n")
                f.write(f"  NG: {summary['ng']}\n")
                f.write(f"  警告: {summary['warning']}\n")
                f.write(f"  必須項目NG: {summary['required_ng']}\n")
                f.write(f"  全体ステータス: {summary['status']}\n")
                f.write("="*80 + "\n\n")
                
                if results:
                    f.write("指摘事項:\n")
                    f.write("-"*80 + "\n")
                    for category, category_results in by_category.items():
                        f.write(f"\n【{category}】\n")
                        for i, result in enumerate(category_results, 1):
                            status_symbol = "✗" if result.status == CheckStatus.NG else "!"
                            importance_symbol = "【必須】" if result.importance == Importance.REQUIRED else "【推奨】"
                            f.write(f"  {i}. {status_symbol} {importance_symbol} {result.item}\n")
                            f.write(f"     {result.message}\n")
                            if result.suggestion:
                                f.write(f"     → {result.suggestion}\n")
                            f.write("\n")
            
            print(f"\n結果を保存しました: {args.output}")


if __name__ == "__main__":
    main()

