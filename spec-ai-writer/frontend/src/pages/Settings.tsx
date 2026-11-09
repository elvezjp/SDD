import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Save, Info, AlertCircle, CheckCircle2, Leaf } from "lucide-react";
import apiClient from "@/api/client";
import type {
  LLMProvider,
  ProviderUpdate,
  SettingsResponse,
  SettingsUpdateRequest,
  SettingsSource,
} from "@/types";

// ---------------------------------------------------------------------------
// Provider metadata (UI labels and field visibility)
// ---------------------------------------------------------------------------

interface ProviderMeta {
  label: string;
  hasApiKey: boolean;
  hasBaseUrl: boolean;
  hasBedrock: boolean;
  appliesTemperature: boolean;
}

const PROVIDER_META: Record<LLMProvider, ProviderMeta> = {
  claude: {
    label: "Anthropic",
    hasApiKey: true,
    hasBaseUrl: false,
    hasBedrock: false,
    appliesTemperature: false,
  },
  openai: {
    label: "OpenAI",
    hasApiKey: true,
    hasBaseUrl: false,
    hasBedrock: false,
    appliesTemperature: true,
  },
  openrouter: {
    label: "OpenRouter",
    hasApiKey: true,
    hasBaseUrl: false,
    hasBedrock: false,
    appliesTemperature: true,
  },
  ollama: {
    label: "Ollama (ローカル)",
    hasApiKey: false,
    hasBaseUrl: true,
    hasBedrock: false,
    appliesTemperature: true,
  },
  lmstudio: {
    label: "LM Studio (ローカル)",
    hasApiKey: false,
    hasBaseUrl: true,
    hasBedrock: false,
    appliesTemperature: true,
  },
  kimi: {
    label: "Moonshot",
    hasApiKey: true,
    hasBaseUrl: false,
    hasBedrock: false,
    appliesTemperature: true,
  },
  bedrock: {
    label: "AWS Bedrock",
    hasApiKey: false,
    hasBaseUrl: false,
    hasBedrock: true,
    appliesTemperature: false,
  },
};

