'use client';

import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '@/store/store';
import {
  setTheme,
  setLoading,
  setMessage,
  setSlides,
  setGeneratedFileName,
} from '@/store/presentationSlice';

export default function OneGenerate() {
  const dispatch = useDispatch();
  const {
    theme,
    isLoading,
    message,
    slides,
    generatedFileName
  } = useSelector((state: RootState) => state.presentation);

  const handleGenerateOne = async () => {
    dispatch(setLoading(true));
    dispatch(setMessage('スライドを生成中です... しばらくお待ちください。'));

    try {
      const payload = {
        theme,
        slideCount: 1, // 1枚のみ生成
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
      // 既存のスライドに新しいスライドを追加
      const newSlides = [...slides, ...result.data.slides];
      dispatch(setSlides(newSlides));
      dispatch(setGeneratedFileName(result.pptxFile));
      dispatch(setMessage('✅ スライドが正常に生成されました。'));

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

  const handleClearSlides = () => {
    dispatch(setSlides([]));
    dispatch(setGeneratedFileName(null));
    dispatch(setMessage(''));
  };

  return (
    <div className="container">
      <h1 className="title">ONEスライド生成</h1>
      <p>1枚ずつスライドを生成して、プレゼンテーションを組み立てます。</p>

      <div className="form-group">
        <label htmlFor="theme" className="form-label">
          スライドのテーマ:
        </label>
        <input
          id="theme"
          type="text"
          value={theme}
          onChange={(e) => dispatch(setTheme(e.target.value))}
          placeholder="例: AIを活用した業務効率化のポイント"
          className="form-input"
        />
      </div>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button
          onClick={handleGenerateOne}
          disabled={isLoading || !theme}
          className="form-button"
        >
          {isLoading ? '生成中...' : '新しいスライドを追加'}
        </button>

        {slides.length > 0 && (
          <button
            onClick={handleClearSlides}
            disabled={isLoading}
            className="form-button"
            style={{ backgroundColor: '#dc3545' }}
          >
            クリア
          </button>
        )}
      </div>

      {message && <p className="message">{message}</p>}

      {slides.length > 0 && (
        <div className="slides-container">
          <div className="slides-header">
            <h2>生成されたスライド ({slides.length}枚)</h2>
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