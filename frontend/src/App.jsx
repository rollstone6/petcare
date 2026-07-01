import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import { SkeletonList } from './components/Skeleton'

// 路由级代码分割
const Home = lazy(() => import('./pages/Home'))
const Search = lazy(() => import('./pages/Search'))
const ProductDetail = lazy(() => import('./pages/ProductDetail'))
const IngredientDetail = lazy(() => import('./pages/IngredientDetail'))
const BreedList = lazy(() => import('./pages/BreedList'))
const BreedDetail = lazy(() => import('./pages/BreedDetail'))
const Profile = lazy(() => import('./pages/Profile'))
const HealthTracker = lazy(() => import('./pages/HealthTracker'))
const PetProfiles = lazy(() => import('./pages/PetProfiles'))

export default function App() {
  return (
    <Suspense fallback={<div className="p-4"><SkeletonList count={3} /></div>}>
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
    </Suspense>
  )
}
