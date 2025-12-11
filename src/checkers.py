"""
Check Engine Modules
各種チェック機能を実装
"""

import re
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .pdf_parser import DrawingData


class CheckStatus(Enum):
    """チェック結果のステータス"""
    OK = "OK"
    NG = "NG"
    WARNING = "WARNING"


class Importance(Enum):
    """重要度"""
    REQUIRED = "必須"
    RECOMMENDED = "推奨"
    REFERENCE = "参考"


@dataclass
class CheckResult:
    """チェック結果"""
    category: str  # "必須記載事項", "創建特有項目"など
    item: str  # チェック項目名
    status: CheckStatus  # チェック結果
    message: str  # 指摘内容
    importance: Importance  # 重要度
    location: Optional[Tuple[float, float]] = None  # 図面上の位置
    page_number: Optional[int] = None  # 該当ページ
    suggestion: Optional[str] = None  # 修正提案


class RequiredItemsChecker:
    """必須記載事項チェッカー"""
    
    def __init__(self):
        self.category = "必須記載事項"
    
    def check(self, drawing_data: DrawingData) -> List[CheckResult]:
        """
        必須記載事項をチェック
        
        Args:
            drawing_data: 図面データ
            
        Returns:
            List[CheckResult]: チェック結果のリスト
        """
        results = []
        all_text = self._get_all_text(drawing_data)
        
        # 図面番号チェック
        if not self._has_drawing_number(all_text):
            results.append(CheckResult(
                category=self.category,
                item="図面番号",
                status=CheckStatus.NG,
                message="図面番号が記載されていません",
                importance=Importance.REQUIRED,
                suggestion="図面番号を明記してください（例: A-001, S-001）"
            ))
        
        # 図面名チェック
        if not self._has_drawing_name(all_text):
            results.append(CheckResult(
                category=self.category,
                item="図面名",
                status=CheckStatus.NG,
                message="図面名が記載されていません",
                importance=Importance.REQUIRED,
                suggestion="図面名を明記してください（例: 1階平面図、立面図）"
            ))
        
        # 縮尺チェック
        scale = self._extract_scale(all_text)
        if not scale:
            results.append(CheckResult(
                category=self.category,
                item="縮尺",
                status=CheckStatus.NG,
                message="縮尺が記載されていません",
                importance=Importance.REQUIRED,
                suggestion="縮尺を明記してください（例: 1/100, 1/50）"
            ))
        
        # 作成日チェック
        if not self._has_creation_date(all_text):
            results.append(CheckResult(
                category=self.category,
                item="作成日",
                status=CheckStatus.WARNING,
                message="作成日が明示されていない可能性があります",
                importance=Importance.RECOMMENDED,
                suggestion="作成日を明記してください"
            ))
        
        # 作成者チェック
        if not self._has_creator(all_text):
            results.append(CheckResult(
                category=self.category,
                item="作成者",
                status=CheckStatus.WARNING,
                message="作成者が明示されていない可能性があります",
                importance=Importance.RECOMMENDED,
                suggestion="作成者名を明記してください"
            ))
        
        return results
    
    def _get_all_text(self, drawing_data: DrawingData) -> str:
        """全ページのテキストを結合"""
        return "\n".join(drawing_data.extracted_text.values())
    
    def _has_drawing_number(self, text: str) -> bool:
        """図面番号の存在チェック"""
        patterns = [
            r'図面番号[:：]\s*[A-Z0-9\-]+',
            r'図番[:：]\s*[A-Z0-9\-]+',
            r'DWG\s*NO[:：]\s*[A-Z0-9\-]+',
            r'[A-Z]\-\d{3,}',  # A-001形式
            r'S\-\d{3,}',  # S-001形式
        ]
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _has_drawing_name(self, text: str) -> bool:
        """図面名の存在チェック"""
        patterns = [
            r'図面名[:：]',
            r'平面図',
            r'立面図',
            r'断面図',
            r'詳細図',
            r'配置図',
        ]
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _extract_scale(self, text: str) -> Optional[str]:
        """縮尺を抽出"""
        patterns = [
            r'縮尺[:：]\s*1[/／]\d+',
            r'SCALE[:：]\s*1[/／]\d+',
            r'1[/／]\d+',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    def _has_creation_date(self, text: str) -> bool:
        """作成日の存在チェック"""
        patterns = [
            r'作成日[:：]\s*\d{4}[/年]\d{1,2}[/月]\d{1,2}[日]?',
            r'作成日[:：]\s*\d{4}[-/]\d{1,2}[-/]\d{1,2}',
            r'DATE[:：]\s*\d{4}[-/]\d{1,2}[-/]\d{1,2}',
        ]
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _has_creator(self, text: str) -> bool:
        """作成者の存在チェック"""
        patterns = [
            r'作成者[:：]',
            r'作成[:：]',
            r'設計者[:：]',
            r'DRAWN\s*BY[:：]',
        ]
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False


class SoukenSpecificChecker:
    """創建特有項目チェッカー"""
    
    def __init__(self):
        self.category = "創建特有項目"
    
    def check(self, drawing_data: DrawingData) -> List[CheckResult]:
        """
        創建特有項目をチェック
        
        Args:
            drawing_data: 図面データ
            
        Returns:
            List[CheckResult]: チェック結果のリスト
        """
        results = []
        all_text = self._get_all_text(drawing_data)
        
        # 外断熱チェック
        if not self._has_external_insulation_spec(all_text):
            results.append(CheckResult(
                category=self.category,
                item="外断熱仕様",
                status=CheckStatus.NG,
                message="外断熱仕様が記載されていません",
                importance=Importance.REQUIRED,
                suggestion="創建基準: 外断熱仕様を明記してください"
            ))
        
        # 第一種換気システムチェック
        if not self._has_first_class_ventilation(all_text):
            results.append(CheckResult(
                category=self.category,
                item="第一種換気システム",
                status=CheckStatus.NG,
                message="第一種換気システムの記載がありません",
                importance=Importance.REQUIRED,
                suggestion="創建基準: 第一種換気システムの仕様を明記してください"
            ))
        
        # 釘ピッチチェック
        nail_pitch = self._extract_nail_pitch(all_text)
        if nail_pitch:
            if nail_pitch > 150:
                results.append(CheckResult(
                    category=self.category,
                    item="釘ピッチ",
                    status=CheckStatus.NG,
                    message=f"釘ピッチが{nail_pitch}mmです。創建基準は150mm以下です。",
                    importance=Importance.REQUIRED,
                    suggestion="創建基準: 釘ピッチを150mm以下に修正してください"
                ))
        else:
            results.append(CheckResult(
                category=self.category,
                item="釘ピッチ",
                status=CheckStatus.WARNING,
                message="釘ピッチの記載が見つかりません",
                importance=Importance.RECOMMENDED,
                suggestion="創建基準: 釘ピッチを明記してください（基準: 150mm以下）"
            ))
        
        # 隠蔽部分の施工方法チェック
        if not self._has_hidden_part_construction_method(all_text):
            results.append(CheckResult(
                category=self.category,
                item="隠蔽部分の施工方法",
                status=CheckStatus.WARNING,
                message="隠蔽部分の施工方法が明記されていない可能性があります",
                importance=Importance.RECOMMENDED,
                suggestion="創建基準: 隠蔽部分の施工方法を明記し、写真記録を指示してください"
            ))
        
        return results
    
    def _get_all_text(self, drawing_data: DrawingData) -> str:
        """全ページのテキストを結合"""
        return "\n".join(drawing_data.extracted_text.values())
    
    def _has_external_insulation_spec(self, text: str) -> bool:
        """外断熱仕様の存在チェック"""
        patterns = [
            r'外断熱',
            r'外部断熱',
            r'外側断熱',
            r'EXTERNAL\s*INSULATION',
        ]
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _has_first_class_ventilation(self, text: str) -> bool:
        """第一種換気システムの存在チェック"""
        patterns = [
            r'第一種換気',
            r'1種換気',
            r'第一種',
            r'1ST\s*CLASS\s*VENTILATION',
        ]
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_nail_pitch(self, text: str) -> Optional[int]:
        """釘ピッチを抽出"""
        patterns = [
            r'釘ピッチ[:：]\s*(\d+)\s*mm',
            r'釘間隔[:：]\s*(\d+)\s*mm',
            r'NAIL\s*PITCH[:：]\s*(\d+)\s*mm',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        return None
    
    def _has_hidden_part_construction_method(self, text: str) -> bool:
        """隠蔽部分の施工方法の存在チェック"""
        patterns = [
            r'隠蔽',
            r'写真記録',
            r'写真撮影',
            r'HIDDEN\s*PART',
        ]
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


class CheckEngine:
    """チェックエンジン（統合）"""
    
    def __init__(self):
        self.required_checker = RequiredItemsChecker()
        self.souken_checker = SoukenSpecificChecker()
    
    def check_all(self, drawing_data: DrawingData) -> List[CheckResult]:
        """
        すべてのチェックを実行
        
        Args:
            drawing_data: 図面データ
            
        Returns:
            List[CheckResult]: すべてのチェック結果
        """
        results = []
        
        # 必須記載事項チェック
        results.extend(self.required_checker.check(drawing_data))
        
        # 創建特有項目チェック
        results.extend(self.souken_checker.check(drawing_data))
        
        return results
    
    def get_summary(self, results: List[CheckResult]) -> dict:
        """
        チェック結果のサマリーを取得
        
        Args:
            results: チェック結果のリスト
            
        Returns:
            dict: サマリー情報
        """
        total = len(results)
        ok_count = sum(1 for r in results if r.status == CheckStatus.OK)
        ng_count = sum(1 for r in results if r.status == CheckStatus.NG)
        warning_count = sum(1 for r in results if r.status == CheckStatus.WARNING)
        
        required_ng = sum(1 for r in results 
                         if r.status == CheckStatus.NG and r.importance == Importance.REQUIRED)
        
        return {
            'total': total,
            'ok': ok_count,
            'ng': ng_count,
            'warning': warning_count,
            'required_ng': required_ng,
            'status': 'PASS' if required_ng == 0 else 'FAIL'
        }

