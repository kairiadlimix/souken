"""
PDF Parser Module
図面PDFを読み込み、テキストやメタデータを抽出する
"""

import PyPDF2
import pdfplumber
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PageData:
    """1ページ分のデータ"""
    page_number: int
    text: str
    width: float
    height: float


@dataclass
class DrawingData:
    """図面データ"""
    file_path: str
    pages: List[PageData]
    metadata: Dict[str, any]
    extracted_text: Dict[int, str]  # page_num -> text


class PDFParser:
    """PDF解析クラス"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
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
        
        # pdfplumberでテキスト抽出（より精度が高い）
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    extracted_text[page_num] = text
                    
                    page_data = PageData(
                        page_number=page_num,
                        text=text,
                        width=page.width,
                        height=page.height
                    )
                    pages.append(page_data)
        except Exception as e:
            print(f"テキスト抽出エラー: {e}")
            # フォールバック: PyPDF2を使用
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    text = page.extract_text() or ""
                    extracted_text[page_num] = text
                    
                    page_data = PageData(
                        page_number=page_num,
                        text=text,
                        width=0.0,
                        height=0.0
                    )
                    pages.append(page_data)
        
        return DrawingData(
            file_path=pdf_path,
            pages=pages,
            metadata=metadata,
            extracted_text=extracted_text
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

