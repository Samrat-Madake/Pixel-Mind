import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Search, Users, Share2, Copy, Settings as SettingsIcon } from 'lucide-react';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex h-screen bg-base text-primary overflow-hidden">
        {/* Sidebar */}
        <aside className="w-20 lg:w-64 glass border-r border-glass flex flex-col items-center lg:items-stretch py-6 px-4">
          <div className="flex items-center gap-3 mb-10 px-2">
            <div className="w-10 h-10 bg-accent rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(124,106,245,0.4)]">
              <span className="font-bold text-xl">P</span>
            </div>
            <h1 className="hidden lg:block font-bold text-xl tracking-tight">PixelMind</h1>
          </div>
          
          <nav className="flex-1 space-y-2">
            {[
              { icon: Search, label: 'Search', active: true },
              { icon: Users, label: 'People' },
              { icon: Share2, label: 'Graph' },
              { icon: Copy, label: 'Duplicates' },
            ].map((item) => (
              <button
                key={item.label}
                className={`w-full flex items-center gap-4 p-3 rounded-xl transition-all ${
                  item.active 
                    ? 'bg-accent text-white shadow-lg shadow-accent/20' 
                    : 'text-text-secondary hover:bg-glass'
                }`}
              >
                <item.icon size={22} />
                <span className="hidden lg:block font-medium">{item.label}</span>
              </button>
            ))}
          </nav>
          
          <button className="flex items-center gap-4 p-3 rounded-xl text-text-secondary hover:bg-glass mt-auto">
            <SettingsIcon size={22} />
            <span className="hidden lg:block font-medium">Settings</span>
          </button>
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
          <header className="h-20 border-b border-glass flex items-center justify-between px-8 shrink-0">
            <h2 className="text-2xl font-bold">Search Library</h2>
            <div className="flex items-center gap-4">
               <div className="px-4 py-1.5 bg-glass border border-glass rounded-full text-xs font-medium text-success flex items-center gap-2">
                 <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                 System Online
               </div>
            </div>
          </header>
          
          <div className="flex-1 overflow-y-auto custom-scrollbar p-8">
            <div className="max-w-6xl mx-auto flex flex-col items-center justify-center h-full text-center">
              <div className="w-24 h-24 bg-accent-dim rounded-full flex items-center justify-center mb-6">
                <Search size={40} className="text-accent" />
              </div>
              <h3 className="text-3xl font-bold mb-4">Ready to Explore?</h3>
              <p className="text-text-secondary max-w-md mb-8">
                Drop a folder in settings or use the search bar to find memories using AI-powered semantic search.
              </p>
              <div className="flex gap-4">
                <button className="px-6 py-2.5 bg-accent text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-accent/30 transition-all">
                  Index New Folder
                </button>
                <button className="px-6 py-2.5 bg-glass border border-glass rounded-xl font-semibold hover:bg-glass/10 transition-all">
                  Documentation
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;
