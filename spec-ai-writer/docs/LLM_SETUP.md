# LLMプロバイダー セットアップガイド

Spec AIライターは以下の7つのLLMプロバイダーに対応しています。使用するプロバイダーのセクションを参照してセットアップしてください。

| プロバイダー  | 特徴                                            | 推奨用途                   |
| ------------- | ----------------------------------------------- | -------------------------- |
| Anthropic     | 高品質な日本語対応、仕様書生成に最適            | 個人・チーム開発           |
| OpenAI (公式) | GPT-6 シリーズ対応                              | OpenAIを既に利用中の場合   |
| OpenRouter    | 100以上のモデルを単一APIで切替可能              | 複数モデルを試したい場合   |
| Moonshot      | Kimi シリーズ対応                               | 高コスパ、長コンテキスト   |
| Ollama        | API料金不要、オフライン動作、データ外部送信なし | プライバシー重視・検証用途 |
| LM Studio     | API料金不要、オフライン動作、データ外部送信なし | プライバシー重視・検証用途 |
| AWS Bedrock   | 既存AWSインフラ統合、IAM管理                    | エンタープライズ環境       |

> **Web UI からの設定**: 上記プロバイダーのほとんどは、Web ダッシュボードの「設定」ページから編集・即時反映できます。`.env` を編集してサーバーを再起動する必要はありません。変更は `data/settings.json` に保存され、環境変数よりも優先されます。
>
> **注意**: `data/settings.json` は API キーを**平文**で保存します（`.env` と同じリスクモデル）。共有マシンでの使用は避け、ファイルパーミッションは自動的に `0600` に設定されます。

## 生成パラメータ（Temperature / Effort）

生成パラメータは、選んでいるプロバイダーとモデルが対応している場合にだけ送信します。設定画面では、対応していない項目は変更できません。

**Temperature**（環境変数 `TEMPERATURE`）

| 送信する                                                        | 送信しない                                                                      |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| OpenAI の `gpt-3.5` / `gpt-4` / `gpt-4o` 系、Ollama、LM Studio | Claude、AWS Bedrock、OpenAI の `gpt-5` / `gpt-6` / `o` 系、その他の判定できないモデル |

`kimi-k2.6` は、設定にかかわらず 0.6 に固定して送信します。Claude の新しいモデルなど、`temperature` を受け付けないモデルに代わりとなる設定はありません。

**Effort**（環境変数 `EFFORT`、初期値 `auto`）

思考の深さを指定します。`auto` のときは送信せず、モデルの既定の動作になります。

| 接続先                                   | 選べる値                                                                                                         |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Claude / AWS Bedrock                     | Claude 4.7 以降は `low` / `medium` / `high` / `xhigh` / `max`。4.6 は `xhigh` なし。Opus 4.5 は `low`〜`high`。Haiku 4.5 などは対象外 |
| OpenAI                                   | `gpt-6` 系は `low`〜`max`。`gpt-5` / `o` 系は `low` / `medium` / `high`。`-pro` 系と `o1-mini` は対象外                 |
| OpenRouter、Moonshot、Ollama、LM Studio | 対象外                                                                                                           |

---

## Claude (Anthropic API)

### セットアップ

1. Anthropic APIキーを取得: https://console.anthropic.com/

