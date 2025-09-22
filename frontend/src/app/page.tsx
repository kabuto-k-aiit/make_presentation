'use client'; // このコンポーネントをクライアントコンポーネントとして指定

import { useState } from 'react';

export default function Home() {
  const [theme, setTheme] = useState('');
  const [slideCount, setSlideCount] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [slides, setSlides] = useState<{ title: string; content: string[] }[]>([]);

  const handleGenerate = async () => {
    setIsLoading(true);
    setMessage('スライドを生成中です... しばらくお待ちください。');

    try {
        const payload = {
            theme: theme,
            slideCount: slideCount,
        };

        // FastAPIのAPIエンドポイントを呼び出す
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
        console.log(result.data); // 生成されたデータを確認
        setSlides(result.data.slides);
        setMessage('✅ スライドのデータが正常に生成されました。');
        
        // PowerPointファイルのダウンロードリンクを作成
        if (result.pptxFile) {
          // ファイル名だけを取得（パスを除去）
          const filename = result.pptxFile.split('/').pop();
          const downloadUrl = `http://localhost:8000/download/${filename}`;
          console.log('Downloading from:', downloadUrl); // デバッグ用
          const downloadLink = document.createElement('a');
          downloadLink.href = downloadUrl;
          downloadLink.download = filename || 'presentation.pptx';
          document.body.appendChild(downloadLink);
          downloadLink.click();
          document.body.removeChild(downloadLink);
        }

    } catch (error: any) {
        setMessage(`❌ スライドの生成中にエラーが発生しました: ${error.message}`);
    } finally {
        setIsLoading(false);
    }
};

  return (
    <div
      style={{
        fontFamily: 'sans-serif',
        maxWidth: '600px',
        margin: '40px auto',
        padding: '20px',
        border: '1px solid #ccc',
        borderRadius: '8px',
        boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
      }}
    >
      <h1>スライド自動生成ツール</h1>
      <p>プレゼンのテーマと枚数を入力して、スライドを自動で作成します。</p>

      <div style={{ marginBottom: '15px' }}>
        <label htmlFor="theme" style={{ display: 'block', marginBottom: '5px' }}>
          プレゼンのテーマ:
        </label>
        <input
          id="theme"
          type="text"
          value={theme}
          onChange={(e) => setTheme(e.target.value)}
          placeholder="例: AIを活用した業務効率化"
          style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
        />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="slide-count" style={{ display: 'block', marginBottom: '5px' }}>
          スライド枚数:
        </label>
        <input
          id="slide-count"
          type="number"
          value={slideCount}
          onChange={(e) => setSlideCount(Number(e.target.value))}
          min="1"
          style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
        />
      </div>

      <button
        onClick={handleGenerate}
        disabled={isLoading || !theme}
        style={{
          width: '100%',
          padding: '10px',
          fontSize: '16px',
          backgroundColor: isLoading ? '#ccc' : '#007BFF',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: isLoading ? 'not-allowed' : 'pointer',
        }}
      >
        {isLoading ? '生成中...' : 'スライドを生成'}
      </button>

      {message && <p style={{ marginTop: '20px', textAlign: 'center' }}>{message}</p>}

      {slides.length > 0 && (
        <div style={{ marginTop: '30px' }}>
          <h2>生成されたスライド</h2>
          {slides.map((slide, index) => (
            <div
              key={index}
              style={{
                marginBottom: '30px',
                padding: '20px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                backgroundColor: '#f9f9f9',
              }}
            >
              <h3 style={{ 
                marginTop: '0',
                marginBottom: '15px',
                color: '#333',
                borderBottom: '2px solid #007BFF',
                paddingBottom: '8px'
              }}>
                {index + 1}. {slide.title}
              </h3>
              <ul style={{ 
                margin: '0',
                paddingLeft: '20px',
                listStyleType: 'disc'
              }}>
                {slide.content.map((item, itemIndex) => (
                  <li key={itemIndex} style={{ marginBottom: '8px' }}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}