import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

// 产品
export const getProducts = (params) => api.get('/products', { params });
export const getProduct = (id) => api.get(`/products/${id}`);

// 成分
export const getIngredients = (params) => api.get('/ingredients', { params });
export const getIngredient = (id) => api.get(`/ingredients/${id}`);

// 品种
export const getBreeds = (params) => api.get('/breeds', { params });
export const getBreed = (id) => api.get(`/breeds/${id}`);
export const getBreedProducts = (id) => api.get(`/breeds/${id}/products`);

// 品牌
export const getBrands = (params) => api.get('/brands', { params });

// 品类
export const getCategories = (params) => api.get('/categories', { params });

export default api;
