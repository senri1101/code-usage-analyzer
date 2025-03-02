#!/usr/bin/env python3
"""
CodeUsageAnalyzer - コード利用状況分析ツール

このツールは、Pythonコードベース内の関数やメソッドの呼び出し回数を分析し、
リファクタリング候補（プライベートメソッドに変更できそうなメソッド）を特定します。
また、未使用の関数、クラス、変数なども特定します。
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
VariableInfo = namedtuple('VariableInfo', ['name', 'file', 'class_name', 'function_name', 'lineno', 'is_constant'])
ClassInfo = namedtuple('ClassInfo', ['name', 'file', 'lineno'])


class FunctionVisitor(ast.NodeVisitor):
    """関数定義とクラス定義を収集するビジター"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.current_class = None
        self.functions = []
        self.classes = []
        self.variables = []
        self.current_function = None
        
    def visit_ClassDef(self, node):
        # クラス定義を記録
        self.classes.append(ClassInfo(
            name=node.name,
            file=self.filename,
            lineno=node.lineno
        ))
        
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
        
        old_function = self.current_function
        self.current_function = node.name
        # 関数内の全ノードを訪問
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_Assign(self, node):
        # 変数定義を記録
        for target in node.targets:
            if isinstance(target, ast.Name):
                # 定数かどうか判定（大文字の場合は定数と見なす）
                is_constant = target.id.isupper()
                
                self.variables.append(VariableInfo(
                    name=target.id,
                    file=self.filename,
                    class_name=self.current_class,
                    function_name=self.current_function,
                    lineno=node.lineno,
                    is_constant=is_constant
                ))
        
        self.generic_visit(node)
    
    def visit_AnnAssign(self, node):
        # 型アノテーション付きの変数定義
        if isinstance(node.target, ast.Name):
            # 定数かどうか判定（大文字の場合は定数と見なす）
            is_constant = node.target.id.isupper()
            
            self.variables.append(VariableInfo(
                name=node.target.id,
                file=self.filename,
                class_name=self.current_class,
                function_name=self.current_function,
                lineno=node.lineno,
                is_constant=is_constant
            ))
        
        self.generic_visit(node)


