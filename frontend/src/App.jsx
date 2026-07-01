import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Search from './pages/Search'
import ProductDetail from './pages/ProductDetail'
import IngredientDetail from './pages/IngredientDetail'
import BreedList from './pages/BreedList'
import BreedDetail from './pages/BreedDetail'
import Profile from './pages/Profile'
import HealthTracker from './pages/HealthTracker'
import PetProfiles from './pages/PetProfiles'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<Search />} />
        <Route path="/product/:id" element={<ProductDetail />} />
        <Route path="/ingredient/:id" element={<IngredientDetail />} />
        <Route path="/breeds" element={<BreedList />} />
        <Route path="/breed/:id" element={<BreedDetail />} />
        <Route path="/compare" element={<Navigate to="/search" replace />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/pets" element={<PetProfiles />} />
        <Route path="/health" element={<HealthTracker />} />
      </Route>
    </Routes>
  )
}
