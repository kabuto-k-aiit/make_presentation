'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const menuItems = [
    { path: '/', label: 'ホーム' },
    { path: '/bulk-generate', label: '一括スライド生成' },
    { path: '/one-generate', label: 'ONEスライド生成' },
  ];

  return (
    <nav className="navigation">
      <button
        className={`hamburger ${isOpen ? 'active' : ''}`}
        onClick={toggleMenu}
        aria-label="メニュー"
      >
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
      </button>

      <div className={`menu-overlay ${isOpen ? 'active' : ''}`} onClick={toggleMenu}></div>

      <div className={`menu ${isOpen ? 'active' : ''}`}>
        {menuItems.map((item) => (
          <Link
            key={item.path}
            href={item.path}
            className={`menu-item ${pathname === item.path ? 'active' : ''}`}
            onClick={toggleMenu}
          >
            {item.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}