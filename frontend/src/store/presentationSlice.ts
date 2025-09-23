import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from './store';

interface Slide {
  title: string;
  content: string[];
}

interface PresentationState {
  theme: string;
  slideCount: number;
  isLoading: boolean;
  message: string;
  error: string | null;
  slides: Slide[];
  generatedFileName: string | null;
}

const initialState: PresentationState = {
  theme: '',
  slideCount: 5,
  isLoading: false,
  message: '',
  error: null,
  slides: [],
  generatedFileName: null,
};

// 非同期アクション
export const generateSlides = createAsyncThunk(
  'presentation/generateSlides',
  async (request: { theme: string; slideCount: number }, { getState }) => {
    const state = getState() as RootState;
    const token = state.auth.token;

    if (!token) {
      throw new Error('認証が必要です。ログインしてください。');
    }

    const response = await fetch('http://localhost:8000/generate-slides', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('セッションの有効期限が切れました。再度ログインしてください。');
      }
      const error = await response.json();
      throw new Error(error.detail || '処理に失敗しました');
    }

    return await response.json();
  }
);

export const downloadPresentation = createAsyncThunk(
  'presentation/downloadPresentation',
  async (filename: string, { getState }) => {
    const state = getState() as RootState;
    const token = state.auth.token;

    if (!token) {
      throw new Error('認証が必要です。ログインしてください。');
    }

    const response = await fetch(`http://localhost:8000/download/${filename}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('セッションの有効期限が切れました。再度ログインしてください。');
      }
      throw new Error('ダウンロードに失敗しました');
    }

    return response.blob();
  }
);

export const presentationSlice = createSlice({
  name: 'presentation',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<string>) => {
      state.theme = action.payload;
    },
    setSlideCount: (state, action: PayloadAction<number>) => {
      state.slideCount = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // generateSlides
      .addCase(generateSlides.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(generateSlides.fulfilled, (state, action) => {
        state.isLoading = false;
        state.slides = action.payload.data.slides;
        state.generatedFileName = action.payload.pptxFile;
        state.message = action.payload.message;
      })
      .addCase(generateSlides.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || '処理に失敗しました';
      })
      // downloadPresentation
      .addCase(downloadPresentation.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(downloadPresentation.fulfilled, (state) => {
        state.isLoading = false;
      })
      .addCase(downloadPresentation.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'ダウンロードに失敗しました';
      });
  },
});

export const {
  setTheme,
  setSlideCount,
  clearError,
} = presentationSlice.actions;

export const selectPresentation = (state: RootState) => state.presentation;
export const selectIsLoading = (state: RootState) => state.presentation.isLoading;
export const selectError = (state: RootState) => state.presentation.error;

export default presentationSlice.reducer;