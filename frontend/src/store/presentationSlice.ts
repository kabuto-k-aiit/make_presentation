import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Slide {
  title: string;
  content: string[];
}

interface PresentationState {
  theme: string;
  slideCount: number;
  isLoading: boolean;
  message: string;
  slides: Slide[];
  generatedFileName: string | null;
}

const initialState: PresentationState = {
  theme: '',
  slideCount: 5,
  isLoading: false,
  message: '',
  slides: [],
  generatedFileName: null,
};

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
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setMessage: (state, action: PayloadAction<string>) => {
      state.message = action.payload;
    },
    setSlides: (state, action: PayloadAction<Slide[]>) => {
      state.slides = action.payload;
    },
    setGeneratedFileName: (state, action: PayloadAction<string | null>) => {
      state.generatedFileName = action.payload;
    },
  },
});

export const {
  setTheme,
  setSlideCount,
  setLoading,
  setMessage,
  setSlides,
  setGeneratedFileName,
} = presentationSlice.actions;

export default presentationSlice.reducer;