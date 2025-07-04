import { configureStore } from '@reduxjs/toolkit';

// Import reducers
import authReducer from './authSlice';
import questionsReducer from './questionsSlice';
import practiceReducer from './practiceSlice';

// Configure store
export const store = configureStore({
  reducer: {
    auth: authReducer,
    questions: questionsReducer,
    practice: practiceReducer,
  },
  devTools: process.env.NODE_ENV !== 'production',
});

// Export store as default
export default store;
