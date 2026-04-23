import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
});

export const api = {
  // --- Search & Timeline ---
  search: async (query = '', filters = {}) => {
    const params = { q: query, ...filters };
    const response = await client.get('/search/', { params });
    return response.data;
  },

  // --- People ---
  getPeople: async () => {
    const response = await client.get('/people/');
    return response.data;
  },
  getPersonImages: async (clusterId) => {
    const response = await client.get(`/people/${clusterId}/images`);
    return response.data;
  },
  removePersonImage: async (clusterId, imageId) => {
    const response = await client.delete(`/people/${clusterId}/images/${imageId}`);
    return response.data;
  },
  deletePerson: async (clusterId) => {
    const response = await client.delete(`/people/${clusterId}`);
    return response.data;
  },
  labelPerson: async (clusterId, label) => {
    const response = await client.post('/people/label-cluster', { cluster_id: clusterId, label });
    return response.data;
  },
  mergePeople: async (clusterIds, targetLabel = null) => {
    const response = await client.post('/people/merge-clusters', { cluster_ids: clusterIds, target_label: targetLabel });
    return response.data;
  },

  // --- Graph ---
  getGraph: async () => {
    const response = await client.get('/graph/');
    return response.data;
  },
  getPersonGraph: async (clusterId) => {
    const response = await client.get(`/graph/${clusterId}`);
    return response.data;
  },

  // --- Duplicates ---
  getDuplicates: async () => {
    const response = await client.get('/duplicates/');
    return response.data;
  },
  deleteDuplicate: async (imageId) => {
    const response = await client.post('/duplicates/delete', { image_id: imageId });
    return response.data;
  },

  // --- Things ---
  getThings: async () => {
    const response = await client.get('/things/');
    return response.data;
  },
  getThingImages: async (category) => {
    const response = await client.get(`/things/${category}`);
    return response.data;
  },

  // --- Indexing ---
  startIndexing: async (directoryPath) => {
    const response = await client.post('/index/', { folder_path: directoryPath });
    return response.data;
  },
  getIndexProgress: async () => {
    const response = await client.get('/index/status');
    return response.data;
  },

  // Helper for generating image URLs
  getThumbnailUrl: (imageId) => `${API_BASE_URL}/images/thumbnail/${imageId}`,
  getFullImageUrl: (imageId) => `${API_BASE_URL}/images/full/${imageId}`,
};

export default client;
