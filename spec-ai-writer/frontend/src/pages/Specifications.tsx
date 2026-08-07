import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Download, Eye, FileText, RotateCcw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import apiClient from '@/api/client';

export default function Specifications() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [selectedPhase, setSelectedPhase] = useState<number | null>(null);

  // Fetch project info for display name
  const { data: projectData } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => apiClient.getProject(projectId!),
    enabled: !!projectId,
  });

  // Fetch specifications list
  const { data: specsData, isLoading } = useQuery({
    queryKey: ['specifications', projectId],
    queryFn: () => apiClient.listSpecifications(projectId!),
    enabled: !!projectId,
  });

  // Fetch selected specification content
  const { data: specContent } = useQuery({
    queryKey: ['specification', projectId, selectedPhase],
    queryFn: () => apiClient.getSpecification(projectId!, selectedPhase!),
    enabled: !!projectId && selectedPhase !== null,
  });

  const handleDownload = async (phaseNum: number, filename: string) => {
    try {
      const blob = await apiClient.downloadSpecification(projectId!, phaseNum);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download failed:', error);
      alert('ダウンロードに失敗しました');
    }
  };

  const handleDownloadAll = async () => {
    try {
      const blob = await apiClient.downloadAllSpecifications(projectId!);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${projectId}_specifications.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download all failed:', error);
      alert('一括ダウンロードに失敗しました');
    }
  };

  const handleReInterview = async (phaseNum: number) => {
    if (!window.confirm(`フェーズ ${phaseNum} のインタビューをリセットして再インタビューを開始しますか？\n既存の回答データと生成済み仕様書は削除されます。`)) {
      return;
    }
    try {
      await apiClient.resetPhase({ project_id: projectId!, phase_num: phaseNum });
      navigate(`/interview/${projectId}?phase=${phaseNum}`);
    } catch (error) {
      console.error('Reset phase failed:', error);
      alert('フェーズのリセットに失敗しました');
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/dashboard" className="btn btn-ghost p-2">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              仕様書: {projectData?.display_name || projectId}
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              生成された仕様書を確認・ダウンロードできます
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Link to={`/interview/${projectId}`} className="btn btn-secondary">
            インタビューへ
          </Link>
          <button onClick={handleDownloadAll} className="btn btn-primary flex items-center gap-2">
            <Download className="h-4 w-4" />
            一括ダウンロード
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="text-center py-12">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
          <p className="mt-2 text-gray-500">読み込み中...</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Specifications List */}
        <div className="lg:col-span-1 space-y-3">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            フェーズ一覧
          </h3>
          {specsData?.specifications.map((spec) => (
            <div
              key={spec.phase_num}
              className={`card p-4 cursor-pointer transition-all ${
                selectedPhase === spec.phase_num
                  ? 'border-2 border-primary-500'
                  : 'hover:border-gray-300'
              } ${!spec.exists ? 'opacity-50' : ''}`}
              onClick={() => spec.exists && setSelectedPhase(spec.phase_num)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-gray-400" />
                    <span className="font-medium text-sm text-gray-900 dark:text-white">
                      Phase {spec.phase_num}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                    {spec.phase_name}
                  </p>
                  {spec.exists && spec.generated_at && (
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(spec.generated_at).toLocaleDateString('ja-JP')}
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-1">
                  {spec.exists && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReInterview(spec.phase_num);
                      }}
                      className="btn btn-secondary p-1"
                      title="再インタビュー"
                      aria-label="再インタビュー"
                    >
                      <RotateCcw className="h-4 w-4" />
                    </button>
                  )}
                  {spec.exists ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDownload(spec.phase_num, spec.filename);
                      }}
                      className="btn btn-secondary p-1"
                      aria-label="ダウンロード"
                    >
                      <Download className="h-4 w-4" />
                    </button>
                  ) : (
                    <span className="badge badge-gray">未生成</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Specification Preview */}
        <div className="lg:col-span-2">
          {selectedPhase === null ? (
            <div className="card text-center py-12">
              <Eye className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">
                左のリストから仕様書を選択してください
              </p>
            </div>
          ) : specContent ? (
            <div className="card">
              <div className="mb-4 flex items-center justify-between border-b border-gray-200 dark:border-gray-700 pb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                    {specContent.phase_name}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {specContent.filename}
                  </p>
                </div>
                <button
                  onClick={() =>
                    handleDownload(specContent.phase_num, specContent.filename)
                  }
                  className="btn btn-primary flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  ダウンロード
                </button>
              </div>

              <div className="markdown-body prose dark:prose-invert max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    a: ({ href, children }) => {
                      if (href) {
                        // Handle relative .md spec links like ./01-principle-definition.md
                        const mdMatch = href.match(/(?:^|\/)(\d{2})-[\w-]+\.md$/);
                        if (mdMatch) {
                          const phaseNum = parseInt(mdMatch[1], 10);
                          return (
                            <button
                              onClick={() => setSelectedPhase(phaseNum)}
                              className="text-primary-500 hover:text-primary-700 underline cursor-pointer bg-transparent border-none p-0 font-[inherit] text-[inherit]"
                            >
                              {children}
                            </button>
                          );
                        }
                      }
                      return (
                        <a href={href} target="_blank" rel="noopener noreferrer">
                          {children}
                        </a>
                      );
                    },
                  }}
                >
                  {specContent.content}
                </ReactMarkdown>
              </div>
            </div>
          ) : (
            <div className="card text-center py-12">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
              <p className="mt-2 text-gray-500">読み込み中...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
