import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { questionsService } from '../api/questionsService';

// Async thunks for questions
export const fetchQuestions = createAsyncThunk(
  'questions/fetchQuestions',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await questionsService.getQuestions(params);
      return response;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const searchQuestions = createAsyncThunk(
  'questions/searchQuestions',
  async ({ query, filters = {} }, { rejectWithValue }) => {
    try {
      const response = await questionsService.searchWithFilters(query, filters);
      return response;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const fetchQuestionById = createAsyncThunk(
  'questions/fetchQuestionById',
  async (questionId, { rejectWithValue }) => {
    try {
      const response = await questionsService.getQuestionById(questionId);
      return response;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const fetchSimilarQuestions = createAsyncThunk(
  'questions/fetchSimilarQuestions',
  async ({ questionId, limit = 5 }, { rejectWithValue }) => {
    try {
      const response = await questionsService.getSimilarQuestions(questionId, limit);
      return { questionId, similarQuestions: response };
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const fetchRandomQuestions = createAsyncThunk(
  'questions/fetchRandomQuestions',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await questionsService.getRandomQuestions(params);
      return response;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const getSearchSuggestions = createAsyncThunk(
  'questions/getSearchSuggestions',
  async (query, { rejectWithValue }) => {
    try {
      const response = await questionsService.getSearchSuggestions(query);
      return response;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

const questionsSlice = createSlice({
  name: 'questions',
  initialState: {
    questions: [],
    currentQuestion: null,
    searchResults: [],
    randomQuestions: [],
    similarQuestions: {},
    searchSuggestions: [],
    pagination: {
      page: 1,
      totalPages: 1,
      totalItems: 0,
      perPage: 20,
      hasNext: false,
      hasPrevious: false,
    },
    isLoading: false,
    searchLoading: false,
    error: null,
    searchQuery: '',
    filters: {},
    lastUpdated: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setSearchQuery: (state, action) => {
      state.searchQuery = action.payload;
    },
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {};
    },
    clearSearchResults: (state) => {
      state.searchResults = [];
      state.searchQuery = '';
    },
    clearCurrentQuestion: (state) => {
      state.currentQuestion = null;
    },
    updateQuestionInList: (state, action) => {
      const { questionId, updates } = action.payload;
      const questionIndex = state.questions.findIndex(q => q.id === questionId);
      if (questionIndex !== -1) {
        state.questions[questionIndex] = { ...state.questions[questionIndex], ...updates };
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Questions
      .addCase(fetchQuestions.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchQuestions.fulfilled, (state, action) => {
        state.isLoading = false;
        
        if (action.payload.items) {
          // Paginated response
          state.questions = action.payload.items;
          state.pagination = {
            page: action.payload.page || 1,
            totalPages: action.payload.pages || 1,
            totalItems: action.payload.total || 0,
            perPage: action.payload.per_page || 20,
            hasNext: action.payload.has_next || false,
            hasPrevious: action.payload.has_prev || false,
          };
        } else {
          // Direct array response
          state.questions = Array.isArray(action.payload) ? action.payload : [];
        }
        
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchQuestions.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload?.detail || 'Failed to fetch questions';
      })
      
      // Search Questions
      .addCase(searchQuestions.pending, (state) => {
        state.searchLoading = true;
        state.error = null;
      })
      .addCase(searchQuestions.fulfilled, (state, action) => {
        state.searchLoading = false;
        state.searchResults = action.payload.items || action.payload || [];
        if (action.payload.items) {
          state.pagination = {
            page: action.payload.page || 1,
            totalPages: action.payload.pages || 1,
            totalItems: action.payload.total || 0,
            perPage: action.payload.per_page || 20,
            hasNext: action.payload.has_next || false,
            hasPrevious: action.payload.has_prev || false,
          };
        }
      })
      .addCase(searchQuestions.rejected, (state, action) => {
        state.searchLoading = false;
        state.error = action.payload?.detail || 'Search failed';
      })
      
      // Fetch Question by ID
      .addCase(fetchQuestionById.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchQuestionById.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentQuestion = action.payload;
      })
      .addCase(fetchQuestionById.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload?.detail || 'Failed to fetch question';
      })
      
      // Fetch Similar Questions
      .addCase(fetchSimilarQuestions.fulfilled, (state, action) => {
        const { questionId, similarQuestions } = action.payload;
        state.similarQuestions[questionId] = similarQuestions;
      })
      
      // Fetch Random Questions
      .addCase(fetchRandomQuestions.fulfilled, (state, action) => {
        state.randomQuestions = action.payload.items || action.payload || [];
      })
      
      // Search Suggestions
      .addCase(getSearchSuggestions.fulfilled, (state, action) => {
        state.searchSuggestions = action.payload || [];
      });
  },
});

export const {
  clearError,
  setSearchQuery,
  setFilters,
  clearFilters,
  clearSearchResults,
  clearCurrentQuestion,
  updateQuestionInList,
} = questionsSlice.actions;

// Selectors
export const selectQuestions = (state) => state.questions.questions;
export const selectCurrentQuestion = (state) => state.questions.currentQuestion;
export const selectSearchResults = (state) => state.questions.searchResults;
export const selectRandomQuestions = (state) => state.questions.randomQuestions;
export const selectSimilarQuestions = (questionId) => (state) => 
  state.questions.similarQuestions[questionId] || [];
export const selectQuestionsLoading = (state) => state.questions.isLoading;
export const selectSearchLoading = (state) => state.questions.searchLoading;
export const selectQuestionsError = (state) => state.questions.error;
export const selectSearchQuery = (state) => state.questions.searchQuery;
export const selectFilters = (state) => state.questions.filters;
export const selectPagination = (state) => state.questions.pagination;
export const selectSearchSuggestions = (state) => state.questions.searchSuggestions;

export default questionsSlice.reducer; 