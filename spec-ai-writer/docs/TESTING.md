# テストガイド

Spec AIライターのテストスイート実行方法

## バックエンドテスト (Python/pytest)

### セットアップ

```bash
# テスト用依存パッケージのインストール
pip install -r requirements.txt
```

### テスト実行

```bash
# すべてのテストを実行
pytest

# カバレッジレポート付きで実行
pytest --cov=spec_ai_writer --cov-report=html

# 特定のテストファイルのみ実行
pytest tests/unit/test_context_manager.py

# 特定のマーカーのみ実行
pytest -m unit          # ユニットテストのみ
pytest -m api           # APIテストのみ
pytest -m integration   # 統合テストのみ

# 詳細出力
pytest -v -s

# 並列実行 (pytest-xdist必要)
pytest -n auto
```

### テストカバレッジ

カバレッジレポートは `htmlcov/index.html` に生成されます。

```bash
pytest --cov=spec_ai_writer --cov-report=html
open htmlcov/index.html  # macOS
```

## フロントエンドテスト (Vitest/Testing Library)

### セットアップ

```bash
cd frontend
npm install
```

### テスト実行

```bash
# すべてのテストを実行
npm test

# ウォッチモードで実行
npm test -- --watch

# UIモードで実行 (ブラウザで可視化)
npm run test:ui

# カバレッジレポート付きで実行
npm run test:coverage

# 特定のテストファイルのみ実行
npm test -- src/api/__tests__/client.test.ts
```

### テストカバレッジ

カバレッジレポートは `frontend/coverage/index.html` に生成されます。

```bash
npm run test:coverage
open coverage/index.html  # macOS
```

## テスト構成

### バックエンド

```
tests/
├── conftest.py              # Pytestフィクスチャと設定
├── unit/                    # ユニットテスト
│   ├── test_context_manager.py
│   └── test_phase_manager.py
├── api/                     # APIエンドポイントテスト
│   ├── test_projects_api.py
│   └── test_specifications_api.py
└── integration/             # 統合テスト
```

### フロントエンド

```
frontend/src/
├── api/__tests__/           # APIクライアントテスト
│   └── client.test.ts
├── store/__tests__/         # Zustandストアテスト
│   └── useProjectStore.test.ts
└── test/
    └── setup.ts             # テストセットアップ
```

## テストのベストプラクティス

### バックエンド

1. **モックの使用**
   - LLM APIコールは必ずモック化
   - 外部依存は `pytest-mock` でモック

2. **フィクスチャの活用**
   - `conftest.py` で共通フィクスチャを定義
   - テストデータは再利用可能に

3. **マーカーの使用**
   - `@pytest.mark.unit` - ユニットテスト
   - `@pytest.mark.api` - APIテスト
   - `@pytest.mark.integration` - 統合テスト
   - `@pytest.mark.slow` - 時間のかかるテスト

### フロントエンド

1. **Testing Libraryの原則**
   - ユーザーの視点でテスト
   - 実装詳細ではなく振る舞いをテスト
   - アクセシビリティを意識

2. **モックの使用**
   - API呼び出しは必ずモック化
   - MSW (Mock Service Worker) を使用

3. **非同期処理**
   - `waitFor` や `findBy*` を適切に使用
   - タイムアウトに注意

## CI/CD統合

### GitHub Actions例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=spec_ai_writer

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: cd frontend && npm install
      - run: cd frontend && npm test
```

## トラブルシューティング

### バックエンド

**問題**: `ImportError: No module named 'spec_ai_writer'`

**解決**: ルートディレクトリから実行してください
```bash
cd /path/to/spec-ai-writer
pytest
```

**問題**: LLM API呼び出しエラー

**解決**: モックが正しく設定されているか確認
```python
@pytest.fixture
def mock_llm_client():
    # モックの設定
```

### フロントエンド

**問題**: `Cannot find module '@/...'`

**解決**: `vitest.config.ts` のパスエイリアスを確認

**問題**: DOM関連エラー

**解決**: `src/test/setup.ts` でDOMモックを確認

## カバレッジ目標

- **全体**: 80%以上
- **コアロジック**: 90%以上
- **APIエンドポイント**: 85%以上
- **UIコンポーネント**: 75%以上

## 継続的改善

テストは継続的に改善していきます:

1. 新機能追加時は必ずテストも追加
2. バグ修正時はテストケースを追加
3. カバレッジレポートを定期的にレビュー
4. 遅いテストは最適化または `@pytest.mark.slow` でマーク
