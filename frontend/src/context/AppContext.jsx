import { createContext, useContext, useReducer, useEffect } from 'react'
import { api, getToken } from '../api/client'

const AppContext = createContext()

let savedHistory = []
try {
  const raw = localStorage.getItem('petcare_history')
  if (raw) savedHistory = JSON.parse(raw)
} catch {}

const initialState = {
  user: null,
  searchQuery: '',
  searchHistory: Array.isArray(savedHistory) ? savedHistory : [],
  favorites: [],
}

function reducer(state, action) {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload }
    case 'LOGOUT':
      localStorage.removeItem('petcare_token')
      return { ...state, user: null, favorites: [] }
    case 'SET_SEARCH':
      return { ...state, searchQuery: action.payload }
    case 'ADD_HISTORY':
      const history = [action.payload, ...state.searchHistory.filter(h => h !== action.payload)].slice(0, 10)
      localStorage.setItem('petcare_history', JSON.stringify(history))
      return { ...state, searchHistory: history }
    case 'SET_FAVORITES':
      return { ...state, favorites: action.payload }
    case 'ADD_FAVORITE':
      return { ...state, favorites: [...state.favorites, action.payload] }
    case 'REMOVE_FAVORITE':
      return { ...state, favorites: state.favorites.filter(f => f !== action.payload) }
    case 'CLEAR_HISTORY':
      localStorage.removeItem('petcare_history')
      return { ...state, searchHistory: [] }
    default:
      return state
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState)

  // 启动时检查登录状态
  useEffect(() => {
    if (getToken()) {
      api.getMe().then(user => {
        dispatch({ type: 'SET_USER', payload: user })
        api.getFavorites().then(data => {
          dispatch({ type: 'SET_FAVORITES', payload: (data.items || []).map(f => f.id) })
        }).catch(() => {})
      }).catch(() => {
        localStorage.removeItem('petcare_token')
      })
    }
  }, [])

  return <AppContext.Provider value={{ state, dispatch }}>{children}</AppContext.Provider>
}

export function useApp() {
  return useContext(AppContext)
}