2. `.env`ファイルを設定:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEFAULT_LLM_PROVIDER=claude
CLAUDE_MODEL=claude-haiku-5-5
```

### モデルの例

デフォルトモデル: `claude-haiku-5-5`

| モデル                         | モデルID            |
| ------------------------------ | ------------------- |
| Claude Haiku 5.5（デフォルト） | `claude-haiku-5-5`  |
| Claude Sonnet 5.5              | `claude-sonnet-5-5` |
| Claude Opus 5.5                | `claude-opus-5-5`   |

モデルIDは[Anthropic API モデルページ](https://platform.claude.com/docs/en/about-claude/models/overview)を、料金は [Anthropic API 料金ページ](https://platform.claude.com/docs/en/about-claude/pricing) を確認してください。

### トラブルシューティング

#### エラー: "Authentication error"

**原因**: APIキーが無効または未設定

**解決策**:

- `.env`ファイルの`ANTHROPIC_API_KEY`を確認
- キーが`sk-ant-`で始まることを確認

#### エラー: "Rate limit exceeded"

**原因**: レート制限に達した

**解決策**:

- しばらく待ってから再試行
- Anthropic ConsoleでUsage Tierを確認

---

## OpenAI

### セットアップ

1. OpenAI APIキーを取得: https://platform.openai.com/api-keys

2. `.env`ファイルを設定:

```env
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_LLM_PROVIDER=openai
OPENAI_MODEL=gpt-6-luna
```

### モデルの例

デフォルトモデル: `gpt-6-luna`

| モデル                   | モデルID        |
| ------------------------ | --------------- |
| GPT-6 Luna（デフォルト） | `gpt-6-luna`    |
| GPT-6.1 Sol              | `gpt-6.1-sol`   |
| GPT-6 Astra              | `gpt-6-astra`   |

> **推論モデルについて**: `gpt-5` / `gpt-6` / `o` 系は `max_completion_tokens` を使い、`temperature` は送信しません。モデルのファミリーごとに `provider_registry.py` で判定するため、モデル ID を指定するだけで適切なパラメータが使用されます。

料金は [OpenAI API 料金ページ](https://openai.com/api/pricing/) を確認してください。

### トラブルシューティング

#### エラー: "Incorrect API key provided"

**原因**: APIキーが無効

**解決策**:

- `.env`ファイルの`OPENAI_API_KEY`を確認
- OpenAI Dashboardでキーが有効か確認

---

## OpenRouter

[OpenRouter](https://openrouter.ai/) は 100 以上の LLM を単一 API で切り替えられるサービスです。

### セットアップ

1. OpenRouter API キーを取得: https://openrouter.ai/keys
2. 使用したいモデル ID を確認: https://openrouter.ai/models
3. `.env` ファイルを設定:

```env
DEFAULT_LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
OPENROUTER_MODEL=nvidia/nemotron-3.5-lightning:free
```

または Web UI の「設定」ページで **「OpenRouter」** を選び、API キーとモデル ID を入力して保存します。

### モデル ID の例

| モデル                                  | モデル ID                            |
| --------------------------------------- | ------------------------------------ |
| Nemotron 3.5 Lightning（デフォルト）    | `nvidia/nemotron-3.5-lightning:free` |
| Claude Haiku 5.5                        | `anthropic/claude-haiku-5.5`         |
| GPT-6 Luna                              | `openai/gpt-6-luna`                  |
| Gemma 4 31B                             | `google/gemma-4-31b-it:free`         |

`:free` の付いたモデルは、提供が終了することがあります。

料金は [OpenRouter Models](https://openrouter.ai/models) を確認してください。

### トラブルシューティング

#### エラー: "No auth credentials found"

**原因**: `OPENROUTER_API_KEY` が設定されていない

**解決策**:

- [OpenRouter の API キー管理画面](https://openrouter.ai/keys) で発行したキー (`sk-or-v1-...`) を設定

#### エラー: "Model not found"

**原因**: `OPENROUTER_MODEL` が OpenRouter の命名規則と異なる

**解決策**:

- `anthropic/claude-haiku-5.5` のように `provider/model` 形式で指定
- [モデル一覧](https://openrouter.ai/models) から正確な ID をコピー

---

## Moonshot Kimi

[Moonshot AI](https://platform.moonshot.cn/) が提供するクラウド LLM です。OpenAI 互換 API として接続します。

### セットアップ

1. Kimi API キーを取得: https://platform.moonshot.cn/
2. `.env` ファイルを設定:

```env
DEFAULT_LLM_PROVIDER=kimi
KIMI_API_KEY=your_kimi_api_key_here
KIMI_MODEL=kimi-k3
```

または Web UI の「設定」ページで **「Moonshot Kimi」** を選び、API キーとモデル ID を入力して保存します。

### モデルの例

| モデル                | モデル ID       |
| --------------------- | --------------- |
| Kimi K3（デフォルト） | `kimi-k3`       |
| Kimi K3.1 Pro         | `kimi-k3.1-pro` |

`kimi-k2.6` は 2026 年 12 月下旬に廃止予定で、2026 年 11 月 1 日以降に登録したユーザーは利用できません。

モデルの一覧は [Kimi API のモデル一覧](https://platform.kimi.ai/docs/models) を、料金は [Moonshot Platform](https://platform.moonshot.cn/) を確認してください。

---

## ローカル LLM (Ollama / LM Studio)

OpenAI 互換 HTTP API を提供するローカル LLM ランタイムに接続できます。API 料金なし、データが外部に送信されない、オフラインで動作するなどのメリットがあります。

> ⚠️ **品質について**: 小規模モデル (7B 以下) ではインタビュー質問の生成や構造化データ抽出 (JSON) が不安定になる場合があります。**13B 以上** のモデルを推奨します。

### Ollama

1. [Ollama](https://ollama.com/) をインストール
2. モデルをダウンロード:
   ```bash
   ollama pull gemma4
   ```
3. `.env` ファイルを設定:
   ```env
   DEFAULT_LLM_PROVIDER=ollama
   OLLAMA_MODEL=gemma4
   # OLLAMA_BASE_URL=   # 空欄 = http://localhost:11434/v1
   ```
4. Ollama サーバーが起動していることを確認:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### LM Studio

1. [LM Studio](https://lmstudio.ai/) をインストール
2. モデルをダウンロード (GGUF 形式)
3. LM Studio の「Local Server」タブから OpenAI 互換サーバーを起動 (デフォルト: `http://localhost:1234`)
4. `.env` ファイルを設定:
   ```env
   DEFAULT_LLM_PROVIDER=lmstudio
   LMSTUDIO_MODEL=google/gemma-4  # 読み込んだモデルの識別子に合わせて変更
   # LMSTUDIO_BASE_URL=        # 空欄 = http://localhost:1234/v1
   ```

