#!/usr/bin/env python3
"""
CodeUsageAnalyzer - コード利用状況分析ツール

このツールは、Pythonコードベース内の関数やメソッドの呼び出し回数を分析し、
リファクタリング候補（プライベートメソッドに変更できそうなメソッド）を特定します。
"""

import os
import ast
import argparse
import json
from collections import defaultdict, namedtuple
from typing import Dict, List, Set, Tuple, Optional, Any


# 解析結果を格納するデータ構造
FunctionInfo = namedtuple('FunctionInfo', ['name', 'file', 'class_name', 'lineno'])
CallInfo = namedtuple('CallInfo', ['name', 'file', 'class_name', 'caller_file', 'caller_class', 'caller_function'])


class FunctionVisitor(ast.NodeVisitor):
    """関数定義とクラス定義を収集するビジター"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.current_class = None
        self.functions = []
        
    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        # クラス内の全ノードを訪問
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_FunctionDef(self, node):
        # 関数定義を記録
        self.functions.append(FunctionInfo(
            name=node.name,
            file=self.filename,
            class_name=self.current_class,
            lineno=node.lineno
        ))
        # 関数内の全ノードを訪問
        self.generic_visit(node)


class CallVisitor(ast.NodeVisitor):
    """関数呼び出しを収集するビジター"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.current_class = None
        self.current_function = None
        self.calls = []
        
    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        # クラス内の全ノードを訪問
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_FunctionDef(self, node):
        old_function = self.current_function
        self.current_function = node.name
        # 関数内の全ノードを訪問
        self.generic_visit(node)
        self.current_function = old_function
        
    def visit_Call(self, node):
        # 関数呼び出しの解析
        func_name = None
        class_name = None
        
        # メソッド呼び出しの場合 (obj.method())
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            func_name = node.func.attr
            # self.method() の場合
            if node.func.value.id == 'self':
                class_name = self.current_class
            # クラスやモジュールからのメソッド呼び出し
            else:
                class_name = node.func.value.id
        
        # 直接的な関数呼び出しの場合 (function())
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
        
        # 呼び出し情報を記録（特定できた場合のみ）
        if func_name:
            self.calls.append(CallInfo(
                name=func_name,
                file=self.filename,
                class_name=class_name,
                caller_file=self.filename,
                caller_class=self.current_class,
                caller_function=self.current_function
            ))
        
        # 呼び出し内の引数なども訪問
        self.generic_visit(node)


