'use client';

import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch } from '@/store/store';
import { register, selectAuthError, selectAuthLoading } from '@/store/authSlice';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useRouter } from 'next/navigation';

export default function RegisterPage() {
  const dispatch = useDispatch<AppDispatch>();
  const router = useRouter();
  const error = useSelector(selectAuthError);
  const loading = useSelector(selectAuthLoading);

  const [credentials, setCredentials] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (credentials.password !== credentials.confirmPassword) {
      // パスワードの不一致エラーは、バックエンドに送信せずにフロントエンドで処理
      return;
    }

    try {
      await dispatch(register({
        email: credentials.email,
        username: credentials.username,
        password: credentials.password,
      })).unwrap();
      router.push('/');  // 登録成功時にホームページにリダイレクト
    } catch {
      // エラーはReduxのstateで処理されます
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Typography component="h1" variant="h5">
          アカウント登録
        </Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {credentials.password !== credentials.confirmPassword && (
            <Alert severity="error" sx={{ mb: 2 }}>パスワードが一致しません</Alert>
          )}
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="メールアドレス"
            name="email"
            autoComplete="email"
            autoFocus
            value={credentials.email}
            onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="username"
            label="ユーザー名"
            name="username"
            autoComplete="username"
            value={credentials.username}
            onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="パスワード"
            type="password"
            id="password"
            autoComplete="new-password"
            value={credentials.password}
            onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="confirmPassword"
            label="パスワード（確認）"
            type="password"
            id="confirm-password"
            autoComplete="new-password"
            value={credentials.confirmPassword}
            onChange={(e) => setCredentials({ ...credentials, confirmPassword: e.target.value })}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading || credentials.password !== credentials.confirmPassword}
          >
            {loading ? <CircularProgress size={24} /> : 'アカウント登録'}
          </Button>
        </Box>
      </Box>
    </Container>
  );
}