const PROVIDER_ORDER: LLMProvider[] = [
  "claude",
  "openai",
  "openrouter",
  "kimi",
  "ollama",
  "lmstudio",
  "bedrock",
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function EnvBadge() {
  return (
    <span
      className="inline-flex items-center gap-1 ml-2 px-1.5 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
      title="環境変数から読み込まれています。保存すると JSON に書き込まれ、環境変数の変更が反映されなくなります。"
    >
      <Leaf className="h-3 w-3" />
      ENV
    </span>
  );
}

// ---------------------------------------------------------------------------
// Per-provider slot state
// ---------------------------------------------------------------------------

interface SlotState {
  model: string; // "" = user hasn't typed anything (use env/default)
  apiKey: string; // "" = no change
  baseUrl: string; // "" = use registry default
  awsAccessKeyId: string;
  awsSecretAccessKey: string;
  awsRegion: string;
}

function emptySlot(): SlotState {
  return {
    model: "",
    apiKey: "",
    baseUrl: "",
    awsAccessKeyId: "",
    awsSecretAccessKey: "",
    awsRegion: "",
  };
}

function buildInitialSlots(
  data: SettingsResponse,
): Record<LLMProvider, SlotState> {
  const slots = Object.fromEntries(
    PROVIDER_ORDER.map((p) => [p, emptySlot()]),
  ) as Record<LLMProvider, SlotState>;

  for (const p of PROVIDER_ORDER) {
    const prov = data.providers[p];
    if (!prov) continue;
    const slot = { ...emptySlot() };
    if (data.sources[`${p}.model`] === "json") slot.model = prov.model;
    if (data.sources[`${p}.base_url`] === "json")
      slot.baseUrl = prov.base_url ?? "";
    if (data.sources[`${p}.aws_region`] === "json")
      slot.awsRegion = prov.aws_region ?? "";
    slots[p] = slot;
  }
  return slots;
}

// ---------------------------------------------------------------------------
// Inner form component — initializes state from props, avoids set-state-in-effect
// ---------------------------------------------------------------------------

function SettingsForm({ initialData }: { initialData: SettingsResponse }) {
  const queryClient = useQueryClient();

  // All state is initialized synchronously from props — no useEffect needed
  const [activeProvider, setActiveProvider] = useState<LLMProvider>(
    () => initialData.active_provider,
  );
  const [temperature, setTemperature] = useState<number>(
    () => initialData.temperature,
  );
  const [slots, setSlots] = useState<Record<LLMProvider, SlotState>>(() =>
    buildInitialSlots(initialData),
  );
  const [dirty, setDirty] = useState(false);
  const [saveNotice, setSaveNotice] = useState<{
    kind: "success" | "error";
    message: string;
  } | null>(null);

  // Tracks the latest server state for displaying masked keys and source badges.
  // Updated in onSuccess callback (not in useEffect).
  const [displayData, setDisplayData] = useState<SettingsResponse>(initialData);

  const mutation = useMutation({
    mutationFn: (data: SettingsUpdateRequest) => apiClient.updateSettings(data),
    onSuccess: (data: SettingsResponse) => {
      queryClient.setQueryData(["settings"], data);
      setDisplayData(data);
      setDirty(false);
      setSaveNotice({
        kind: "success",
        message: "設定を保存し、即座に反映しました。",
      });
    },
    onError: (err: unknown) => {
      const anyErr = err as {
        response?: { data?: { detail?: string } };
        message?: string;
      };
      const detail =
        anyErr?.response?.data?.detail ?? anyErr?.message ?? "不明なエラー";
      setSaveNotice({
        kind: "error",
        message: `保存に失敗しました: ${detail}`,
      });
    },
  });

  const markDirty = () => {
    setDirty(true);
    if (saveNotice?.kind === "success") setSaveNotice(null);
  };

  const updateSlot = (provider: LLMProvider, patch: Partial<SlotState>) => {
    setSlots((prev) => ({
      ...prev,
      [provider]: { ...prev[provider], ...patch },
    }));
    markDirty();
  };

  const handleSubmit = (e: { preventDefault(): void }) => {
    e.preventDefault();
    setSaveNotice(null);

    // Build per-provider updates — only include the active provider's slot
    const slot = slots[activeProvider];
    const providerUpdate: ProviderUpdate = {};

    // model/base_url/aws_region: always send (even empty = delete from JSON → revert to default)
    providerUpdate.model = slot.model;
    if (slot.apiKey) providerUpdate.api_key = slot.apiKey;
    if (
      slot.baseUrl !== undefined &&
      PROVIDER_META[activeProvider].hasBaseUrl
    ) {
      providerUpdate.base_url = slot.baseUrl;
    }
    if (activeProvider === "bedrock") {
      if (slot.awsAccessKeyId)
        providerUpdate.aws_access_key_id = slot.awsAccessKeyId;
      if (slot.awsSecretAccessKey)
        providerUpdate.aws_secret_access_key = slot.awsSecretAccessKey;
      providerUpdate.aws_region = slot.awsRegion;
    }

    const payload: SettingsUpdateRequest = {
      active_provider: activeProvider,
      temperature,
      providers: { [activeProvider]: providerUpdate },
    };

    mutation.mutate(payload);
  };

  const prov = displayData.providers[activeProvider];
  const slot = slots[activeProvider];
  const meta = PROVIDER_META[activeProvider];
  const src = (key: string): SettingsSource =>
    displayData.sources[key] ?? "default";

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          LLM 設定
        </h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          使用するプロバイダと認証情報を設定します。保存すると即座に反映されます（再起動不要）。
        </p>
      </div>

      {/* Security warning */}
      <div className="card bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
        <div className="flex items-start gap-3 text-sm text-yellow-800 dark:text-yellow-200">
          <Info className="h-5 w-5 shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">API キーは平文で保存されます</p>
            <p className="mt-1">
              設定は{" "}
              <code className="px-1 bg-yellow-100 dark:bg-yellow-900 rounded">
                data/settings.json
              </code>{" "}
              に保存されます。共有マシンでの使用は避けてください。
            </p>
          </div>
        </div>
      </div>

      {saveNotice && (
        <div
          className={
            saveNotice.kind === "success"
              ? "card bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
              : "card bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800"
          }
        >
          <div
            className={
              saveNotice.kind === "success"
                ? "flex items-center gap-3 text-green-700 dark:text-green-300"
                : "flex items-center gap-3 text-red-700 dark:text-red-300"
            }
          >
            {saveNotice.kind === "success" ? (
              <CheckCircle2 className="h-5 w-5" />
            ) : (
              <AlertCircle className="h-5 w-5" />
            )}
            <span>{saveNotice.message}</span>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Provider selector */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            プロバイダ
          </h3>
          <div className="space-y-2">
            {PROVIDER_ORDER.map((p) => (
              <label key={p} className="flex items-center gap-3 cursor-pointer">
                <input
                  type="radio"
                  name="provider"
                  value={p}
                  checked={activeProvider === p}
                  onChange={() => {
                    setActiveProvider(p);
                    markDirty();
                  }}
                  className="h-4 w-4 text-primary-500"
                />
                <span className="text-gray-900 dark:text-white">
                  {PROVIDER_META[p].label}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Active provider settings */}
        <div className="card space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {meta.label} の設定
          </h3>

          {/* Model */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              モデル ID
              {src(`${activeProvider}.model`) === "env" && <EnvBadge />}
            </label>
            <input
              type="text"
              value={slot.model}
              onChange={(e) =>
                updateSlot(activeProvider, { model: e.target.value })
              }
              placeholder={prov?.model ?? ""}
              className="input w-full font-mono text-sm"
            />
          </div>

          {/* API Key */}
          {meta.hasApiKey && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                API キー
                {src(`${activeProvider}.api_key`) === "env" && <EnvBadge />}
              </label>
              <input
                type="password"
                value={slot.apiKey}
                onChange={(e) =>
                  updateSlot(activeProvider, { apiKey: e.target.value })
                }
                placeholder={
                  prov?.api_key_masked
                    ? `${prov.api_key_masked}（変更する場合のみ入力）`
                    : "新しい API キーを入力"
                }
                className="input w-full"
                autoComplete="off"
              />
            </div>
          )}

          {/* Base URL (Ollama / LM Studio) */}
          {meta.hasBaseUrl && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Base URL
                {src(`${activeProvider}.base_url`) === "env" && <EnvBadge />}
              </label>
              <input
                type="text"
                value={slot.baseUrl}
                onChange={(e) =>
                  updateSlot(activeProvider, { baseUrl: e.target.value })
                }
                placeholder={
                  src(`${activeProvider}.base_url`) === "env" && prov?.base_url
                    ? `${prov.base_url}`
                    : (prov?.base_url ?? "")
                }
                className="input w-full font-mono text-sm"
              />
            </div>
          )}

          {/* Bedrock fields */}
          {meta.hasBedrock && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  リージョン
                  {src("bedrock.aws_region") === "env" && <EnvBadge />}
                </label>
                <input
                  type="text"
                  value={slot.awsRegion}
                  onChange={(e) =>
                    updateSlot("bedrock", { awsRegion: e.target.value })
                  }
                  placeholder={
                    src("bedrock.aws_region") === "env" && prov?.aws_region
                      ? `${prov.aws_region}`
                      : "ap-northeast-1"
                  }
                  className="input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  AWS Access Key ID
                  {src("bedrock.aws_access_key_id") === "env" && <EnvBadge />}
                </label>
                <input
                  type="password"
                  value={slot.awsAccessKeyId}
                  onChange={(e) =>
                    updateSlot("bedrock", { awsAccessKeyId: e.target.value })
                  }
                  placeholder={
                    prov?.aws_access_key_id_masked
                      ? `${prov.aws_access_key_id_masked}（変更する場合のみ入力）`
                      : "AKIA..."
                  }
                  className="input w-full"
                  autoComplete="off"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  AWS Secret Access Key
                  {src("bedrock.aws_secret_access_key") === "env" && (
                    <EnvBadge />
                  )}
                </label>
                <input
                  type="password"
                  value={slot.awsSecretAccessKey}
                  onChange={(e) =>
                    updateSlot("bedrock", {
                      awsSecretAccessKey: e.target.value,
                    })
                  }
                  placeholder={
                    prov?.aws_secret_access_key_masked
                      ? `${prov.aws_secret_access_key_masked}（変更する場合のみ入力）`
                      : ""
                  }
                  className="input w-full"
                  autoComplete="off"
                />
              </div>
            </>
          )}
        </div>

        {/* Temperature */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            生成パラメータ
            {src("temperature") === "env" && <EnvBadge />}
          </h3>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Temperature:{" "}
              <span className="font-mono">{temperature.toFixed(2)}</span>
            </label>
            <input
              type="range"
              min={0}
              max={2}
              step={0.05}
              value={temperature}
              disabled={!PROVIDER_META[activeProvider].appliesTemperature}
              onChange={(e) => {
                setTemperature(parseFloat(e.target.value));
                markDirty();
              }}
              className="w-full disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {PROVIDER_META[activeProvider].appliesTemperature
                ? "一部のモデル（GPT-5 系、o 系、Kimi K2.6 など）には適用されません。"
                : "Claude のモデルには Temperature を送信しないため、この設定は適用されません。"}
            </p>
          </div>
        </div>

        {/* Save */}
        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={!dirty || mutation.isPending}
            className="btn btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="h-4 w-4" />
            {mutation.isPending ? "保存中..." : "保存"}
          </button>
          {dirty && (
            <span className="text-xs text-gray-500 dark:text-gray-400">
              未保存の変更があります
            </span>
          )}
        </div>
      </form>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Outer component — handles loading/error before delegating to SettingsForm
// ---------------------------------------------------------------------------

export default function Settings() {
  const {
    data: serverData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["settings"],
    queryFn: () => apiClient.getSettings(),
  });

  if (isLoading) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400">
        設定を読み込み中...
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
        <div className="flex items-center gap-3 text-red-700 dark:text-red-300">
          <AlertCircle className="h-5 w-5" />
          <span>設定の読み込みに失敗しました。</span>
        </div>
      </div>
    );
  }

  if (!serverData) return null;

  return <SettingsForm initialData={serverData} />;
}
