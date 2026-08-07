import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router';
import { Send, ArrowLeft, Loader2, Square } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useInterviewStore } from '@/store/useInterviewStore';
import axios from 'axios';
import apiClient from '@/api/client';
import type { ChatMessage } from '@/types';

function format422Error(detail: Array<{ type: string; ctx?: Record<string, unknown> }>): string {
  return detail
    .map(({ type, ctx }) => {
      switch (type) {
        case 'string_too_long':
          return `入力が長すぎます（上限: ${ctx?.max_length}文字）`;
        case 'string_too_short':
          return `入力が短すぎます（最低: ${ctx?.min_length}文字）`;
        case 'greater_than_equal':
        case 'less_than_equal':
          return 'フェーズ番号が無効です';
        default:
          return 'リクエストの形式が無効です';
      }
    })
    .join('、');
}

export default function Interview() {
  const { projectId } = useParams<{ projectId: string }>();
  const [input, setInput] = useState('');
  const [isStarting, setIsStarting] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const {
    messages,
    displayName,
    currentPhase,
    phaseName,
    isWaitingForResponse,
    isInterviewActive,
    addMessage,
    setCurrentPhase,
    setProjectId,
    setDisplayName,
    setInterviewActive,
    setWaitingForResponse,
    reset,
  } = useInterviewStore();

  // Start interview via REST API
  const startInterview = useCallback(async () => {
    if (!projectId) return;

    // Reset previous session state (messages may persist during SPA navigation)
    reset();
    setIsStarting(true);
    setError(null);
    setProjectId(projectId);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await apiClient.startInterview(
        { project_id: projectId },
        controller.signal
      );

      setDisplayName(response.display_name);
      setCurrentPhase(response.phase_num, response.phase_name);

      if (response.chat_history && response.chat_history.length > 0) {
        response.chat_history.forEach((msg) => addMessage(msg));
      }

      if (response.all_complete) {
        setInterviewActive(false);
        return;
      }

      setInterviewActive(true);
      if (response.initial_message) {
        addMessage({
          role: 'assistant',
          content: response.initial_message,
          timestamp: new Date().toISOString(),
        });
      } else {
        // New phase: show chat area first, then auto-call POST /answer to generate the first question
        setIsStarting(false);
        setWaitingForResponse(true);
        try {
          const questionResponse = await apiClient.submitAnswer(
            { project_id: projectId },
            controller.signal
          );
          addMessage({
            role: 'assistant',
            content: questionResponse.question,
            timestamp: new Date().toISOString(),
          });
        } catch (questionErr) {
          if (!axios.isCancel(questionErr)) {
            setError('最初の質問の生成に失敗しました。再度お試しください。');
          }
        } finally {
          setWaitingForResponse(false);
        }
      }
    } catch (err) {
      if (axios.isCancel(err)) return;
      console.error('Failed to start interview:', err);
      setError('インタビューの開始に失敗しました。バックエンドサーバーの接続を確認してください。');
    } finally {
      abortControllerRef.current = null;
      setIsStarting(false);
    }
  }, [projectId, setProjectId, setCurrentPhase, setInterviewActive, addMessage, reset, setDisplayName, setWaitingForResponse]);

  useEffect(() => {
    if (!projectId) return;

    // eslint-disable-next-line react-hooks/set-state-in-effect
    startInterview();

    // Cleanup
    return () => {
      abortControllerRef.current?.abort();
      setInterviewActive(false);
    };
  }, [projectId]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    // Auto-scroll to bottom
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const submitMessage = async () => {
    if (!input.trim() || !projectId || isWaitingForResponse) return;

    const userAnswer = input.trim();

    // Add user message to UI
    const userMessage: ChatMessage = {
      role: 'user',
      content: userAnswer,
      timestamp: new Date().toISOString(),
    };

    addMessage(userMessage);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    setWaitingForResponse(true);
    setError(null);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await apiClient.submitAnswer(
        { project_id: projectId, answer: userAnswer },
        controller.signal
      );

      // Check if phase is complete
      if (response.phase_complete) {
        // Add phase completion message
        addMessage({
          role: 'system',
          content: `フェーズ ${response.phase_num} が完了しました。`,
          timestamp: new Date().toISOString(),
        });

        // Check if all phases (1-7) are done
        if (response.phase_num >= 7) {
          addMessage({
            role: 'system',
            content: '全てのフェーズが完了しました。仕様書が生成されました。',
            timestamp: new Date().toISOString(),
          });
          setInterviewActive(false);
          return;
        }

        setCurrentPhase(response.phase_num + 1, '');
      }

      // Add the next question
      addMessage({
        role: 'assistant',
        content: response.question,
        timestamp: new Date().toISOString(),
      });
    } catch (err) {
      if (axios.isCancel(err)) {
        addMessage({
          role: 'system',
          content: '送信を中断しました。',
          timestamp: new Date().toISOString(),
        });
        return;
      }
      console.error('Failed to submit answer:', err);
      const content =
        axios.isAxiosError(err) &&
        err.response?.status === 422 &&
        Array.isArray(err.response.data?.detail) &&
        err.response.data.detail.length > 0
          ? format422Error(err.response.data.detail)
          : '回答の送信中にエラーが発生しました。再度お試しください。';
      addMessage({
        role: 'system',
        content,
        timestamp: new Date().toISOString(),
      });
    } finally {
      abortControllerRef.current = null;
      setWaitingForResponse(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submitMessage();
  };

  const handleAbort = () => {
    abortControllerRef.current?.abort();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      submitMessage();
    }
  };

  if (!projectId) {
    return (
      <div className="card">
        <p className="text-red-600">プロジェクトIDが指定されていません</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/dashboard" className="btn btn-ghost p-2">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              インタビュー: {displayName || projectId}
            </h2>
            {phaseName && (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                フェーズ {currentPhase}: {phaseName}
              </p>
            )}
          </div>
        </div>
        <Link to={`/specs/${projectId}`} className="btn btn-secondary text-sm">
          仕様書を見る
        </Link>
      </div>

      {/* Error */}
      {error && (
        <div className="card bg-red-50 dark:bg-red-900/20 border border-red-200">
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      {/* Starting */}
      {isStarting && (
        <div className="card text-center py-12">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary-500" />
          <p className="mt-4 text-gray-500">インタビューを開始しています...</p>
        </div>
      )}

      {/* Chat Interface */}
      {!isStarting && !error && (
        <div className="card p-0 flex flex-col h-[calc(100vh-16rem)]">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 py-12">
                <p>インタビューを開始します...</p>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-primary-500 text-white'
                      : message.role === 'system'
                        ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-900 dark:text-yellow-200'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                  }`}
                >
                  {message.role === 'assistant' ? (
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  )}
                  <p
                    className={`text-xs mt-1 ${
                      message.role === 'user'
                        ? 'text-primary-100'
                        : 'text-gray-500 dark:text-gray-400'
                    }`}
                  >
                    {new Date(message.timestamp).toLocaleTimeString('ja-JP')}
                  </p>
                </div>
              </div>
            ))}

            {isWaitingForResponse && (
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-gray-700 rounded-lg px-4 py-2">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <div className="border-t border-gray-200 dark:border-gray-700 p-4">
            <form onSubmit={handleSubmit} className="flex gap-2 items-end">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  const el = e.target;
                  el.style.height = 'auto';
                  el.style.height = el.scrollHeight + 'px';
                }}
                onKeyDown={handleKeyDown}
                placeholder="回答を入力してください..."
                className="input flex-1 resize-none overflow-hidden"
                rows={1}
                disabled={isWaitingForResponse || !isInterviewActive}
              />
              <div className="flex flex-col gap-2">
                {isWaitingForResponse ? (
                  <button
                    type="button"
                    onClick={handleAbort}
                    className="btn btn-secondary px-4 flex items-center gap-2"
                  >
                    <Square className="h-5 w-5" />
                    中断
                  </button>
                ) : (
                  <button
                    type="submit"
                    className="btn btn-primary px-4 flex items-center gap-2"
                    disabled={!input.trim() || !isInterviewActive}
                  >
                    <Send className="h-5 w-5" />
                    送信
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
