'use client';

import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from '@/store/store';
import {
  setTheme,
  setSlideCount,
  clearError,
  generateSlides,
  downloadPresentation,
  selectError,
  selectIsLoading,
} from '@/store/presentationSlice';
import { useRequireAuth } from '@/hooks/useRequireAuth';

export default function BulkGenerate() {
  const dispatch = useDispatch<AppDispatch>();
  const {
    theme,
    slideCount,
    slides,
    generatedFileName
  } = useSelector((state: RootState) => state.presentation);
  const error = useSelector(selectError);
  const isLoading = useSelector(selectIsLoading);

  // 認証状態を確認
  useRequireAuth();

  // エラーメッセージをクリア
  useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  const handleGenerate = async () => {
    try {
      await dispatch(generateSlides({ theme, slideCount })).unwrap();
    } catch {
      // エラーはReduxのstateで処理されます
    }
  };

  const handleDownload = async () => {
    if (generatedFileName) {
      try {
        const blob = await dispatch(downloadPresentation(generatedFileName)).unwrap();
        const url = window.URL.createObjectURL(blob);
        const downloadLink = document.createElement('a');
        downloadLink.href = url;
        downloadLink.download = generatedFileName;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        window.URL.revokeObjectURL(url);
      } catch {
        // エラーはReduxのstateで処理されます
      }
    }
  };

  return (
    <div className="container">
      <h1 className="title">一括スライド生成</h1>
      <p>プレゼンのテーマと枚数を入力して、スライドを自動で作成します。</p>

      <div className="form-group">
        <label htmlFor="theme" className="form-label">
          プレゼンのテーマ:
        </label>
        <input
          id="theme"
          type="text"
          value={theme}
          onChange={(e) => dispatch(setTheme(e.target.value))}
          placeholder="例: AIを活用した業務効率化"
          className="form-input"
        />
      </div>

      <div className="form-group">
        <label htmlFor="slide-count" className="form-label">
          スライド枚数:
        </label>
        <input
          id="slide-count"
          type="number"
          value={slideCount}
          onChange={(e) => dispatch(setSlideCount(Number(e.target.value)))}
          min="1"
          className="form-input"
        />
      </div>

      <button
        onClick={handleGenerate}
        disabled={isLoading || !theme}
        className="form-button"
      >
        {isLoading ? '生成中...' : 'スライドを生成'}
      </button>

      {error && <p className="error message">{error}</p>}

      {slides.length > 0 && (
        <div className="slides-container">
          <div className="slides-header">
            <h2>生成されたスライド</h2>
            {generatedFileName && (
              <button onClick={handleDownload} className="export-button">
                <svg 
                  width="16" 
                  height="16" 
                  viewBox="0 0 16 16" 
                  fill="none" 
                  xmlns="http://www.w3.org/2000/svg"
                  className="download-icon"
                >
                  <path 
                    d="M8 12L3 7h3V1h4v6h3L8 12z M3 14v-2h10v2H3z" 
                    fill="currentColor"
                  />
                </svg>
                PowerPointでエクスポート
              </button>
            )}
          </div>
          {slides.map((slide, index) => (
            <div key={index} className="slide-card">
              <h3 className="slide-title">
                {index + 1}. {slide.title}
              </h3>
              <ul className="slide-content">
                {slide.content.map((item, itemIndex) => (
                  <li key={itemIndex}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}