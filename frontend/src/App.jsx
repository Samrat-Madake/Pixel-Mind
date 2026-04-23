import React from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import MainLayout from './layouts/MainLayout';
import TimelinePage from './pages/TimelinePage';
import SearchPage from './pages/SearchPage';
import PeoplePage from './pages/PeoplePage';
import PersonDetailPage from './pages/PersonDetailPage';
import ThingsPage from './pages/ThingsPage';
import ThingDetailPage from './pages/ThingDetailPage';
import AlbumsPage from './pages/AlbumsPage';
import DocumentsPage from './pages/DocumentsPage';
import GraphPage from './pages/GraphPage';
import DuplicatesPage from './pages/DuplicatesPage';
import SettingsPage from './pages/SettingsPage';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <HashRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<TimelinePage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="people" element={<PeoplePage />} />
            <Route path="people/:id" element={<PersonDetailPage />} />
            <Route path="things" element={<ThingsPage />} />
            <Route path="things/:id" element={<ThingDetailPage />} />
            <Route path="albums" element={<AlbumsPage />} />
            <Route path="documents" element={<DocumentsPage />} />
            <Route path="graph" element={<GraphPage />} />
            <Route path="duplicates" element={<DuplicatesPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="*" element={<div style={{ padding: 20 }}>Page Not Found</div>} />
          </Route>
        </Routes>
      </HashRouter>
    </QueryClientProvider>
  );
}

export default App;
