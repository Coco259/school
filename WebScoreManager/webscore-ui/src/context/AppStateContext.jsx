import { createContext, useReducer, useContext } from 'react';

const AppStateContext = createContext(null);

const initialState = {
  students: [],
  courses: [],
  scores: [],
  loading: false,
  error: null
};

function reducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_STUDENTS':
      return { ...state, students: action.payload, loading: false };
    case 'SET_COURSES':
      return { ...state, courses: action.payload, loading: false };
    case 'SET_SCORES':
      return { ...state, scores: action.payload, loading: false };
    default:
      return state;
  }
}

export function AppStateProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <AppStateContext.Provider value={{ state, dispatch }}>
      {children}
    </AppStateContext.Provider>
  );
}

export function useAppState() {
  const value = useContext(AppStateContext);
  if (!value) {
    throw new Error('useAppState must be used within AppStateProvider');
  }
  return value;
}
