"""
PDF Parser Module
図面PDFを読み込み、テキストやメタデータを抽出する
"""

import PyPDF2
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# pdfplumberをオプションでインポート（Vercelでは使用しない）
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    pdfplumber = None

# Gemini OCRをオプションでインポート
try:
    from .gemini_ocr import GeminiOCR
    GEMINI_OCR_AVAILABLE = True
except ImportError:
    GEMINI_OCR_AVAILABLE = False
    GeminiOCR = None


@dataclass
class TextElement:
    """テキスト要素（位置情報付き）"""
    text: str
    x0: float  # 左端のX座標
    y0: float  # 下端のY座標
    x1: float  # 右端のX座標
    y1: float  # 上端のY座標
    page_number: int


@dataclass
class PageData:
    """1ページ分のデータ"""
    page_number: int
    text: str
    width: float
    height: float
    text_elements: List[TextElement]  # 位置情報付きテキスト要素


@dataclass
class DrawingData:
    """図面データ"""
    file_path: str
    pages: List[PageData]
    metadata: Dict[str, any]
    extracted_text: Dict[int, str]  # page_num -> text
    text_elements: Dict[int, List[TextElement]]  # page_num -> List[TextElement]
    gemini_ocr_text: Dict[int, str] = None  # page_num -> Gemini OCRで抽出したテキスト
    gemini_ocr_used: bool = False  # Gemini OCRが使用されたかどうか


