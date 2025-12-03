import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('connecting')
  const [messages, setMessages] = useState<any[]>([])
  const [messageCount, setMessageCount] = useState(0)

  useEffect(() => {
    // WebSocket connection logic will be built in Phase 1
    setConnectionStatus('connected')
  }, [])

  return (
    <div className="min-h-screen bg-slate-900">
      <header className="bg-slate-800 border-b border-slate-700 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white">Azerate Live Log</h1>
            <p className="text-slate-400 text-sm">Real-time message stream</p>
          </div>
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-3 py-2 rounded ${connectionStatus === 'connected' ? 'bg-green-900' : 'bg-yellow-900'}`}>
              <div className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-green-400' : 'bg-yellow-400'}`}></div>
              <span className="text-sm font-medium text-white capitalize">{connectionStatus}</span>
            </div>
            <div className="text-slate-400">
              <span className="text-sm">Messages: <span className="font-bold text-white">{messageCount}</span></span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-80px)]">
        <aside className="w-64 bg-slate-800 border-r border-slate-700 p-4">
          <div className="space-y-4">
            <div>
              <h2 className="text-sm font-semibold text-white mb-2">Filters</h2>
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-slate-300 text-sm cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded" />
                  All Messages
                </label>
              </div>
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white mb-2">Search</h2>
              <input
                type="text"
                placeholder="Search messages..."
                className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </aside>

        <main className="flex-1 bg-slate-900 overflow-auto">
          <div className="p-6">
            <div className="text-center text-slate-400 py-12">
              <p className="text-lg">Waiting for messages...</p>
              <p className="text-sm mt-2">WebSocket connection is {connectionStatus === 'connected' ? 'active' : 'inactive'}</p>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