class CallVisitor(ast.NodeVisitor):
    """関数呼び出しを収集するビジター"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.current_class = None
        self.current_function = None
        self.calls = []
        self.variable_uses = []
        self.class_uses = set()
        
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
                # クラスが使用されたことを記録
                self.class_uses.add(node.func.value.id)
        
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
    
    def visit_Name(self, node):
        # 変数の使用を記録
        if isinstance(node.ctx, ast.Load):
            self.variable_uses.append((
                node.id,
                self.filename,
                self.current_class,
                self.current_function
            ))
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        # importされたクラスを記録
        for name in node.names:
            self.class_uses.add(name.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        # from import されたクラスを記録
        for name in node.names:
            self.class_uses.add(name.name)
        self.generic_visit(node)


class CodeAnalyzer:
    """コードベース全体を分析するクラス"""
    
    def __init__(self, directory: str, skip_directories: Optional[List[str]] = None):
        self.directory = directory
        self.functions = []  # 関数定義のリスト
        self.calls = []      # 関数呼び出しのリスト
        self.variables = []  # 変数定義のリスト
        self.variable_uses = []  # 変数使用のリスト
        self.classes = []    # クラス定義のリスト
        self.class_uses = set()  # クラス使用のセット
        
        # スキップするディレクトリ（デフォルトの一般的な無視すべきディレクトリ）
        self.skip_directories = set([
            # Python関連
            '.venv', 'venv', 'env', '.env', '.virtualenv', 'virtualenv',
            '__pycache__', '.pytest_cache', '.mypy_cache', '.coverage', 'htmlcov',
            '.tox', '.eggs', '*.egg-info', 'build', 'dist', '.ipynb_checkpoints','layer',
            # JavaScript/Node.js関連
            'node_modules', '.npm', '.yarn', '.pnpm',
            # Java/Maven/Gradle関連
            'target', '.gradle', 'build', '.m2',
            # Git関連
            '.git',
            # 編集者関連
            '.idea', '.vscode', '.vs', '.history',
            # AWS関連
            '.aws-sam', 'cdk.out', '.serverless',
            # その他一般的なバイナリ/依存関係フォルダ
            'bin', 'obj', '.cache', 'vendor', '.bundle',
            # Docker関連
            '.docker',
            # 一時ファイル関連
            'tmp', 'temp', 'logs',
        ])
        
        # 追加のスキップディレクトリがある場合
        if skip_directories:
            self.skip_directories.update(skip_directories)
        
    def analyze(self) -> None:
        """指定されたディレクトリ内のPythonファイルを分析"""
        for root, dirs, files in os.walk(self.directory):
            # スキップすべきディレクトリを除外（dirs内の要素を破壊的に変更）
            dirs_to_remove = []
            for i, d in enumerate(dirs):
                if any(pattern in d or d == pattern for pattern in self.skip_directories):
                    dirs_to_remove.append(i)
            
            # 逆順で削除（インデックスがずれるのを防ぐ）
            for i in reversed(dirs_to_remove):
                print(f"⏩ スキップ: {os.path.join(root, dirs[i])}")
                del dirs[i]
            
            # ファイルの処理
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
        
        # 関数とクラス定義の収集
        function_visitor = FunctionVisitor(filepath)
        function_visitor.visit(tree)
        self.functions.extend(function_visitor.functions)
        self.classes.extend(function_visitor.classes)
        self.variables.extend(function_visitor.variables)
        
        # 関数呼び出しと変数使用の収集
        call_visitor = CallVisitor(filepath)
        call_visitor.visit(tree)
        self.calls.extend(call_visitor.calls)
        self.variable_uses.extend(call_visitor.variable_uses)
        self.class_uses.update(call_visitor.class_uses)
        
        print(f"✓ 解析完了: {filepath} (Python)")
    
    def _analyze_dart_file(self, filepath: str) -> None:
        """Dartファイルを分析 (簡易テキストベース解析)"""
        import re
        print(f"✓ Dartファイルの簡易解析開始: {filepath}")
        # 修正後の正規表現:
        # ・アノテーション、async/static/final のオプショナルな出現
        # ・返り値の型が存在する場合、型にジェネリクスやnull許容記号 (?) を許容
        # ・関数名の後にオプショナルなジェネリックパラメータを許容
        func_pattern = r'(?:@\w+\s+)*(?:\b(?:async|static|final)\b\s+)*(?:(?:\b(?:void|Future(?:<[^>]+>)?(?:\?)?|Widget|String|int|bool|double|dynamic)(?:\?)?)\s+)?(\w+)(?:\s*<[^>]+>)?\s*\('
        call_pattern = r'(\w+)\s*\('
        self._analyze_text_based(filepath, func_pattern, call_pattern)
    
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
        
        # 関数定義を検索 (re.MULTILINEとre.DOTALLのフラグを追加)
        for match in re.finditer(func_pattern, content, flags=re.MULTILINE | re.DOTALL):
            # グループ1から関数名を取得
            func_name = match.group(1)
            if func_name:
                self.functions.append(FunctionInfo(
                    name=func_name,
                    file=filepath,
                    class_name=None,  # テキストベースでは正確なクラスは検出できない
                    lineno=content[:match.start()].count('\n') + 1
                ))
        
        # 関数呼び出しを検索
        for match in re.finditer(call_pattern, content, flags=re.MULTILINE | re.DOTALL):
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
            # 既にプライベートメソッド（名前が "_" で始まる）はスキップ
            if func.name.startswith('_'):
                continue
                
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

    def find_unused_functions(self) -> List[Dict[str, Any]]:
        """未使用の関数・メソッドを特定"""
        call_count = self.get_call_count()
        unused_functions = []
        
        for func in self.functions:
            # テスト関数は除外
            if func.name.startswith('test_') or func.name == 'setUp' or func.name == 'tearDown':
                continue
                
            # main関数は除外
            if func.name == 'main':
                continue
                
            # 特殊メソッドは除外
            if func.name.startswith('__') and func.name.endswith('__'):
                continue
                
            # 関数の一意の識別子
            func_id = (func.file, func.name, func.class_name)
            count = call_count.get(func_id, 0)
            
            # 呼び出し回数が0の場合
            if count == 0:
                unused_functions.append({
                    'type': 'function',
                    'file': func.file,
                    'class': func.class_name,
                    'name': func.name,
                    'line': func.lineno
                })
        
        return unused_functions
        
    def find_unused_classes(self) -> List[Dict[str, Any]]:
        """未使用のクラスを特定"""
        unused_classes = []
        
        for cls in self.classes:
            # 抽象クラスやインターフェースは除外
            if cls.name.startswith('Abstract') or cls.name.endswith('Interface'):
                continue
                
            # テストクラスは除外
            if cls.name.startswith('Test') or cls.name.endswith('Test'):
                continue
                
            # クラスが使用されているかチェック
            if cls.name not in self.class_uses:
                unused_classes.append({
                    'type': 'class',
                    'file': cls.file,
                    'name': cls.name,
                    'line': cls.lineno
                })
        
        return unused_classes
        
    def find_unused_variables(self) -> List[Dict[str, Any]]:
        """未使用の変数や定数を特定"""
        unused_variables = []
        
        for var in self.variables:
            # モジュールレベルまたはクラスレベルの変数のみを対象とする
            if var.function_name is not None:
                continue
                
            # 特殊変数は除外
            if var.name.startswith('__') and var.name.endswith('__'):
                continue
                
            # 変数が使用されているかチェック
            is_used = False
            for use_name, use_file, use_class, use_func in self.variable_uses:
                if var.name == use_name:
                    # 同じファイル内で使用されている
                    if use_file == var.file:
                        is_used = True
                        break
            
            if not is_used:
                unused_variables.append({
                    'type': 'variable',
                    'file': var.file,
                    'class': var.class_name,
                    'name': var.name,
                    'is_constant': var.is_constant,
                    'line': var.lineno
                })
        
        return unused_variables
        
    def find_all_unused_elements(self) -> List[Dict[str, Any]]:
        """全ての未使用要素を特定"""
        unused_elements = []
        
        # 未使用の関数・メソッドを取得
        unused_elements.extend(self.find_unused_functions())
        
        # 未使用のクラスを取得
        unused_elements.extend(self.find_unused_classes())
        
        # 未使用の変数・定数を取得
        unused_elements.extend(self.find_unused_variables())
        
        return unused_elements


def main():
    parser = argparse.ArgumentParser(description='コード利用状況分析ツール')
    parser.add_argument('directory', help='分析するコードのディレクトリパス')
    parser.add_argument('--language', '-l', help='分析する言語 (python, dart, go, js, java, csharp), 未指定の場合は自動検出')
    parser.add_argument('--flutter-project', help='Flutterプロジェクトルートディレクトリ')
    parser.add_argument('--analyze-widgets', action='store_true', help='Flutterウィジェットも分析対象に含める')
    parser.add_argument('--go-module', help='Goモジュールパス（例：github.com/user/project）')
    parser.add_argument('--output', '-o', help='結果を出力するJSONファイル', default='refactoring_candidates.json')
    parser.add_argument('--unused-output', help='未使用要素を出力するJSONファイル', default='unused_elements.json')
    parser.add_argument('--html', '-html', help='HTMLレポートを生成する', action='store_true')
    parser.add_argument('--html-output', help='HTML出力ファイル名', default='code_analysis_report.html')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細な出力を表示')
    parser.add_argument('--skip-dirs', help='スキップするディレクトリ（カンマ区切り）', default='')
    parser.add_argument('--find-unused', '-u', action='store_true', help='未使用の関数、クラス、変数を検出する')
    
    args = parser.parse_args()
    
    # スキップするディレクトリの処理
    skip_dirs = []
    if args.skip_dirs:
        skip_dirs = [d.strip() for d in args.skip_dirs.split(',')]
    
    print(f"🔍 ディレクトリの分析を開始: {args.directory}")
    analyzer = CodeAnalyzer(args.directory, skip_dirs)
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
    
    # 未使用要素の特定と出力
    if args.find_unused:
        unused_elements = analyzer.find_all_unused_elements()
        
        with open(args.unused_output, 'w', encoding='utf-8') as f:
            json.dump(unused_elements, f, indent=2, ensure_ascii=False)
        
        print(f"   - 未使用の要素: {len(unused_elements)}")
        print(f"\n💡 未使用要素リストは {args.unused_output} に保存されました")
    
    print(f"\n💡 プライベートメソッド候補リストは {args.output} に保存されました")
    
    # HTMLレポートの生成
    if args.html:
        try:
            from html_reporter import generate_html_report
            print(f"\n🌐 HTMLレポートを生成しています...")
            generate_html_report(args.output, args.html_output, args.directory)
            print(f"✨ HTMLレポートを生成しました: {args.html_output}")
        except ImportError:
            print(f"\n⚠️ HTMLレポート生成には html_reporter.py が必要です")
            print(f"   スクリプトを同じディレクトリに配置して再実行してください")
    
    if args.verbose and candidates:
        print("\nプライベートメソッド候補:")
        for i, candidate in enumerate(candidates, 1):
            print(f"{i}. {candidate['class']}.{candidate['method']} @ {os.path.basename(candidate['file'])}:{candidate['line']}")
    
    if args.verbose and args.find_unused and unused_elements:
        print("\n未使用の要素:")
        for i, element in enumerate(unused_elements, 1):
            element_type = element['type']
            element_name = element['name']
            file_name = os.path.basename(element['file'])
            line_no = element['line']
            if element_type == 'function':
                class_name = element.get('class', '')
                if class_name:
                    print(f"{i}. [未使用関数] {class_name}.{element_name} @ {file_name}:{line_no}")
                else:
                    print(f"{i}. [未使用関数] {element_name} @ {file_name}:{line_no}")
            elif element_type == 'class':
                print(f"{i}. [未使用クラス] {element_name} @ {file_name}:{line_no}")
            elif element_type == 'variable':
                class_name = element.get('class', '')
                type_str = "定数" if element.get('is_constant', False) else "変数"
                if class_name:
                    print(f"{i}. [未使用{type_str}] {class_name}.{element_name} @ {file_name}:{line_no}")
                else:
                    print(f"{i}. [未使用{type_str}] {element_name} @ {file_name}:{line_no}")


if __name__ == "__main__":
    main()