### Web UI からの設定

Web ダッシュボードの「設定」ページで **「Ollama (ローカル)」** または **「LM Studio (ローカル)」** を選択すると、モデル名と Base URL（変更する場合のみ）を入力して保存できます。

### トラブルシューティング

#### エラー: "Connection refused"

**原因**: ローカル LLM サーバーが起動していない

**解決策**:

- Ollama: `ollama serve` で起動確認、または `ollama run <モデル名>` で自動起動
- LM Studio: アプリケーションの「Local Server」タブで Start をクリック
- ポートが設定と一致しているか確認

#### エラー: インタビュー質問が壊れる / JSON 抽出に失敗する

**原因**: モデルの能力不足。小規模モデルでは日本語の指示追従や JSON 出力の整合性が不足する

**解決策**:

- より大きいモデルに切替 (13B 以上を推奨)
- 量子化レベルを上げる (Q5_K_M 以上を推奨)
- インタビュー途中で生成に失敗した場合は、Claude または Kimi に一時的に切り替えて先に進めることを検討

---

## AWS Bedrock

AWS Bedrockを使用すると、既存のAWSインフラ内でClaudeモデルを実行できます。

> **依存ライブラリ**: Bedrock クライアントは `aiobotocore` を使用します。（`boto3` ではありません）

### メリット

- 既存のAWSインフラ統合: 他のAWSサービスと同じVPC・IAMで管理
- コンプライアンス対応: 企業のセキュリティポリシーに準拠
- プライベートネットワーク: VPC Endpointでインターネット経由のアクセス不要
- 監査ログ: CloudTrailで全API呼び出しを記録

### 前提条件

- AWSアカウント
- Bedrock API キー、または AWS のアクセスキーとシークレットキー

