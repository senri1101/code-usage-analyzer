# コード解析ツールの拡張計画

## 他言語対応のアーキテクチャ

コード解析ツールを他のプログラミング言語に対応させるために、以下のようなプラグイン型アーキテクチャを採用します。

```
code_analyzer/
├── core/
│   ├── __init__.py
│   ├── analyzer.py      # 言語に依存しない基本機能
│   └── utils.py         # ユーティリティ関数
├── languages/
│   ├── __init__.py
│   ├── python/          # Python言語対応
│   │   ├── __init__.py
│   │   ├── parser.py    # Pythonコードのパーサー
│   │   └── visitor.py   # AST訪問処理
│   ├── javascript/      # JavaScript言語対応
│   │   ├── __init__.py
│   │   ├── parser.py    # JavaScriptコードのパーサー
│   │   └── visitor.js   # AST訪問処理
│   ├── java/            # Java言語対応
│   │   └── ...
│   └── ...
└── main.py              # メインスクリプト
```

## 言語別対応計画

### 1. Flutter/Dart対応

Flutterのプロジェクト分析には、以下の方法を採用します：

- `analyzer` - Dartの静的解析ツール

```dart
// 実装イメージ (dart/parser.dart)
import 'package:analyzer/dart/analysis/features.dart';
import 'package:analyzer/dart/analysis/utilities.dart';
import 'package:analyzer/dart/ast/ast.dart';

class DartParser {
  Future<CompilationUnit> parseFile(String filePath) async {
    final result = parseFile(
      path: filePath,
      featureSet: FeatureSet.latestLanguageVersion(),
    );
    return result.unit;
  }
  
  List<MethodDeclaration> findMethods(CompilationUnit unit) {
    final methods = <MethodDeclaration>[];
    unit.visitChildren(
      AstVisitor(
        methodDeclaration: (node) {
          methods.add(node);
          return true;
        },
      ),
    );
    return methods;
  }
  
  List<MethodInvocation> findCalls(CompilationUnit unit) {
    final calls = <MethodInvocation>[];
    unit.visitChildren(
      AstVisitor(
        methodInvocation: (node) {
          calls.add(node);
          return true;
        },
      ),
    );
    return calls;
  }
}
```

FlutterプロジェクトのためのCLIオプション:
```
--flutter-project=/path/to/flutter/project
--analyze-widgets=true  # Widgetクラスも分析対象に含める
```

### 2. Go言語対応

Goコードの解析には、以下のライブラリを使用します：

- `go/ast` - Go言語標準ライブラリのASTパーサー

```go
// 実装イメージ (goparser/parser.go)
package goparser

import (
	"go/ast"
	"go/parser"
	"go/token"
)

// ParseFile parses a Go source file
func ParseFile(filePath string) (*ast.File, error) {
	fset := token.NewFileSet()
	return parser.ParseFile(fset, filePath, nil, parser.ParseComments)
}

// FindFunctions finds all function declarations
func FindFunctions(file *ast.File) []*ast.FuncDecl {
	var functions []*ast.FuncDecl
	
	ast.Inspect(file, func(n ast.Node) bool {
		if fn, ok := n.(*ast.FuncDecl); ok {
			functions = append(functions, fn)
		}
		return true
	})
	
	return functions
}

// FindCalls finds all function calls
func FindCalls(file *ast.File) []*ast.CallExpr {
	var calls []*ast.CallExpr
	
	ast.Inspect(file, func(n ast.Node) bool {
		if call, ok := n.(*ast.CallExpr); ok {
			calls = append(calls, call)
		}
		return true
	})
	
	return calls
}
```

Pythonからの呼び出し方：
```python
# Go用のラッパー
import subprocess
import json

def parse_go_file(file_path):
    """Goコードを解析するためのプロセスを呼び出す"""
    result = subprocess.run(
        ["go", "run", "goparser/cmd/main.go", "--file", file_path],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)
```

### 3. JavaScript/TypeScript対応

JavaScript/TypeScriptの解析には、以下のライブラリを使用します：

- `esprima` - JavaScriptのパーサー
- `typescript` - TypeScriptのパーサー

