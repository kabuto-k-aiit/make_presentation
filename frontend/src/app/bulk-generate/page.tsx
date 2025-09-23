'use client';

import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '@/store/store';
import {
  setTheme,
  setSlideCount,
  setLoading,
  setMessage,
  setSlides,
  setGeneratedFileName,
} from '@/store/presentationSlice';

export default function BulkGenerate() {
  const dispatch = useDispatch();
  const {
    theme,
    slideCount,
    isLoading,
    message,
    slides,
    generatedFileName
  } = useSelector((state: RootState) => state.presentation);

  const handleGenerate = async () => {
    dispatch(setLoading(true));
    dispatch(setMessage('スライドを生成中です... しばらくお待ちください。'));

    try {
      const payload = {
        theme,
        slideCount,
      };

      const response = await fetch('http://localhost:8000/generate-slides', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('API呼び出しに失敗しました。');
      }

      const result = await response.json();
      dispatch(setSlides(result.data.slides));
      dispatch(setGeneratedFileName(result.pptxFile));
      dispatch(setMessage('✅ スライドのデータが正常に生成されました。'));

    } catch (error: any) {
      dispatch(setMessage(`❌ スライドの生成中にエラーが発生しました: ${error.message}`));
    } finally {
      dispatch(setLoading(false));
    }
  };

  const handleDownload = () => {
    if (generatedFileName) {
      const filename = generatedFileName.split('/').pop();
      const downloadUrl = `http://localhost:8000/download/${filename}`;
      const downloadLink = document.createElement('a');
      downloadLink.href = downloadUrl;
      downloadLink.download = filename || 'presentation.pptx';
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
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

      {message && <p className="message">{message}</p>}

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