### セットアップ

#### ステップ1: AWS Bedrockでモデルアクセスを有効化

1. AWS Consoleにログイン
2. リージョンを選択 (推奨: `ap-northeast-1`)
3. AWS Bedrock → Model access
4. 「Manage model access」をクリック
5. 「Anthropic」セクションで使用するモデルを有効化 (例: Claude Haiku 5.5)

#### ステップ2: IAMポリシーの設定

**最小権限ポリシー (推奨)**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": [
        "arn:aws:bedrock:*:*:inference-profile/*anthropic.claude-haiku-5-5*",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-haiku-5-5*"
      ]
    }
  ]
}
```

#### ステップ3: 認証情報の設定

Bedrock API キーか、アクセスキーとシークレットキーの組のどちらかを設定します。両方を設定した場合は、Bedrock API キーを使います。Web UI の「設定」ページの「AWS Bedrock」でも設定できます。

**オプション A: Bedrock API キー**

[Bedrock API キー](https://docs.aws.amazon.com/ja_jp/bedrock/latest/userguide/api-keys.html)を発行し、`.env`ファイルに設定します。短期キーは最長 12 時間で失効し、発行したリージョンでのみ使えます。

```env
AWS_BEARER_TOKEN_BEDROCK=your_bedrock_api_key_here
AWS_REGION=ap-northeast-1
DEFAULT_LLM_PROVIDER=bedrock
```

**オプション B: アクセスキーとシークレットキー**

`.env`ファイル:

```env
AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_REGION=ap-northeast-1
DEFAULT_LLM_PROVIDER=bedrock
```

### モデルの例

Bedrockでは Cross-Region Inference Profile を使用してモデルにアクセスします。

デフォルトモデル: `global.anthropic.claude-haiku-5-5`

| モデル                         | Inference Profile ID                | 備考                     |
| ------------------------------ | ----------------------------------- | ------------------------ |
| Claude Haiku 5.5（デフォルト） | `global.anthropic.claude-haiku-5-5` | リージョンを問わない     |
| Claude Haiku 5.5               | `jp.anthropic.claude-haiku-5-5`     | 日本のリージョンで処理   |

`global.` と `jp.` は、それぞれ別のリソースとして IAM で許可が必要です。

料金は [AWS Bedrock 料金ページ](https://aws.amazon.com/bedrock/pricing/) を確認してください。

### トラブルシューティング

#### エラー: "Could not connect to the endpoint URL"

**原因**: リージョンが正しくない、またはBedrockが利用できないリージョン

**解決策**:

```env
AWS_REGION=ap-northeast-1  # 正しいリージョンに変更
```

#### エラー: "AccessDeniedException"

**原因**: IAMポリシーが不足、またはモデルアクセスが有効化されていない

画面には「LLM APIキーが無効、または、モデルの利用が許可されていません。」と表示されます。

**解決策**:

1. AWS Console → Bedrock → Model accessでモデルを有効化
2. IAMポリシーで、使用する Inference Profile に対する`bedrock:InvokeModel`権限を付与
3. 許可されているモデルの ID（`global.` または `jp.`）を設定

#### エラー: "ValidationException: The provided model identifier is invalid"

**原因**: モデルIDが間違っている、またはリージョンで利用不可

**解決策**:

```bash
# 利用可能なモデルを確認
aws bedrock list-foundation-models --region ap-northeast-1 \
  --query 'modelSummaries[?contains(modelId, `claude`)].modelId'
```

---

**関連リンク**:

- [Anthropic API ドキュメント](https://docs.anthropic.com/)
- [OpenAI API ドキュメント](https://platform.openai.com/docs)
- [OpenRouter ドキュメント](https://openrouter.ai/docs)
- [Moonshot Platform ドキュメント](https://platform.moonshot.cn/docs)
- [AWS Bedrock 公式ドキュメント](https://docs.aws.amazon.com/bedrock/)
