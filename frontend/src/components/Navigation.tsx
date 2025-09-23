'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useSelector, useDispatch } from 'react-redux';
import { selectIsAuthenticated, logout } from '@/store/authSlice';

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const dispatch = useDispatch();
  const isAuthenticated = useSelector(selectIsAuthenticated);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const handleLogout = () => {
    dispatch(logout());
    router.push('/login');
    setIsOpen(false);
  };

  const menuItems = [
    { path: '/', label: 'ホーム' },
    { path: '/bulk-generate', label: '一括スライド生成' },
    { path: '/one-generate', label: 'ONEスライド生成' },
    ...(isAuthenticated
      ? [{ label: 'ログアウト', onClick: handleLogout }]
      : [
          { path: '/login', label: 'ログイン' },
          { path: '/register', label: 'アカウント登録' },
        ]
    ),
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
        {menuItems.map((item) =>
          item.onClick ? (
            <button
              key={item.label}
              className="menu-item"
              onClick={item.onClick}
            >
              {item.label}
            </button>
          ) : (
            <Link
              key={item.path}
              href={item.path!}
              className={`menu-item ${pathname === item.path ? 'active' : ''}`}
              onClick={toggleMenu}
            >
              {item.label}
            </Link>
          )
        )}
      </div>
    </nav>
  );
}