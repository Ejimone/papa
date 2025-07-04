import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { practiceService } from '../api/practiceService';

// Async thunks for practice
export const createPracticeSession = createAsyncThunk(
  'practice/createSession',
  async (sessionConfig, { rejectWithValue }) => {
    try {
      const response = await practiceService.createPracticeSession(sessionConfig);
      return response;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const fetchPracticeSessions = createAsyncThunk(
  'practice/fetchSessions',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await practiceService.getPracticeSessions(params);
      return response;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const fetchPracticeSession = createAsyncThunk(
  'practice/fetchSession',
  async (sessionId, { rejectWithValue }) => {
    try {
      const response = await practiceService.getPracticeSession(sessionId);
      return response;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const submitAttempt = createAsyncThunk(
  'practice/submitAttempt',
  async (attemptData, { rejectWithValue }) => {
    try {
      const response = await practiceService.submitAttempt(attemptData);
      return response;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const completePracticeSession = createAsyncThunk(
  'practice/completeSession',
  async ({ sessionId, sessionData = {} }, { rejectWithValue }) => {
    try {
      const response = await practiceService.completePracticeSession(sessionId, sessionData);
      return response;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const fetchBookmarks = createAsyncThunk(
  'practice/fetchBookmarks',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await practiceService.getBookmarks(params);
      return response;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const toggleBookmark = createAsyncThunk(
  'practice/toggleBookmark',
  async ({ questionId, isBookmarked }, { rejectWithValue }) => {
    try {
      if (isBookmarked) {
        await practiceService.removeBookmark(questionId);
        return { questionId, isBookmarked: false };
      } else {
        await practiceService.bookmarkQuestion(questionId);
        return { questionId, isBookmarked: true };
      }
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const fetchProgress = createAsyncThunk(
  'practice/fetchProgress',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await practiceService.getProgress(params);
      return response;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const fetchProgressSummary = createAsyncThunk(
  'practice/fetchProgressSummary',
  async (_, { rejectWithValue }) => {
    try {
      const response = await practiceService.getProgressSummary();
      return response;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

const practiceSlice = createSlice({
  name: 'practice',
  initialState: {
    currentSession: null,
    sessions: [],
    attempts: [],
    bookmarks: [],
    progress: null,
    progressSummary: null,
    
    // Session state
    sessionQuestions: [],
    currentQuestionIndex: 0,
    sessionStartTime: null,
    sessionTimeElapsed: 0,
    
    // UI state
    isLoading: false,
    sessionLoading: false,
    bookmarksLoading: false,
    error: null,
    
    // Practice settings
    selectedSubject: null,
    selectedDifficulty: 'mixed',
    questionCount: 10,
    timeLimit: null,
    sessionType: 'quick_practice',
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    
    // Session management
    setCurrentSession: (state, action) => {
      state.currentSession = action.payload;
    },
    clearCurrentSession: (state) => {
      state.currentSession = null;
      state.sessionQuestions = [];
      state.currentQuestionIndex = 0;
      state.sessionStartTime = null;
      state.sessionTimeElapsed = 0;
    },
    
    // Question navigation
    setCurrentQuestionIndex: (state, action) => {
      state.currentQuestionIndex = action.payload;
    },
    nextQuestion: (state) => {
      if (state.currentQuestionIndex < state.sessionQuestions.length - 1) {
        state.currentQuestionIndex += 1;
      }
    },
    previousQuestion: (state) => {
      if (state.currentQuestionIndex > 0) {
        state.currentQuestionIndex -= 1;
      }
    },
    
    // Session timing
    startSessionTimer: (state) => {
      state.sessionStartTime = Date.now();
    },
    updateSessionTime: (state, action) => {
      state.sessionTimeElapsed = action.payload;
    },
    
    // Practice settings
    setPracticeSettings: (state, action) => {
      const { subject, difficulty, questionCount, timeLimit, sessionType } = action.payload;
      if (subject !== undefined) state.selectedSubject = subject;
      if (difficulty !== undefined) state.selectedDifficulty = difficulty;
      if (questionCount !== undefined) state.questionCount = questionCount;
      if (timeLimit !== undefined) state.timeLimit = timeLimit;
      if (sessionType !== undefined) state.sessionType = sessionType;
    },
    
    // Attempt tracking
    addAttempt: (state, action) => {
      state.attempts.unshift(action.payload);
    },
    
    // Bookmarks
    updateBookmarkStatus: (state, action) => {
      const { questionId, isBookmarked } = action.payload;
      if (isBookmarked) {
        // Add to bookmarks if not already there
        if (!state.bookmarks.find(b => b.question_id === questionId)) {
          state.bookmarks.push({ question_id: questionId });
        }
      } else {
        // Remove from bookmarks
        state.bookmarks = state.bookmarks.filter(b => b.question_id !== questionId);
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Create Practice Session
      .addCase(createPracticeSession.pending, (state) => {
        state.sessionLoading = true;
        state.error = null;
      })
      .addCase(createPracticeSession.fulfilled, (state, action) => {
        state.sessionLoading = false;
        state.currentSession = action.payload;
        state.sessionQuestions = action.payload.questions || [];
        state.currentQuestionIndex = 0;
        state.sessionStartTime = Date.now();
      })
      .addCase(createPracticeSession.rejected, (state, action) => {
        state.sessionLoading = false;
        state.error = action.payload?.detail || 'Failed to create practice session';
      })
      
      // Fetch Practice Sessions
      .addCase(fetchPracticeSessions.fulfilled, (state, action) => {
        state.sessions = action.payload.items || action.payload || [];
      })
      
      // Fetch Practice Session
      .addCase(fetchPracticeSession.pending, (state) => {
        state.sessionLoading = true;
      })
      .addCase(fetchPracticeSession.fulfilled, (state, action) => {
        state.sessionLoading = false;
        state.currentSession = action.payload;
        state.sessionQuestions = action.payload.questions || [];
      })
      .addCase(fetchPracticeSession.rejected, (state, action) => {
        state.sessionLoading = false;
        state.error = action.payload?.detail || 'Failed to fetch session';
      })
      
      // Submit Attempt
      .addCase(submitAttempt.fulfilled, (state, action) => {
        state.attempts.unshift(action.payload);
      })
      
      // Complete Practice Session
      .addCase(completePracticeSession.fulfilled, (state, action) => {
        if (state.currentSession && state.currentSession.id === action.payload.id) {
          state.currentSession = { ...state.currentSession, ...action.payload };
        }
      })
      
      // Fetch Bookmarks
      .addCase(fetchBookmarks.pending, (state) => {
        state.bookmarksLoading = true;
      })
      .addCase(fetchBookmarks.fulfilled, (state, action) => {
        state.bookmarksLoading = false;
        state.bookmarks = action.payload.items || action.payload || [];
      })
      .addCase(fetchBookmarks.rejected, (state, action) => {
        state.bookmarksLoading = false;
        state.error = action.payload?.detail || 'Failed to fetch bookmarks';
      })
      
      // Toggle Bookmark
      .addCase(toggleBookmark.fulfilled, (state, action) => {
        const { questionId, isBookmarked } = action.payload;
        state.updateBookmarkStatus({ questionId, isBookmarked });
      })
      
      // Fetch Progress
      .addCase(fetchProgress.fulfilled, (state, action) => {
        state.progress = action.payload;
      })
      
      // Fetch Progress Summary
      .addCase(fetchProgressSummary.fulfilled, (state, action) => {
        state.progressSummary = action.payload;
      });
  },
});

export const {
  clearError,
  setCurrentSession,
  clearCurrentSession,
  setCurrentQuestionIndex,
  nextQuestion,
  previousQuestion,
  startSessionTimer,
  updateSessionTime,
  setPracticeSettings,
  addAttempt,
  updateBookmarkStatus,
} = practiceSlice.actions;

// Selectors
export const selectCurrentSession = (state) => state.practice.currentSession;
export const selectSessions = (state) => state.practice.sessions;
export const selectSessionQuestions = (state) => state.practice.sessionQuestions;
export const selectCurrentQuestion = (state) => {
  const { sessionQuestions, currentQuestionIndex } = state.practice;
  return sessionQuestions[currentQuestionIndex] || null;
};
export const selectCurrentQuestionIndex = (state) => state.practice.currentQuestionIndex;
export const selectSessionProgress = (state) => {
  const { sessionQuestions, currentQuestionIndex } = state.practice;
  return {
    current: currentQuestionIndex + 1,
    total: sessionQuestions.length,
    percentage: sessionQuestions.length > 0 ? ((currentQuestionIndex + 1) / sessionQuestions.length) * 100 : 0
  };
};
export const selectBookmarks = (state) => state.practice.bookmarks;
export const selectProgress = (state) => state.practice.progress;
export const selectProgressSummary = (state) => state.practice.progressSummary;
export const selectPracticeLoading = (state) => state.practice.isLoading;
export const selectSessionLoading = (state) => state.practice.sessionLoading;
export const selectBookmarksLoading = (state) => state.practice.bookmarksLoading;
export const selectPracticeError = (state) => state.practice.error;
export const selectPracticeSettings = (state) => ({
  selectedSubject: state.practice.selectedSubject,
  selectedDifficulty: state.practice.selectedDifficulty,
  questionCount: state.practice.questionCount,
  timeLimit: state.practice.timeLimit,
  sessionType: state.practice.sessionType,
});
export const selectSessionTime = (state) => ({
  startTime: state.practice.sessionStartTime,
  elapsed: state.practice.sessionTimeElapsed,
});

export default practiceSlice.reducer; 