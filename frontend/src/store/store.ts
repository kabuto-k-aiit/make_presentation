import { configureStore } from '@reduxjs/toolkit';
import presentationReducer from './presentationSlice';
import authReducer from './authSlice';

export const store = configureStore({
  reducer: {
    presentation: presentationReducer,
    auth: authReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;