class PDFParser:
    """PDF解析クラス"""
    
    def __init__(self, use_gemini_ocr: bool = False, gemini_api_key: Optional[str] = None, force_gemini_ocr: bool = False):
        """
        Args:
            use_gemini_ocr: pdfplumberで抽出できない場合にGemini OCRを使用するか（フォールバック）
            gemini_api_key: Gemini APIキー（未指定の場合は環境変数から取得）
            force_gemini_ocr: Trueの場合、pdfplumberを使わずGemini OCRのみを使用
        """
        self.supported_formats = ['.pdf']
        self.force_gemini_ocr = force_gemini_ocr
        self.use_gemini_ocr = (use_gemini_ocr or force_gemini_ocr) and GEMINI_OCR_AVAILABLE
        self.gemini_ocr = None
        
        if self.use_gemini_ocr:
            try:
                self.gemini_ocr = GeminiOCR(api_key=gemini_api_key)
            except Exception as e:
                print(f"Gemini OCR初期化エラー: {e}")
                if self.force_gemini_ocr:
                    raise  # force_gemini_ocrがTrueの場合はエラーを投げる
                self.use_gemini_ocr = False
    
    def parse(self, pdf_path: str) -> DrawingData:
        """
        PDFを解析してDrawingDataを返す
        
        Args:
            pdf_path: PDFファイルのパス
            
        Returns:
            DrawingData: 解析された図面データ
        """
        pages = []
        extracted_text = {}
        metadata = {}
        
        # PyPDF2でメタデータを取得
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = {
                    'title': pdf_reader.metadata.get('/Title', '') if pdf_reader.metadata else '',
                    'author': pdf_reader.metadata.get('/Author', '') if pdf_reader.metadata else '',
                    'creator': pdf_reader.metadata.get('/Creator', '') if pdf_reader.metadata else '',
                    'producer': pdf_reader.metadata.get('/Producer', '') if pdf_reader.metadata else '',
                    'creation_date': pdf_reader.metadata.get('/CreationDate', '') if pdf_reader.metadata else '',
                    'modification_date': pdf_reader.metadata.get('/ModDate', '') if pdf_reader.metadata else '',
                    'num_pages': len(pdf_reader.pages)
                }
        except Exception as e:
            print(f"メタデータ取得エラー: {e}")
        
        # Gemini OCRを強制使用する場合
        if self.force_gemini_ocr and self.gemini_ocr:
            print("Gemini OCRのみを使用してPDFを解析します...")
            try:
                gemini_ocr_text = self.gemini_ocr.extract_text_from_pdf(pdf_path)
                extracted_text = gemini_ocr_text
                text_elements_dict = {page_num: [] for page_num in extracted_text.keys()}
                gemini_ocr_used = True
                
                # ページデータを作成（位置情報は取得できない）
                for page_num, text in extracted_text.items():
                    page_data = PageData(
                        page_number=page_num,
                        text=text,
                        width=0.0,
                        height=0.0,
                        text_elements=[]
                    )
                    pages.append(page_data)
            except Exception as e:
                error_msg = str(e)
                if "quota" in error_msg.lower() or "rate" in error_msg.lower() or "429" in error_msg:
                    print("⚠ Gemini OCRのレート制限に達しました。pdfplumberにフォールバックします...")
                    # フォールバック: pdfplumberを使用
                    self.force_gemini_ocr = False
                    self.use_gemini_ocr = False
                else:
                    raise  # その他のエラーは再発生
        else:
            # pdfplumberでテキスト抽出（より精度が高い）
            # Vercelではpdfplumberが利用できないため、PyPDF2にフォールバック
            text_elements_dict = {}
            gemini_ocr_text = {}
            gemini_ocr_used = False
            
            if PDFPLUMBER_AVAILABLE:
                try:
                    with pdfplumber.open(pdf_path) as pdf:
                    for page_num, page in enumerate(pdf.pages, start=1):
                        text = page.extract_text() or ""
                        
                        # pdfplumberでテキストが抽出できない、または短い場合（画像ベースPDFの可能性）
                        # Gemini OCRをフォールバックとして使用
                        if self.use_gemini_ocr and self.gemini_ocr and (not text or len(text.strip()) < 50):
                            try:
                                print(f"ページ{page_num}: pdfplumberでテキストが抽出できませんでした。Gemini OCRを試行します...")
                                gemini_text = self.gemini_ocr.extract_text_from_pdf_page(pdf_path, page_num)
                                if gemini_text and len(gemini_text.strip()) > 0:
                                    text = gemini_text
                                    gemini_ocr_text[page_num] = gemini_text
                                    gemini_ocr_used = True
                                    print(f"ページ{page_num}: Gemini OCRでテキスト抽出成功（{len(gemini_text)}文字）")
                            except Exception as e:
                                print(f"ページ{page_num}: Gemini OCRエラー: {e}")
                                # Gemini OCRが失敗してもpdfplumberの結果（空文字列）を使用
                        
                        extracted_text[page_num] = text
                        
                        # 位置情報付きテキスト要素を取得
                        text_elements = []
                        try:
                            # pdfplumberのwords（単語単位）を使用
                            words = page.extract_words()
                            if words:
                                # 単語をグループ化してテキスト要素を作成
                                current_text = ""
                                current_x0 = None
                                current_y0 = None
                                current_x1 = None
                                current_y1 = None
                                
                                for word in words:
                                    word_text = word.get('text', '')
                                    if word_text.strip():
                                        word_x0 = word.get('x0', 0)
                                        word_y0 = word.get('top', 0)  # pdfplumberは'top'と'bottom'を使用
                                        word_x1 = word.get('x1', 0)
                                        word_y1 = word.get('bottom', 0)
                                        
                                        # 同じ行かどうか判定（Y座標の差が小さい場合）
                                        if current_text and abs(word_y0 - (current_y0 or 0)) > 10:
                                            # 新しい行に移った場合、前の要素を保存
                                            if current_text.strip():
                                                text_elements.append(TextElement(
                                                    text=current_text.strip(),
                                                    x0=current_x0 or 0,
                                                    y0=current_y0 or 0,
                                                    x1=current_x1 or 0,
                                                    y1=current_y1 or 0,
                                                    page_number=page_num
                                                ))
                                            current_text = word_text
                                            current_x0 = word_x0
                                            current_y0 = word_y0
                                            current_x1 = word_x1
                                            current_y1 = word_y1
                                        else:
                                            current_text += " " + word_text if current_text else word_text
                                            if current_x0 is None:
                                                current_x0 = word_x0
                                                current_y0 = word_y0
                                            current_x1 = word_x1
                                            current_y1 = word_y1
                                
                                # 最後の要素を保存
                                if current_text.strip():
                                    text_elements.append(TextElement(
                                        text=current_text.strip(),
                                        x0=current_x0 or 0,
                                        y0=current_y0 or 0,
                                        x1=current_x1 or 0,
                                        y1=current_y1 or 0,
                                        page_number=page_num
                                    ))
                        except Exception as e:
                            print(f"位置情報取得エラー（ページ{page_num}）: {e}")
                            # エラーが発生した場合は空のリストを返す
                        
                        text_elements_dict[page_num] = text_elements
                        
                        page_data = PageData(
                            page_number=page_num,
                            text=text,
                            width=page.width,
                            height=page.height,
                            text_elements=text_elements
                        )
                        pages.append(page_data)
                except Exception as e:
                    print(f"pdfplumberテキスト抽出エラー: {e}")
                    # フォールバック: PyPDF2を使用
                    PDFPLUMBER_AVAILABLE = False  # このセッションでは使用しない
            
            if not PDFPLUMBER_AVAILABLE:
                # フォールバック: PyPDF2を使用
                print("pdfplumberが利用できないため、PyPDF2を使用します...")
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages, start=1):
                        text = page.extract_text() or ""
                        extracted_text[page_num] = text
                        
                        page_data = PageData(
                            page_number=page_num,
                            text=text,
                            width=0.0,
                            height=0.0,
                            text_elements=[]
                        )
                        pages.append(page_data)
        
        return DrawingData(
            file_path=pdf_path,
            pages=pages,
            metadata=metadata,
            extracted_text=extracted_text,
            text_elements=text_elements_dict,
            gemini_ocr_text=gemini_ocr_text if gemini_ocr_text else None,
            gemini_ocr_used=gemini_ocr_used
        )
    
    def extract_text(self, pdf_path: str) -> Dict[int, str]:
        """
        各ページからテキストを抽出
        
        Args:
            pdf_path: PDFファイルのパス
            
        Returns:
            Dict[int, str]: ページ番号 -> テキストの辞書
        """
        drawing_data = self.parse(pdf_path)
        return drawing_data.extracted_text
    
    def get_all_text(self, pdf_path: str) -> str:
        """
        全ページのテキストを結合して返す
        
        Args:
            pdf_path: PDFファイルのパス
            
        Returns:
            str: 全テキスト
        """
        extracted_text = self.extract_text(pdf_path)
        return "\n\n".join([f"--- Page {num} ---\n{text}" 
                           for num, text in sorted(extracted_text.items())])


if __name__ == "__main__":
    # テスト用
    parser = PDFParser()
    # 実際のファイルパスを指定してテスト
    # data = parser.parse("path/to/drawing.pdf")
    # print(data)







