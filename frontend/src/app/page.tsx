'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <div className="container">
      <h1 className="title">スライド自動生成ツール</h1>
      <div className="grid-container">
        <Link href="/bulk-generate" style={{ textDecoration: 'none' }}>
          <div className="card bulk">
            <h2>一括スライド生成</h2>
            <p>
              テーマを入力するだけで、プレゼンテーション全体を自動生成します。
              タイトルスライドから内容まで、一括で作成できます。
            </p>
          </div>
        </Link>
        
        <Link href="/one-generate" style={{ textDecoration: 'none' }}>
          <div className="card one">
            <h2>ONEスライド生成</h2>
            <p>
              1枚ずつスライドを生成します。
              より細かな制御と調整が可能です。
              （開発中）
            </p>
          </div>
        </Link>
      </div>
    </div>
  );
}