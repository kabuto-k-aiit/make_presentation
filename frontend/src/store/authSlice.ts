import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import { RootState } from './store';

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: {
    username: string | null;
    email: string | null;
  } | null;
  isAuthenticated: boolean;
  error: string | null;
  loading: boolean;
}

const getFromLocalStorage = (key: string): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(key);
  }
  return null;
};

const setToLocalStorage = (key: string, value: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(key, value);
  }
};

const removeFromLocalStorage = (key: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(key);
  }
};

const initialState: AuthState = {
  token: getFromLocalStorage('token'),
  refreshToken: getFromLocalStorage('refreshToken'),
  user: null,
  isAuthenticated: !!getFromLocalStorage('token'),
  error: null,
  loading: false,
};

// 認証関連のAPI呼び出し
export const register = createAsyncThunk(
  'auth/register',
  async (credentials: { email: string; username: string; password: string }) => {
    const response = await fetch('http://localhost:8000/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    const data = await response.json();
    return data;
  }
);

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: { username: string; password: string }) => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch('http://localhost:8000/token', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    return data;
  }
);

export const refreshToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { getState }) => {
    const state = getState() as RootState;
    const currentRefreshToken = state.auth.refreshToken;

    if (!currentRefreshToken) {
      throw new Error('リフレッシュトークンが存在しません');
    }

    const response = await fetch('http://localhost:8000/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ current_token: currentRefreshToken }),
    });

    if (!response.ok) {
      if (response.status === 401) {
        // リフレッシュトークンが無効な場合はログアウト
        throw new Error('セッションの有効期限が切れました');
      }
      const error = await response.json();
      throw new Error(error.detail || 'トークンの更新に失敗しました');
    }

    const data = await response.json();
    return data;
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.token = null;
      state.user = null;
      state.isAuthenticated = false;
      // ログアウト時にローカルストレージからトークンを削除
      removeFromLocalStorage('token');
    },
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
      state.isAuthenticated = true;
      // トークンをローカルストレージに保存
      setToLocalStorage('token', action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      // Register
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.isAuthenticated = true;
        setToLocalStorage('token', action.payload.access_token);
        setToLocalStorage('refreshToken', action.payload.refresh_token);
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Registration failed';
      })
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.isAuthenticated = true;
        setToLocalStorage('token', action.payload.access_token);
        setToLocalStorage('refreshToken', action.payload.refresh_token);
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Login failed';
      })
      // RefreshToken
      .addCase(refreshToken.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.isAuthenticated = true;
        setToLocalStorage('token', action.payload.access_token);
        setToLocalStorage('refreshToken', action.payload.refresh_token);
      })
      .addCase(refreshToken.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Token refresh failed';
        if (action.error.message?.includes('セッションの有効期限')) {
          // セッション期限切れの場合はログアウト
          state.token = null;
          state.refreshToken = null;
          state.isAuthenticated = false;
          removeFromLocalStorage('token');
          removeFromLocalStorage('refreshToken');
        }
      });
  },
});

export const { logout, setToken } = authSlice.actions;

export const selectAuth = (state: RootState) => state.auth;
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated;
export const selectAuthError = (state: RootState) => state.auth.error;
export const selectAuthLoading = (state: RootState) => state.auth.loading;

export default authSlice.reducer;