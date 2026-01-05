import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Send, ArrowLeft, Loader2 } from 'lucide-react';
import { useInterviewStore } from '@/store/useInterviewStore';
import { WebSocketManager } from '@/api/websocket';
import type { ChatMessage, WebSocketMessage } from '@/types';

export default function Interview() {
  const { projectName } = useParams<{ projectName: string }>();
  const [input, setInput] = useState('');
  const [ws, setWs] = useState<WebSocketManager | null>(null);
  const [isConnecting, setIsConnecting] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const messages = useInterviewStore((state) => state.messages);
  const currentPhase = useInterviewStore((state) => state.currentPhase);
  const phaseName = useInterviewStore((state) => state.phaseName);
  const isWaitingForResponse = useInterviewStore(
    (state) => state.isWaitingForResponse
  );
  const setProjectName = useInterviewStore((state) => state.setProjectName);
  const setInterviewActive = useInterviewStore((state) => state.setInterviewActive);

  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    console.log('Received message:', message);
    const { addMessage, setCurrentPhase, setInterviewActive, setWaitingForResponse } =
      useInterviewStore.getState();

    switch (message.type) {
      case 'question':
        // Assistant question
        addMessage({
          role: 'assistant',
          content: message.content,
          timestamp: new Date().toISOString(),
        });

        if (message.metadata?.phase_num && message.metadata?.phase_name) {
          setCurrentPhase(message.metadata.phase_num, message.metadata.phase_name);
        }

        setWaitingForResponse(false);
        break;

      case 'phase_complete':
        // Phase completed
        addMessage({
          role: 'system',
          content: `✅ ${message.content}`,
          timestamp: new Date().toISOString(),
        });
        break;

      case 'spec_generated':
        // Spec generated
        addMessage({
          role: 'system',
          content: `📄 ${message.content}`,
          timestamp: new Date().toISOString(),
        });
        break;

      case 'complete':
        // Interview complete
        addMessage({
          role: 'system',
          content: `🎉 ${message.content}`,
          timestamp: new Date().toISOString(),
        });
        setInterviewActive(false);
        break;

      case 'error':
        // Error occurred
        addMessage({
          role: 'system',
          content: `❌ ${message.content}`,
          timestamp: new Date().toISOString(),
        });
        setWaitingForResponse(false);
        break;

      default:
        addMessage({
          role: 'system',
          content: `⚠️ 未対応のメッセージ: ${message.type}`,
          timestamp: new Date().toISOString(),
        });
    }
  }, []);

  useEffect(() => {
    if (!projectName) return;

    setProjectName(projectName);

    // Initialize WebSocket
    const websocket = new WebSocketManager(projectName);
    setWs(websocket);

    websocket
      .connect()
      .then(() => {
        setIsConnecting(false);
        setInterviewActive(true);
      })
      .catch((err) => {
        console.error('Failed to connect:', err);
        setError('WebSocket接続に失敗しました');
        setIsConnecting(false);
      });

    // Handle incoming messages
    const unsubscribe = websocket.onMessage((message: WebSocketMessage) => {
      handleWebSocketMessage(message);
    });

    // Cleanup
    return () => {
      unsubscribe();
      websocket.disconnect();
      setInterviewActive(false);
    };
  }, [handleWebSocketMessage, projectName, setInterviewActive, setProjectName]);

  useEffect(() => {
    // Auto-scroll to bottom
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || !ws || isWaitingForResponse) return;

    // Add user message to UI
    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    useInterviewStore.getState().addMessage(userMessage);

    // Send to WebSocket
    ws.sendAnswer(input.trim());

    setInput('');
    setWaitingForResponse(true);
  };

  if (!projectName) {
    return (
      <div className="card">
        <p className="text-red-600">プロジェクト名が指定されていません</p>
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
              インタビュー: {projectName}
            </h2>
            {phaseName && (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                フェーズ {currentPhase}: {phaseName}
              </p>
            )}
          </div>
        </div>
        <Link to={`/specs/${projectName}`} className="btn btn-secondary text-sm">
          仕様書を見る
        </Link>
      </div>

      {/* Error */}
      {error && (
        <div className="card bg-red-50 dark:bg-red-900/20 border border-red-200">
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      {/* Connecting */}
      {isConnecting && (
        <div className="card text-center py-12">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary-600" />
          <p className="mt-4 text-gray-500">接続中...</p>
        </div>
      )}

      {/* Chat Interface */}
      {!isConnecting && !error && (
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
                      ? 'bg-primary-600 text-white'
                      : message.role === 'system'
                        ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-900 dark:text-yellow-200'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
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
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="回答を入力してください..."
                className="input flex-1"
                disabled={isWaitingForResponse}
              />
              <button
                type="submit"
                className="btn btn-primary px-6 flex items-center gap-2"
                disabled={!input.trim() || isWaitingForResponse}
              >
                {isWaitingForResponse ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
                送信
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
