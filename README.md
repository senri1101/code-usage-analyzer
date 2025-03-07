# CodeUsageAnalyzer

![License](https://img.shields.io/github/license/YourUsername/CodeUsageAnalyzer)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)

コードベース内の関数やメソッドの使用状況を分析し、リファクタリングの候補および未使用要素（関数、クラス、変数、定数等）を特定するツールです。

## 機能

- Pythonコードベース内の関数/メソッド定義の自動検出
- 関数/メソッドの呼び出し回数の追跡
- プライベートメソッドにできる候補の特定（1回だけ呼ばれていて、同じファイル内からの呼び出し）
- 未使用の関数、クラス、変数、定数などの抽出
- 結果のJSON形式およびHTML形式での出力

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/YourUsername/CodeUsageAnalyzer.git
cd CodeUsageAnalyzer

# 仮想環境を作成して有効化
## Pythonの仮想環境（Windowsの場合）
python -m venv venv
venv\Scripts\activate

## Pythonの仮想環境（macOS/Linuxの場合）
python3 -m venv venv
source venv/bin/activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

## 使用方法

### 基本的な使用法

```bash
python code_analyzer.py /path/to/your/code --output refactoring_candidates.json
```

### HTML形式のレポート出力

HTMLレポートには、プライベートメソッド候補に加えて未使用要素（関数、クラス、変数、定数）の情報も表示されます。

```bash
# JSON出力とHTMLレポートの両方を生成
python code_analyzer.py /path/to/your/code --html

# HTMLレポートのファイル名を指定
python code_analyzer.py /path/to/your/code --html --html-output report.html

# HTMLレポーターを直接実行（JSONファイルから）
python html_reporter.py refactoring_candidates.json --output report.html
```

### 未使用要素の抽出

未使用要素の検出機能を有効にするには、`--find-unused`（または `-u`）オプションを使用してください。検出された未使用要素は、指定したJSONファイル（デフォルトは `unused_elements.json`）に保存され、HTMLレポートにも反映されます。

```bash
python code_analyzer.py /path/to/your/code --find-unused
```

### 言語を指定して実行

```bash
# Python特有の解析を実行
python code_analyzer.py /path/to/python/project --language python

# Flutterプロジェクトを解析
python code_analyzer.py /path/to/flutter/project --flutter-project /path/to/flutter/project/root --analyze-widgets

# Goプロジェクトを解析
python code_analyzer.py /path/to/go/project --go-module github.com/username/project
```

### オプション

- `directory`: 分析するコードベースのディレクトリパス（必須）
- `--output`, `-o`: 結果を出力するJSONファイル（デフォルト: `refactoring_candidates.json`）
- `--find-unused`, `-u`: 未使用の関数、クラス、変数、定数を検出する
- `--unused-output`: 未使用要素を出力するJSONファイル（デフォルト: `unused_elements.json`）
- `--html`, `-html`: HTMLレポートを生成する
- `--html-output`: HTML出力ファイル名（デフォルト: `code_analysis_report.html`）
- `--verbose`, `-v`: 詳細な出力を表示

## 出力例

```json
[
  {
    "file": "/path/to/your/code/module.py",
    "class": "MyClass",
    "method": "my_method",
    "line": 42,
    "callers": [
      {
        "file": "/path/to/your/code/module.py",
        "class": "MyClass",
        "function": "another_method"
      }
    ]
  }
]
```

未使用要素の例:

```json
[
  {
    "type": "function",
    "file": "/path/to/your/code/module.py",
    "class": "MyClass",
    "name": "unused_method",
    "line": 88
  },
  {
    "type": "class",
    "file": "/path/to/your/code/another_module.py",
    "name": "UnusedClass",
    "line": 10
  }
]
```

## 対応言語

本ツールは以下の言語に対応しています：

### 完全対応
- Python - ASTを使用した完全な解析

### 簡易対応 (テキストベース解析)
- Dart/Flutter - 関数とメソッド呼び出しの簡易解析
- Go - 関数とメソッド呼び出しの簡易解析
- JavaScript/TypeScript - 関数とメソッド呼び出しの簡易解析

### 今後対応予定
- Java
- C#
- Ruby
- PHP
- Swift
- Rust

それぞれの言語に対する完全な構文解析サポートは、フェーズ別に追加される予定です。

## 貢献

貢献は大歓迎です！以下の方法で参加できます：

1. リポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを開く

## ライセンス

MIT ライセンスの下で配布されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。