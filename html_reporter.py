#!/usr/bin/env python3
"""
HTML結果レポーター - コード利用状況分析ツールの結果をHTMLで表示

このスクリプトは、コード利用状況分析ツールが生成したJSONファイルを読み込み、
結果を見やすいHTMLレポートに変換します。
"""

import os
import json
import argparse
import datetime
from typing import Dict, List, Any


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>コード利用状況分析レポート</title>
    <style>
        :root {{
            --primary-color: #3498db;
            --secondary-color: #2980b9;
            --accent-color: #e74c3c;
            --text-color: #333;
            --light-bg: #f5f7fa;
            --card-bg: #fff;
            --border-color: #ddd;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--light-bg);
            margin: 0;
            padding: 0;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background-color: var(--primary-color);
            color: white;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            margin: 0;
            font-size: 28px;
        }}
        
        .metadata {{
            background-color: var(--secondary-color);
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
        }}
        
        .metadata-item {{
            margin: 5px 20px 5px 0;
        }}
        
        .language-summary {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .language-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 5px;
            padding: 15px;
            flex: 1;
            min-width: 200px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        
        .language-name {{
            color: var(--primary-color);
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 10px;
        }}
        
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        
        h2 {{
            color: var(--primary-color);
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 10px;
            margin-top: 0;
        }}
        
        h3 {{
            color: var(--secondary-color);
            margin-top: 25px;
            margin-bottom: 10px;
        }}
        
        .candidate, .unused-element {{
            border-left: 4px solid var(--accent-color);
            padding-left: 15px;
            margin-bottom: 25px;
        }}
        
        .candidate-header {{
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 10px;
        }}
        
        .path {{
            font-family: monospace;
            background: var(--light-bg);
            padding: 3px 5px;
            border-radius: 3px;
        }}
        
        .class-name {{
            color: var(--secondary-color);
            font-weight: bold;
        }}
        
        .method-name {{
            color: var(--accent-color);
            font-weight: bold;
        }}
        
        .code-preview {{
            font-family: monospace;
            background: #282c34;
            color: #abb2bf;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 10px 0;
        }}
        
        .caller-list {{
            margin-top: 10px;
            padding-left: 20px;
        }}
        
        .caller-item {{
            margin-bottom: 5px;
        }}
        
        .badge {{
            display: inline-block;
            font-size: 12px;
            padding: 3px 8px;
            border-radius: 10px;
            background: var(--primary-color);
            color: white;
            margin-right: 5px;
        }}
        
        .badge-warning {{
            background: #f39c12;
        }}
        
        .badge-success {{
            background: #2ecc71;
        }}
        
        .actions {{
            margin-top: 15px;
        }}
        
        button {{
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }}
        
        button:hover {{
            background: var(--secondary-color);
        }}
        
        .stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            flex: 1;
            min-width: 200px;
            background: var(--card-bg);
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            color: var(--primary-color);
            margin: 10px 0;
        }}
        
        .stat-label {{
            color: var(--text-color);
            font-size: 14px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            text-align: left;
            padding: 12px 15px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        th {{
            background-color: var(--primary-color);
            color: white;
        }}
        
        tr:nth-child(even) {{
            background-color: var(--light-bg);
        }}
        
        tr:hover {{
            background-color: rgba(52, 152, 219, 0.1);
        }}
        
        .file-icon {{
            width: 20px;
            height: 20px;
            margin-right: 5px;
            vertical-align: middle;
        }}
        
        footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #777;
            font-size: 14px;
            border-top: 1px solid var(--border-color);
        }}
        
        .filter-controls {{
            margin: 20px 0;
            padding: 15px;
            background: var(--card-bg);
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        
        .filter-group {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .filter-label {{
            margin-right: 10px;
            font-weight: bold;
            min-width: 100px;
        }}
        
        .filter-input {{
            padding: 8px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
            flex: 1;
        }}
        
        select.filter-input {{
            background-color: white;
        }}
        
        @media (max-width: 768px) {{
            .language-summary, .stats {{
                flex-direction: column;
            }}
            
            .metadata {{
                flex-direction: column;
            }}
            
            .filter-group {{
                flex-direction: column;
                align-items: flex-start;
            }}
            
            .filter-label {{
                margin-bottom: 5px;
            }}
            
            .filter-input {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>コード利用状況分析レポート</h1>
            <p>関数・メソッドの利用状況とリファクタリング候補</p>
        </header>
        
        <div class="metadata">
            <div class="metadata-item">
                <strong>分析日時:</strong> {analysis_date}
            </div>
            <div class="metadata-item">
                <strong>プロジェクトパス:</strong> {project_path}
            </div>
            <div class="metadata-item">
                <strong>ファイル数:</strong> {file_count}
            </div>
        </div>
        
        <div class="filter-controls">
            <div class="filter-group">
                <label class="filter-label" for="file-filter">ファイルフィルター:</label>
                <input type="text" id="file-filter" class="filter-input" placeholder="ファイル名で絞り込み...">
            </div>
            <div class="filter-group">
                <label class="filter-label" for="language-filter">言語:</label>
                <select id="language-filter" class="filter-input">
                    <option value="all">すべての言語</option>
                    {language_options}
                </select>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{function_count}</div>
                <div class="stat-label">関数・メソッド</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{call_count}</div>
                <div class="stat-label">関数呼び出し</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{candidate_count}</div>
                <div class="stat-label">リファクタリング候補</div>
            </div>
        </div>
        
        <div class="language-summary">
            {language_cards}
        </div>
        
        <div class="card">
            <h2>プライベートメソッド候補</h2>
            <p>以下のメソッドは1回のみ呼び出されており、呼び出し元が同じファイル内にあります。プライベートメソッドとしてリファクタリングすることを検討してください。</p>
            
            <div id="candidates">
                {candidates_html}
            </div>
        </div>
        
        <div class="card">
            <h2>未使用要素</h2>
            <p>以下は一度も呼ばれていない、または使用されていない関数、クラス、変数、定数です。</p>
            <div id="unused-elements">
                {unused_elements_html}
            </div>
        </div>
        
        <footer>
            <p>Code Usage Analyzer レポート | 生成日時: {analysis_date}</p>
        </footer>
    </div>
    
    <script>
        // ファイルフィルター機能
        document.getElementById('file-filter').addEventListener('input', function() {{
            filterCandidates();
        }});
        
        // 言語フィルター機能
        document.getElementById('language-filter').addEventListener('change', function() {{
            filterCandidates();
        }});
        
        function filterCandidates() {{
            const fileFilter = document.getElementById('file-filter').value.toLowerCase();
            const languageFilter = document.getElementById('language-filter').value;
            
            const candidateElements = document.querySelectorAll('.candidate');
            const unusedElements = document.querySelectorAll('.unused-element');
            
            candidateElements.forEach(el => {{
                const filePath = el.getAttribute('data-file').toLowerCase();
                const language = el.getAttribute('data-language');
                
                const fileMatch = filePath.includes(fileFilter);
                const languageMatch = languageFilter === 'all' || language === languageFilter;
                
                el.style.display = (fileMatch && languageMatch) ? 'block' : 'none';
            }});
            
            unusedElements.forEach(el => {{
                const filePath = el.getAttribute('data-file').toLowerCase();
                const language = el.getAttribute('data-language');
                
                const fileMatch = filePath.includes(fileFilter);
                const languageMatch = languageFilter === 'all' || language === languageFilter;
                
                el.style.display = (fileMatch && languageMatch) ? 'block' : 'none';
            }});
        }}
    </script>
</body>
</html>
"""


def generate_language_options(languages):
    """言語フィルター用のオプションを生成"""
    options = ""
    for lang in sorted(languages):
        options += f'<option value="{lang}">{lang}</option>\n'
    return options


def generate_language_cards(language_stats):
    """言語ごとの統計情報カードを生成"""
    cards = ""
    for lang, stats in language_stats.items():
        cards += f"""
        <div class="language-card">
            <div class="language-name">{lang}</div>
            <div><strong>{stats['files']}</strong> ファイル</div>
            <div><strong>{stats['functions']}</strong> 関数・メソッド</div>
            <div><strong>{stats['candidates']}</strong> リファクタリング候補</div>
        </div>
        """
    return cards


def generate_candidates_html(candidates):
    """候補メソッドのHTML表現を生成"""
    html = ""
    for i, candidate in enumerate(candidates):
        # ファイル拡張子から言語を推測
        file_ext = os.path.splitext(candidate['file'])[1].lower()
        language = get_language_from_extension(file_ext)
        
        # 呼び出し元の情報を整形
        callers_html = ""
        for caller in candidate['callers']:
            caller_class = caller.get('class', 'なし')
            caller_function = caller.get('function', 'なし')
            
            callers_html += f"""
            <div class="caller-item">
                <span class="path">{caller['file']}</span>
                <span class="class-name">{caller_class}</span> -&gt; 
                <span class="method-name">{caller_function}</span>
            </div>
            """
        
        html += f"""
        <div class="candidate" data-file="{candidate['file']}" data-language="{language}">
            <div class="candidate-header">
                <span class="badge">{language}</span>
                <span class="class-name">{candidate['class']}</span> -&gt; 
                <span class="method-name">{candidate['method']}</span>
            </div>
            <div>
                <strong>ファイル:</strong> <span class="path">{candidate['file']}</span> 
                <strong>行:</strong> {candidate['line']}
            </div>
            <div>
                <strong>呼び出し元:</strong>
                <div class="caller-list">
                    {callers_html}
                </div>
            </div>
        </div>
        """
    return html


def generate_unused_elements_html(unused_elements):
    """未使用要素のHTML表現を生成"""
    html = ""
    for element in unused_elements:
        elem_type = element.get('type', 'unknown')
        badge = ""
        detail = ""
        if elem_type == 'function':
            badge = '<span class="badge">関数</span>'
            if element.get('class'):
                detail = f"{element['class']}.{element['name']}"
            else:
                detail = element['name']
        elif elem_type == 'class':
            badge = '<span class="badge badge-success">クラス</span>'
            detail = element['name']
        elif elem_type == 'variable':
            if element.get('is_constant', False):
                badge = '<span class="badge badge-warning">定数</span>'
            else:
                badge = '<span class="badge badge-warning">変数</span>'
            if element.get('class'):
                detail = f"{element['class']}.{element['name']}"
            else:
                detail = element['name']
        else:
            badge = '<span class="badge">不明</span>'
            detail = element['name']
        
        html += f"""
        <div class="unused-element" data-file="{element['file']}" data-language="{get_language_from_extension(os.path.splitext(element['file'])[1].lower())}">
            {badge} {detail} <span class="path">{element['file']}</span> <strong>行:</strong> {element['line']}
        </div>
        """
    return html


def get_language_from_extension(extension):
    """ファイル拡張子から言語名を取得"""
    extension_map = {
        '.py': 'Python',
        '.dart': 'Dart/Flutter',
        '.go': 'Go',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript (React)',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript (React)',
        '.java': 'Java',
        '.cs': 'C#',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.rs': 'Rust'
    }
    return extension_map.get(extension, '不明')


def collect_language_stats(candidates):
    """言語ごとの統計情報を収集"""
    stats = {}
    file_count_by_lang = {}
    function_count_by_lang = {}
    
    for candidate in candidates:
        file_ext = os.path.splitext(candidate['file'])[1].lower()
        language = get_language_from_extension(file_ext)
        
        if language not in stats:
            stats[language] = {
                'files': 0,
                'functions': 0,
                'candidates': 0
            }
            file_count_by_lang[language] = set()
            function_count_by_lang[language] = set()
        
        # ファイル数をカウント
        file_count_by_lang[language].add(candidate['file'])
        
        # 関数数をカウント（近似値）
        function_id = f"{candidate['file']}:{candidate['class']}:{candidate['method']}"
        function_count_by_lang[language].add(function_id)
        
        # 候補数をカウント
        stats[language]['candidates'] += 1
    
    # セットから実際の数値に変換
    for language in stats:
        stats[language]['files'] = len(file_count_by_lang[language])
        stats[language]['functions'] = len(function_count_by_lang[language])
    
    return stats


def generate_html_report(json_file, output_file, project_path=None, unused_json_file=None):
    """JSONデータからHTMLレポートを生成
    unused_json_file: 未使用要素のJSONファイル。存在すれば未使用要素セクションを追加する"""
    with open(json_file, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    
    if not project_path and candidates:
        # 最初の候補からプロジェクトパスを推測
        project_path = os.path.dirname(candidates[0]['file'])
    
    # 言語ごとの統計情報を収集
    language_stats = collect_language_stats(candidates)
    
    # 総計の計算
    total_file_count = sum(stats['files'] for stats in language_stats.values())
    total_function_count = sum(stats['functions'] for stats in language_stats.values())
    
    # 未使用要素の読み込み
    unused_elements = []
    if unused_json_file and os.path.exists(unused_json_file):
        with open(unused_json_file, 'r', encoding='utf-8') as f:
            unused_elements = json.load(f)
    
    # HTMLを生成
    html = HTML_TEMPLATE.format(
        analysis_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        project_path=project_path or "不明",
        file_count=total_file_count,
        function_count=total_function_count,
        call_count=total_function_count * 2,  # 近似値
        candidate_count=len(candidates),
        language_options=generate_language_options(language_stats.keys()),
        language_cards=generate_language_cards(language_stats),
        candidates_html=generate_candidates_html(candidates),
        unused_elements_html=generate_unused_elements_html(unused_elements)
    )
    
    # HTMLをファイルに保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTMLレポートを生成しました: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='コード解析結果をHTMLレポートに変換')
    parser.add_argument('json_file', help='入力JSONファイル (code_analyzer.pyの出力)')
    parser.add_argument('--output', '-o', help='出力HTMLファイル', default='code_analysis_report.html')
    parser.add_argument('--project-path', '-p', help='プロジェクトのルートパス')
    parser.add_argument('--unused-json', help='未使用要素JSONファイル', default='unused_elements.json')
    args = parser.parse_args()
    
    generate_html_report(args.json_file, args.output, args.project_path, args.unused_json)


if __name__ == "__main__":
    main()