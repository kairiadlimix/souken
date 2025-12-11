"""
図面チェックAIシステム - Streamlit Web UI
ブラウザから簡単に図面をチェックできるWebアプリケーション
"""

import streamlit as st
import sys
from pathlib import Path
import tempfile
import os
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.pdf_parser import PDFParser
from src.checkers import CheckEngine, CheckStatus, Importance

# ページ設定
st.set_page_config(
    page_title="図面チェックAIシステム",
    page_icon="📐",
    layout="wide"
)

# タイトル
st.title("📐 図面チェックAIシステム")
st.markdown("---")
st.markdown("設計事務所から提出される図面を自動的にチェックし、創建基準に基づいた指摘を行います。")

# サイドバー
with st.sidebar:
    st.header("📋 使い方")
    st.markdown("""
    1. **PDFファイルをアップロード**
       - 図面PDFファイルを選択してください
    
    2. **チェック実行**
       - 「チェック実行」ボタンをクリック
    
    3. **結果確認**
       - チェック結果が表示されます
       - 指摘事項を確認して修正してください
    """)
    
    st.markdown("---")
    st.header("✅ チェック項目")
    st.markdown("""
    **必須記載事項**
    - 図面番号
    - 図面名
    - 縮尺
    - 作成日
    - 作成者
    
    **創建特有項目**
    - 外断熱仕様
    - 第一種換気システム
    - 釘ピッチ（150mm以下）
    - 隠蔽部分の施工方法
    """)

# ファイルアップロード
st.header("📁 図面ファイルのアップロード")
uploaded_file = st.file_uploader(
    "PDFファイルを選択してください",
    type=['pdf'],
    help="図面PDFファイルをアップロードしてください"
)

if uploaded_file is not None:
    # ファイル情報を表示
    st.info(f"📄 ファイル名: {uploaded_file.name}")
    st.info(f"📊 ファイルサイズ: {uploaded_file.size / 1024:.2f} KB")
    
    # チェック実行ボタン
    if st.button("🔍 チェック実行", type="primary", use_container_width=True):
        with st.spinner("図面を解析中..."):
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name
            
            try:
                # PDF解析
                parser = PDFParser()
                drawing_data = parser.parse(tmp_path)
                
                st.success(f"✓ PDF解析完了 ({drawing_data.metadata.get('num_pages', 0)}ページ)")
                
                # チェック実行
                with st.spinner("チェックを実行中..."):
                    check_engine = CheckEngine()
                    results = check_engine.check_all(drawing_data)
                    summary = check_engine.get_summary(results)
                
                # 結果表示
                st.markdown("---")
                st.header("📊 チェック結果")
                
                # サマリー
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("総チェック数", summary['total'])
                with col2:
                    st.metric("✓ OK", summary['ok'], delta=None)
                with col3:
                    st.metric("✗ NG", summary['ng'], delta=None, delta_color="inverse")
                with col4:
                    st.metric("⚠ 警告", summary['warning'], delta=None)
                
                # 全体ステータス
                status_color = {
                    'OK': '🟢',
                    'WARNING': '🟡',
                    'NG': '🔴'
                }
                status_emoji = status_color.get(summary['status'], '⚪')
                st.markdown(f"### {status_emoji} 全体ステータス: {summary['status']}")
                
                # 必須項目NGがある場合
                if summary['required_ng'] > 0:
                    st.error(f"⚠️ **必須項目で{summary['required_ng']}件のNGがあります**")
                
                # 結果の詳細
                st.markdown("---")
                st.header("📝 指摘事項")
                
                # カテゴリごとにグループ化
                by_category = {}
                for result in results:
                    if result.status != CheckStatus.OK:
                        if result.category not in by_category:
                            by_category[result.category] = []
                        by_category[result.category].append(result)
                
                if by_category:
                    for category, category_results in by_category.items():
                        with st.expander(f"📂 {category} ({len(category_results)}件)", expanded=True):
                            for i, result in enumerate(category_results, 1):
                                # ステータスアイコン
                                if result.status == CheckStatus.NG:
                                    status_icon = "❌"
                                    status_color = "red"
                                else:
                                    status_icon = "⚠️"
                                    status_color = "orange"
                                
                                # 重要度アイコン
                                if result.importance == Importance.REQUIRED:
                                    importance_badge = "🔴 **【必須】**"
                                else:
                                    importance_badge = "🟡 **【推奨】**"
                                
                                st.markdown(f"""
                                **{i}. {status_icon} {importance_badge} {result.item}**
                                
                                {result.message}
                                """)
                                
                                if result.suggestion:
                                    st.info(f"💡 推奨: {result.suggestion}")
                                
                                if result.page_number:
                                    st.caption(f"📄 ページ: {result.page_number}")
                                
                                st.markdown("---")
                else:
                    st.success("🎉 指摘事項はありませんでした！")
                
                # OK項目の表示（オプション）
                ok_results = [r for r in results if r.status == CheckStatus.OK]
                if ok_results and st.checkbox("✓ OK項目も表示する"):
                    st.markdown("---")
                    st.header("✅ チェック通過項目")
                    for result in ok_results:
                        st.markdown(f"✓ {result.item}")
                
                # 結果をセッションに保存（ダウンロード用）
                st.session_state['check_results'] = {
                    'file_name': uploaded_file.name,
                    'summary': summary,
                    'results': [
                        {
                            'category': r.category,
                            'item': r.item,
                            'status': r.status.value,
                            'message': r.message,
                            'importance': r.importance.value,
                            'page_number': r.page_number,
                            'suggestion': r.suggestion
                        }
                        for r in results
                    ],
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
                st.exception(e)
            
            finally:
                # 一時ファイルを削除
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    # 結果のダウンロード（結果がある場合）
    if 'check_results' in st.session_state:
        st.markdown("---")
        st.header("💾 結果のダウンロード")
        
        # テキスト形式でダウンロード
        results_text = f"""
図面チェック結果レポート
========================

ファイル名: {st.session_state['check_results']['file_name']}
チェック日時: {st.session_state['check_results']['timestamp']}

サマリー
--------
総チェック数: {st.session_state['check_results']['summary']['total']}
OK: {st.session_state['check_results']['summary']['ok']}
NG: {st.session_state['check_results']['summary']['ng']}
警告: {st.session_state['check_results']['summary']['warning']}
必須項目NG: {st.session_state['check_results']['summary']['required_ng']}
全体ステータス: {st.session_state['check_results']['summary']['status']}

指摘事項
--------
"""
        for result in st.session_state['check_results']['results']:
            if result['status'] != 'OK':
                results_text += f"""
【{result['category']}】
- {result['item']}: {result['message']}
  重要度: {result['importance']}
"""
                if result['suggestion']:
                    results_text += f"  推奨: {result['suggestion']}\n"
                if result['page_number']:
                    results_text += f"  ページ: {result['page_number']}\n"
        
        st.download_button(
            label="📥 結果をテキスト形式でダウンロード",
            data=results_text,
            file_name=f"check_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

else:
    st.info("👆 上記からPDFファイルをアップロードしてください")

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>図面チェックAIシステム v1.0.0 | 創建内部使用</small>
</div>
""", unsafe_allow_html=True)