class CodeAnalyzer:
    """コードベース全体を分析するクラス"""
    
    def __init__(self, directory: str):
        self.directory = directory
        self.functions = []  # 関数定義のリスト
        self.calls = []      # 関数呼び出しのリスト
        
    def analyze(self) -> None:
        """指定されたディレクトリ内のPythonファイルを分析"""
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    self._analyze_file(filepath)
    
    def _analyze_file(self, filepath: str) -> None:
        """ファイルを分析（ファイル拡張子から言語を自動判定）"""
        try:
            ext = os.path.splitext(filepath)[1].lower()
            
            # Pythonファイル
            if ext == '.py':
                self._analyze_python_file(filepath)
            # Dartファイル
            elif ext == '.dart':
                self._analyze_dart_file(filepath)
            # Goファイル
            elif ext == '.go':
                self._analyze_go_file(filepath)
            # JavaScriptファイル
            elif ext in ['.js', '.jsx', '.ts', '.tsx']:
                self._analyze_js_file(filepath)
            # 他の言語ファイル
            else:
                print(f"! サポートされていない言語: {filepath}")
                
        except Exception as e:
            print(f"! エラー: {filepath} - {str(e)}")
    
    def _analyze_python_file(self, filepath: str) -> None:
        """Pythonファイルを分析"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # ASTの解析
        tree = ast.parse(content, filename=filepath)
        
        # 関数定義の収集
        function_visitor = FunctionVisitor(filepath)
        function_visitor.visit(tree)
        self.functions.extend(function_visitor.functions)
        
        # 関数呼び出しの収集
        call_visitor = CallVisitor(filepath)
        call_visitor.visit(tree)
        self.calls.extend(call_visitor.calls)
        
        print(f"✓ 解析完了: {filepath} (Python)")
    
    def _analyze_dart_file(self, filepath: str) -> None:
        """Dartファイルを分析 (将来的な実装)"""
        # 将来的にはDart用のパーサーを実装
        print(f"! Dart解析はまだ実装されていません: {filepath}")
        # プレースホルダーとして簡易解析（テキストベース）を行う
        self._analyze_text_based(filepath, r'(?:void|Future|Widget|String|int|bool|double|dynamic|var)\s+(\w+)\s*\(', r'(?:\w+)\.(\w+)\s*\(')
    
    def _analyze_go_file(self, filepath: str) -> None:
        """Goファイルを分析 (将来的な実装)"""
        # 将来的にはGo用のパーサーを実装
        print(f"! Go解析はまだ実装されていません: {filepath}")
        # プレースホルダーとして簡易解析（テキストベース）を行う
        self._analyze_text_based(filepath, r'func\s+(?:\([\w\s*]+\)\s+)?(\w+)\s*\(', r'(?:\w+)\.(\w+)\s*\(')
    
    def _analyze_js_file(self, filepath: str) -> None:
        """JavaScriptファイルを分析 (将来的な実装)"""
        # 将来的にはJavaScript用のパーサーを実装
        print(f"! JavaScript解析はまだ実装されていません: {filepath}")
        # プレースホルダーとして簡易解析（テキストベース）を行う
        self._analyze_text_based(filepath, r'(?:function|const|let|var)\s+(\w+)\s*\(|(\w+)\s*:\s*function', r'(?:\w+)\.(\w+)\s*\(')
    
    def _analyze_text_based(self, filepath: str, func_pattern: str, call_pattern: str) -> None:
        """簡易的なテキストベース解析（正規表現を使用）"""
        import re
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 関数定義を検索
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1) if match.group(1) else match.group(2)
            if func_name:
                self.functions.append(FunctionInfo(
                    name=func_name,
                    file=filepath,
                    class_name=None,  # テキストベースでは正確なクラスは検出できない
                    lineno=content[:match.start()].count('\n') + 1
                ))
        
        # 関数呼び出しを検索
        for match in re.finditer(call_pattern, content):
            call_name = match.group(1)
            if call_name:
                self.calls.append(CallInfo(
                    name=call_name,
                    file=filepath,
                    class_name=None,
                    caller_file=filepath,
                    caller_class=None,
                    caller_function=None
                ))
        
        print(f"✓ 簡易解析完了: {filepath} (テキストベース)")
    
    def get_call_count(self) -> Dict[Tuple[str, str, Optional[str]], int]:
        """各関数の呼び出し回数を計算"""
        call_count = defaultdict(int)
        
        for call in self.calls:
            # 関数の一意の識別子 (ファイル名, 関数名, クラス名)
            func_id = (call.file, call.name, call.class_name)
            call_count[func_id] += 1
        
        return call_count
    
    def find_private_candidates(self) -> List[Dict[str, Any]]:
        """プライベートメソッドの候補を特定"""
        call_count = self.get_call_count()
        candidates = []
        
        for func in self.functions:
            # 関数の一意の識別子
            func_id = (func.file, func.name, func.class_name)
            count = call_count.get(func_id, 0)
            
            # 呼び出し元を取得
            callers = set()
            for call in self.calls:
                if (call.file, call.name, call.class_name) == func_id:
                    callers.add((call.caller_file, call.caller_class, call.caller_function))
            
            # 呼び出し回数が1回のみ、かつ同じファイルからの呼び出しの場合
            if count == 1 and all(caller[0] == func.file for caller in callers):
                # クラスメソッドの場合のみを対象
                if func.class_name:
                    candidates.append({
                        'file': func.file,
                        'class': func.class_name,
                        'method': func.name,
                        'line': func.lineno,
                        'callers': [{'file': f, 'class': c, 'function': fn} for f, c, fn in callers]
                    })
        
        return candidates


def main():
    parser = argparse.ArgumentParser(description='コード利用状況分析ツール')
    parser.add_argument('directory', help='分析するコードのディレクトリパス')
    parser.add_argument('--language', '-l', help='分析する言語 (python, dart, go, js, java, csharp), 未指定の場合は自動検出')
    parser.add_argument('--flutter-project', help='Flutterプロジェクトルートディレクトリ')
    parser.add_argument('--analyze-widgets', action='store_true', help='Flutterウィジェットも分析対象に含める')
    parser.add_argument('--go-module', help='Goモジュールパス（例：github.com/user/project）')
    parser.add_argument('--output', '-o', help='結果を出力するJSONファイル', default='refactoring_candidates.json')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細な出力を表示')
    
    args = parser.parse_args()
    
    print(f"🔍 ディレクトリの分析を開始: {args.directory}")
    analyzer = CodeAnalyzer(args.directory)
    analyzer.analyze()
    
    # プライベートメソッド候補の特定
    candidates = analyzer.find_private_candidates()
    
    # 結果の出力
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 分析完了!")
    print(f"📊 分析結果:")
    print(f"   - 検出された関数/メソッド: {len(analyzer.functions)}")
    print(f"   - 検出された関数呼び出し: {len(analyzer.calls)}")
    print(f"   - プライベートメソッド候補: {len(candidates)}")
    print(f"\n💡 プライベートメソッド候補リストは {args.output} に保存されました")
    
    if args.verbose and candidates:
        print("\nプライベートメソッド候補:")
        for i, candidate in enumerate(candidates, 1):
            print(f"{i}. {candidate['class']}.{candidate['method']} @ {os.path.basename(candidate['file'])}:{candidate['line']}")


if __name__ == "__main__":
    main()