```javascript
// 実装イメージ (javascript/parser.js)
const esprima = require('esprima');
const fs = require('fs');

function parseFile(filePath) {
  const code = fs.readFileSync(filePath, 'utf8');
  return esprima.parseScript(code, { loc: true });
}

function findFunctions(ast) {
  // 関数定義を抽出
  // ...
}

function findCalls(ast) {
  // 関数呼び出しを抽出
  // ...
}
```

### 2. Java対応

Javaコードの解析には、以下のライブラリを使用します：

- `javaparser` - Javaコードのパース用

```java
// 実装イメージ (JavaParser.java)
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;

public class JavaParser {
    public static CompilationUnit parseFile(String filePath) {
        return StaticJavaParser.parse(new File(filePath));
    }
    
    public static List<MethodInfo> findMethods(CompilationUnit cu) {
        // メソッド定義を抽出
        // ...
    }
    
    public static List<CallInfo> findCalls(CompilationUnit cu) {
        // メソッド呼び出しを抽出
        // ...
    }
}
```

### 3. C#対応

C#コードの解析には、Roslyn（.NET Compiler Platform）を使用します：

```csharp
// 実装イメージ (CSharpParser.cs)
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

public class CSharpParser
{
    public static SyntaxTree ParseFile(string filePath)
    {
        string code = File.ReadAllText(filePath);
        return CSharpSyntaxTree.ParseText(code);
    }
    
    public static List<MethodInfo> FindMethods(SyntaxTree tree)
    {
        // メソッド定義を抽出
        // ...
    }
    
    public static List<CallInfo> FindCalls(SyntaxTree tree)
    {
        // メソッド呼び出しを抽出
        // ...
    }
}
```

## 言語検出と自動対応

複数の言語が混在するプロジェクトに対応するため、ファイル拡張子に基づいて適切な言語パーサーを選択する機能を実装します：

```python
def get_language_parser(file_path):
    """ファイル拡張子から適切な言語パーサーを選択"""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.py']:
        return PythonParser()
    elif ext in ['.js', '.jsx', '.ts', '.tsx']:
        return JavaScriptParser()
    elif ext in ['.java']:
        return JavaParser()
    elif ext in ['.cs']:
        return CSharpParser()
    # その他の言語...
    else:
        return None  # 未対応の言語
```

## プラグイン型拡張の仕組み

新しい言語に対応するプラグインを簡単に追加できるようにするための仕組みを実装します：

1. 言語パーサープラグインのインターフェース定義
2. プラグイン自動検出と読み込み機能
3. 言語固有の設定オプション

```python
class LanguageParserInterface:
    """言語パーサーのインターフェース"""
    
    def can_parse(self, file_path):
        """このパーサーでファイルを解析できるか判定"""
        pass
    
    def parse_file(self, file_path):
        """ファイルを解析してASTを返す"""
        pass
    
    def find_functions(self, ast):
        """関数定義を抽出"""
        pass
    
    def find_calls(self, ast):
        """関数呼び出しを抽出"""
        pass
```

## 今後のロードマップ

1. **第1フェーズ: Python対応の安定化**
   - 既存のPython解析機能のバグ修正と改善
   - テストカバレッジの拡大

2. **第2フェーズ: Flutter/Dart対応**
   - Dartパーサーの実装
   - Flutterウィジェット固有の解析
   - パッケージ依存関係の解析

3. **第3フェーズ: Go言語対応**
   - Goパーサーの実装
   - Goモジュールとパッケージ解析
   - インターフェース実装状況の検出

4. **第4フェーズ: JavaScript/TypeScript対応**
   - JavaScriptパーサーの実装
   - TypeScriptパーサーの実装
   - エコシステム固有の解析（React, Node.js等）

5. **第5フェーズ: Java対応**
   - Javaパーサーの実装
   - Spring, Androidなどのフレームワーク対応

6. **第6フェーズ: C#対応**
   - C#パーサーの実装
   - .NETフレームワーク対応

7. **第7フェーズ: その他言語対応**
   - Ruby, Rust, PHP, Swiftなどへの対応
   - コミュニティからの貢献受付

6. **継続的改善**
   - パフォーマンス最適化
   - UI/CLIの使いやすさ向上
   - データ可視化機能の追加

## 貢献のためのガイドライン

新しい言語パーサーを実装する際のガイドラインを整備し、オープンソースコミュニティからの貢献を促進します。