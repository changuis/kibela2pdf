# Kibela to PDF コンバーター

このツールはKibelaのページからコンテンツを抜き出して、特定のフォーマット要件でPDFファイルを作るんやで。

## 機能

- Kibela APIを使ってKibelaページからコンテンツを抜き出すで
- メタデータ、日付、いらん要素なしのきれいなPDFファイルを生成するわ
- 枠線と太字ヘッダー付きのテーブルフォーマットを保持するで
- 適切な見出し階層（H1、H2、H3、H4）を維持するんや
- **✅ クリック可能なリンク** - リンクが青い下線付きテキストで表示されて、クリックしたらURLが開くで
- **✅ 画像サポート** - ローカルのPNGファイル（1.png、2.png、3.png）が利用可能やったら自動で使うで
- **✅ コードブロック** - グレー背景と枠線付きの等幅フォーマットやで
- **✅ 番号付きリスト** - 適切な連番（1.、2.、3.、など）やで
- フォルダ情報、目次、コメントは除外するで
- フッターにページ数や一時ファイルパスは入れへんで
- 日本語フォントサポートで適切にレンダリングするわ

## 利用可能なバージョン

### 1. WeasyPrintバージョン（`kibela_to_pdf.py`）
高度なCSSサポート付きのHTML-to-PDF変換にWeasyPrintを使うで。

### 2. ReportLabバージョン（`kibela_to_pdf_alternative.py`）- **macOS推奨やで**
ReportLabを使ったPDF生成で、macOSシステムでより信頼性が高くて拡張機能付きや：
- **テーブルと段落でのクリック可能なリンク**
- **ローカル画像埋め込み**（1.png、2.png、3.pngファイルを自動使用）
- **拡張コードブロックフォーマット**
- **より良い日本語フォントサポート**

## クイックセットアップ

自動インストール用のセットアップスクリプトを実行するで：
```bash
./setup.sh
```

これで以下のことをやってくれるわ：
- Python依存関係をインストール
- スクリプトを実行可能にする
- 環境変数をチェック

## 手動前提条件

1. **環境変数**：`.zshrc`に以下の環境変数を設定しといてや：
   ```bash
   export KIBELA_TOKEN=your_kibela_api_token
   export KIBELA_TEAM=your_team_name
   ```

2. **Python依存関係**： 
   
   **WeasyPrintバージョン用：**
   ```bash
   pip3 install -r requirements.txt
   # macOSでは追加のシステムライブラリが必要かもしれへんで：
   brew install pango gdk-pixbuf libffi gobject-introspection
   ```
   
   **ReportLabバージョン用（推奨）：**
   ```bash
   pip3 install -r requirements_alternative.txt
   ```

## 使い方

### シンプルなラッパースクリプト（一番簡単やで）
```bash
# 基本的な使い方
./kibela2pdf "https://your-team.kibe.la/notes/12345"

# 出力ファイルを指定
./kibela2pdf "https://your-team.kibe.la/notes/12345" -o "my-document.pdf"
```

### ReportLabバージョン（推奨やで）
```bash
# 基本的な使い方
python3 kibela_to_pdf_alternative.py "https://your-team.kibe.la/notes/12345"

# 出力ファイルを指定
python3 kibela_to_pdf_alternative.py "https://your-team.kibe.la/notes/12345" -o "my-document.pdf"
```

### WeasyPrintバージョン
```bash
# 基本的な使い方
python3 kibela_to_pdf.py "https://your-team.kibe.la/notes/12345"

# 出力ファイルを指定
python3 kibela_to_pdf.py "https://your-team.kibe.la/notes/12345" -o "my-document.pdf"
```

### スクリプトを実行可能にする（オプション）
```bash
chmod +x kibela_to_pdf_alternative.py
./kibela_to_pdf_alternative.py "https://your-team.kibe.la/notes/12345"
```

## 画像サポート

ReportLabバージョンは利用可能やったらローカルPNGファイルを自動で埋め込むで：

1. **画像をスクリプトと同じディレクトリに置く**
2. **連番で名前を付ける**：`1.png`、`2.png`、`3.png`など
3. **コンバーターを実行**すると、これらの画像を順番に自動で使うで

```bash
# ディレクトリ構造の例：
kibela2pdf/
├── 1.png          # ドキュメントの最初の画像
├── 2.png          # ドキュメントの2番目の画像
├── 3.png          # ドキュメントの3番目の画像
└── kibela_to_pdf_alternative.py

# コンバーターを実行
./kibela2pdf "https://your-team.kibe.la/notes/12345"
```

