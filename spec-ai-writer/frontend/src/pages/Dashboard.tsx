import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router';
import { Plus, Trash2, ExternalLink, Clock, CheckCircle2 } from 'lucide-react';
import { format } from 'date-fns';
import { ja } from 'date-fns/locale';
import apiClient from '@/api/client';
import type { ProjectCreate } from '@/types';

export default function Dashboard() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const queryClient = useQueryClient();

  // Fetch projects
  const {
    data: projectsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['projects'],
    queryFn: () => apiClient.listProjects(),
  });

  // Create project mutation
  const createMutation = useMutation({
    mutationFn: (data: ProjectCreate) => apiClient.createProject(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setIsCreateModalOpen(false);
      setNewProjectName('');
    },
  });

  // Delete project mutation
  const deleteMutation = useMutation({
    mutationFn: (projectId: string) => apiClient.deleteProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });

  const handleCreateProject = (e: React.FormEvent) => {
    e.preventDefault();
    if (newProjectName.trim()) {
      createMutation.mutate({
        display_name: newProjectName.trim(),
      });
    }
  };

  const getPhaseStatusBadge = (currentPhase: number) => {
    if (currentPhase === 7) {
      return (
        <span className="badge badge-success flex items-center gap-1">
          <CheckCircle2 className="h-3 w-3" />
          完了
        </span>
      );
    }
    return (
      <span className="badge badge-info flex items-center gap-1">
        <Clock className="h-3 w-3" />
        フェーズ {currentPhase}
      </span>
    );
  };

  const isMockMode = import.meta.env.VITE_USE_MOCK_API === 'true';

  return (
    <div className="space-y-6">
      {/* Mock Mode Banner */}
      {isMockMode && (
        <div className="card bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0">
              <span className="text-2xl">🎭</span>
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-yellow-900 dark:text-yellow-200">
                モックモードで動作中
              </h3>
              <p className="text-sm text-yellow-800 dark:text-yellow-300 mt-1">
                実際のLLM APIを呼び出さずに、サンプルデータでUIを確認できます。
                実際の機能を使用するには、環境変数 <code className="bg-yellow-100 dark:bg-yellow-900/50 px-1 rounded">VITE_USE_MOCK_API</code> を削除してバックエンドサーバーを起動してください。
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            プロジェクト一覧
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            仕様駆動開発ドキュメントを作成・管理します
          </p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="h-5 w-5" />
          新規プロジェクト
        </button>
      </div>

      {/* Projects Grid */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
          <p className="mt-2 text-gray-500">読み込み中...</p>
        </div>
      )}

      {error && (
        <div className="card bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
          <p className="text-red-800 dark:text-red-200">
            エラーが発生しました: {(error as Error).message}
          </p>
        </div>
      )}

      {projectsData && projectsData.projects.length === 0 && (
        <div className="card text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">
            プロジェクトがありません。新規プロジェクトを作成してください。
          </p>
        </div>
      )}

      {projectsData && projectsData.projects.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projectsData.projects.map((project) => (
            <div key={project.project_id} className="card hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {project.display_name}
                  </h3>
                </div>
                {getPhaseStatusBadge(project.current_phase)}
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400">進捗</span>
                  <span className="font-medium">
                    {Object.values(project.phase_status).filter((s) => s === 'completed')
                      .length}{' '}
                    / 7 フェーズ
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${
                        (Object.values(project.phase_status).filter(
                          (s) => s === 'completed'
                        ).length /
                          7) *
                        100
                      }%`,
                    }}
                  />
                </div>
              </div>

              <div className="flex flex-col gap-2 mb-4 text-xs text-gray-500 dark:text-gray-400">
                <div className="flex justify-between">
                  <span>Q&A数:</span>
                  <span>{project.total_qa_pairs}</span>
                </div>
                <div className="flex justify-between">
                  <span>更新日:</span>
                  <span>
                    {format(new Date(project.updated_at), 'yyyy/MM/dd HH:mm', {
                      locale: ja,
                    })}
                  </span>
                </div>
              </div>

              <div className="flex gap-2">
                <Link
                  to={`/interview/${project.project_id}`}
                  className="btn btn-primary flex-1 flex items-center justify-center gap-2 text-sm"
                >
                  インタビュー開始
                  <ExternalLink className="h-4 w-4" />
                </Link>
                <Link
                  to={`/specs/${project.project_id}`}
                  className="btn btn-secondary flex items-center justify-center gap-2 text-sm"
                >
                  仕様書
                </Link>
                <button
                  onClick={() => {
                    if (confirm(`プロジェクト「${project.display_name}」を削除しますか？`)) {
                      deleteMutation.mutate(project.project_id);
                    }
                  }}
                  className="btn btn-danger p-2"
                  disabled={deleteMutation.isPending}
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Project Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
              新規プロジェクト作成
            </h3>
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                  プロジェクト名 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  className="input"
                  placeholder="例: my-webapp"
                  required
                  maxLength={100}
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="btn btn-secondary"
                  disabled={createMutation.isPending}
                >
                  キャンセル
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={createMutation.isPending || !newProjectName.trim()}
                >
                  {createMutation.isPending ? '作成中...' : '作成'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