スクリプトは以下のことをやってくれるで：
- ✅ HTMLで見つかった最初の画像に`1.png`を使う
- ✅ HTMLで見つかった2番目の画像に`2.png`を使う
- ✅ PDFページ幅に合うように画像をスケール（最大400ポイント）
- ✅ 高品質画像をPDFに埋め込む

## コマンドラインオプション

- `url`：KibelaページURL（必須）
- `-o, --output`：出力PDFファイルパス（オプション、デフォルトはサニタイズされたページタイトル）

## 例

```bash
# 自動生成ファイル名でKibelaページをPDFに変換（ReportLab）
python3 kibela_to_pdf_alternative.py "https://spikestudio.kibe.la/notes/12345"

# カスタム出力ファイル名で変換（ReportLab）
python3 kibela_to_pdf_alternative.py "https://spikestudio.kibe.la/notes/12345" -o "project-documentation.pdf"

# WeasyPrintバージョンを使用
python3 kibela_to_pdf.py "https://spikestudio.kibe.la/notes/12345" -o "project-documentation.pdf"

# ローカル画像付き（ReportLabバージョン）
# 1. 1.png、2.png、3.pngをディレクトリに置く
# 2. コンバーターを実行
./kibela2pdf "https://spikestudio.kibe.la/notes/12345" -o "document-with-images.pdf"
```

## 出力フォーマット

生成されるPDFには以下が含まれるで：
- ✅ H1見出しとしてのページタイトル
- ✅ 適切な見出し階層（H1、H2、H3、H4）
- ✅ 枠線と太字ヘッダー付きテーブル
- ✅ **クリック可能なリンク**（URLを開く青い下線付きテキスト）
- ✅ **実際の画像**（利用可能な場合はローカルPNGファイルから）
- ✅ **コードブロック**（等幅フォーマットとグレー背景付き）
- ✅ **番号付きリスト**（適切な連番付き）
- ✅ メタデータなしのクリーンなコンテンツ
- ✅ 日本語フォントサポート
- ❌ 日付やタイムスタンプなし
- ❌ フォルダ情報なし
- ❌ 目次なし
- ❌ コメントなし
- ❌ フッターにページ番号なし
- ❌ 一時ファイルパスなし

## リンク機能

ReportLabバージョンは完全なクリック可能リンクサポートを提供するで：

- **青い下線付きテキスト** - リンクが従来のWebリンクのように表示される
- **クリック可能機能** - クリックしてブラウザでURLを開く
- **テーブルサポート** - テーブルセル内のリンクも完全に機能する
- **クリーンな外観** - ドキュメントを散らかす可視URLなし
- **クロスプラットフォーム** - すべてのPDFビューアで動作

## トラブルシューティング

1. **API認証エラー**：`KIBELA_TOKEN`と`KIBELA_TEAM`環境変数が正しく設定されてることを確認してや。

2. **ノートが見つからへん**：KibelaのURLが正しくて、そのノートにアクセス権があることを確認してや。

3. **PDF生成エラー**：すべての依存関係、特にWeasyPrintが正しくインストールされてることを確認してや。

4. **フォントの問題**：スクリプトは日本語対応フォントを使うで。フォントレンダリングの問題が発生したら、システムに必要なフォントがインストールされてることを確認してや。

5. **画像の問題**： 
   - PNGファイルが正しく名前付けされてることを確認（1.png、2.png、3.png）
   - 画像をスクリプトと同じディレクトリに置く
   - 画像がPNG形式であることを確認

6. **リンクの問題**： 
   - リンクはReportLabバージョンでのみクリック可能
   - リンク注釈をサポートするPDFビューアを使ってることを確認

## 依存関係

### ReportLabバージョン（推奨）
- `requests`：KibelaへのAPI呼び出し用
- `beautifulsoup4`：HTMLパースとクリーニング用
- `reportlab`：高度な機能付きPDF生成用
- `pillow`：画像処理用
- `html2text`：テキスト処理用

### WeasyPrintバージョン
- `requests`：KibelaへのAPI呼び出し用
- `beautifulsoup4`：HTMLパースとクリーニング用
- `weasyprint`：PDF生成用
- `html2text`：テキスト処理用
- `lxml`：XML/HTMLパース用

## バージョン履歴

### 最新バージョン（ReportLab）
- ✅ クリック可能リンクサポートを追加
- ✅ ローカル画像埋め込み（1.png、2.png、3.png）を追加
- ✅ 拡張コードブロックフォーマット
- ✅ 改良されたテーブルスタイリング
- ✅ より良い日本語フォントサポート
- ✅ 完全なインタラクティビティ付きプロフェッショナルPDF出力

### 以前のバージョン（WeasyPrint）
- 基本的なPDF生成
- テーブルと見出しサポート
- 日本語フォント互換性
