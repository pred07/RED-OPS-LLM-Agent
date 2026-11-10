'use client';

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  Shield, 
  Terminal, 
  Cpu, 
  Target, 
  Lock, 
  User, 
  Zap, 
  Send, 
  Skull,
  Activity,
  CheckSquare,
  Server,
  Network,
  Copy,
  Flame,
  History,
  LayoutGrid
} from 'lucide-react';
import { Target as TargetType, ChatMessage } from '../types';

const API_BASE = 'http://localhost:8000/api';

export default function WarRoom() {
  const [targets, setTargets] = useState<Record<string, TargetType>>({});
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [selectedIP, setSelectedIP] = useState<string | null>(null);
  
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const isAutoScrollEnabled = useRef(true);

  const handleScroll = () => {
    if (!chatContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current;
    isAutoScrollEnabled.current = scrollHeight - scrollTop - clientHeight < 50;
  };

  const scrollToBottom = () => {
    if (chatContainerRef.current && isAutoScrollEnabled.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [stateRes, historyRes] = await Promise.all([
          axios.get(`${API_BASE}/state`),
          axios.get(`${API_BASE}/history`)
        ]);
        setTargets(stateRes.data);
        setMessages(historyRes.data);
        
        if (!selectedIP && Object.keys(stateRes.data).length > 0) {
          setSelectedIP(Object.keys(stateRes.data)[0]);
        }
      } catch (err) {
        console.error('Sync failed');
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, [selectedIP]);

  useEffect(() => {
    if (!selectedIP) return;
    const fetchSuggestions = async () => {
      try {
        const res = await axios.get(`${API_BASE}/suggestions/${selectedIP}`);
        setSuggestions(res.data);
      } catch (err) {
        setSuggestions([]);
      }
    };
    fetchSuggestions();
  }, [selectedIP, targets]);

  const handleSend = async () => {
    if (!input.trim() || isSending) return;
    const query = input;
    setInput('');
    setIsSending(true);
    isAutoScrollEnabled.current = true;
    try {
      await axios.post(`${API_BASE}/chat`, { query, sender: "Operator" });
    } catch (err) {
      console.error('Chat failed');
    } finally {
      setIsSending(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const selectedTarget = selectedIP ? targets[selectedIP] : null;
  const lastMsg = messages.length > 0 ? messages[messages.length - 1] : null;
  const isAgentThinking = lastMsg?.type === 'user' || isSending;

  return (
    <main className="flex h-screen bg-[#0a0a0a] text-slate-400 font-sans overflow-hidden">
      
      {/* --- LEFT: TARGET MATRIX --- */}
      <aside className="w-72 border-r border-white/5 bg-[#0d0d0d] flex flex-col">
        <div className="p-6 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-3 text-cyan-500">
            <LayoutGrid className="w-4 h-4" />
            <h2 className="font-bold text-xs tracking-widest uppercase">Target Matrix</h2>
          </div>
          <Activity className="w-3 h-3 text-cyan-500 animate-pulse" />
        </div>
        
        <div className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
          {Object.entries(targets).map(([ip, data]) => (
            <button 
              key={ip} 
              onClick={() => setSelectedIP(ip)}
              className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
                selectedIP === ip 
                  ? 'bg-cyan-500/10 border-cyan-500/20' 
                  : 'bg-transparent border-transparent hover:bg-white/5'
              }`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className={`text-base font-bold tracking-tight ${selectedIP === ip ? 'text-white' : 'text-slate-400'}`}>{ip}</span>
                {data.access_level === 'admin' && <Skull className="text-red-500 w-3 h-3" />}
              </div>
              <div className="flex gap-2 text-[10px] font-bold text-slate-600 uppercase tracking-tight">
                <span>{Object.keys(data.ports).length} Ports</span>
                <span className={data.access_level === 'admin' ? 'text-red-500' : 'text-emerald-600'}>
                  {data.access_level?.toUpperCase() || 'Scanning'}
                </span>
              </div>
            </button>
          ))}
        </div>
      </aside>

      {/* --- CENTER: MISSION CONTROL --- */}
      <section className="flex-1 flex flex-col bg-[#0a0a0a] overflow-hidden">
        
        <div className="p-8 border-b border-white/5 bg-[#0d0d0d]/30">
          <div className="flex justify-between items-center">
            <div className="space-y-1">
              <h1 className="text-4xl font-black text-white tracking-tight">{selectedIP || "Awaiting Target"}</h1>
              <div className="flex items-center gap-4 text-xs font-bold text-slate-500 uppercase tracking-widest">
                <div className="flex items-center gap-1.5"><Server className="w-3.5 h-3.5 text-slate-700" /> {selectedTarget?.hostname || "Unresolved"}</div>
                <div className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-slate-700" /> {selectedTarget?.os || "Fingerprinting"}</div>
              </div>
            </div>
            <div className="px-4 py-1.5 bg-cyan-500/10 border border-cyan-500/20 rounded-lg">
              <span className="text-[10px] font-black text-cyan-500 uppercase tracking-widest">Active Engagement</span>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-8 space-y-12 custom-scrollbar">
          
          {/* Tactical Playbook */}
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <Flame className="text-red-500 w-5 h-5" />
              <h2 className="text-sm font-black text-white tracking-widest uppercase">Tactical Playbook</h2>
            </div>

            <div className="grid grid-cols-1 gap-3">
              {suggestions.map((v, i) => (
                <div key={i} className="group p-5 rounded-2xl bg-[#111] border border-white/5 hover:border-red-500/20 transition-all">
                  <div className="flex justify-between items-start gap-4">
                    <div className="flex-1 space-y-3">
                      <h4 className="text-sm font-bold text-white group-hover:text-red-500 transition-colors">{v.name}</h4>
                      <div className="flex items-center gap-2">
                        <code className="text-xs font-mono font-bold text-cyan-400 bg-cyan-500/5 px-3 py-1.5 rounded-lg border border-cyan-500/10">
                          {v.command}
                        </code>
                        <button 
                          onClick={() => copyToClipboard(v.command)}
                          className="p-2 bg-white/5 hover:bg-white/10 rounded-lg transition-all text-slate-500 hover:text-white"
                        >
                          <Copy className="w-3.5 h-3.5" />
                        </button>
                      </div>
                      <p className="text-xs leading-relaxed text-slate-500 line-clamp-2">{v.desc}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Targeted Execution Log */}
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <History className="text-cyan-500 w-5 h-5" />
              <h2 className="text-sm font-black text-white tracking-widest uppercase">Target Log: {selectedIP}</h2>
            </div>
            <div className="p-6 rounded-3xl bg-[#0d0d0d] border border-white/5">
               <div className="space-y-3">
                  {messages.filter(m => m.type === 'tool' && m.content.includes(selectedIP || '')).map((m, i) => (
                    <div key={i} className="flex gap-4 group">
                      <div className="text-[10px] text-slate-700 font-bold w-16 pt-0.5">{m.timestamp}</div>
                      <div className="text-xs text-slate-400 font-mono leading-relaxed border-l-2 border-white/5 pl-4 group-hover:border-cyan-500/20 transition-all">
                        {m.content}
                      </div>
                    </div>
                  ))}
               </div>
            </div>
          </div>

        </div>
      </section>

      {/* --- RIGHT: STRATEGY STREAM --- */}
      <aside className="w-[420px] flex flex-col bg-[#0d0d0d] border-l border-white/5">
        <div className="p-6 border-b border-white/5 flex items-center justify-between sticky top-0 z-10 bg-[#0d0d0d]">
          <div className="flex items-center gap-3">
            <Cpu className="text-magenta-500 w-5 h-5" />
            <h2 className="font-bold text-xs text-white tracking-widest uppercase">Neural Strategy</h2>
          </div>
          <span className="text-[10px] font-black text-magenta-500 uppercase tracking-widest bg-magenta-500/10 px-2 py-0.5 rounded">Live</span>
        </div>

        <div 
          ref={chatContainerRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar scroll-smooth"
        >
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[95%] p-5 rounded-2xl border transition-all ${
                msg.type === 'ai' ? 'bg-[#151515] border-magenta-500/10' : 
                msg.type === 'tool' ? 'bg-transparent border-white/5 text-slate-600 font-mono text-[10px] italic' : 
                'bg-cyan-500/10 border-cyan-500/20 text-white'
              }`}>
                <div className={`flex items-center gap-2 mb-3 ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}>
                  <span className={`text-[9px] font-black uppercase tracking-widest ${
                    msg.type === 'ai' ? 'text-magenta-500' : 'text-slate-500'
                  }`}>
                    {msg.sender}
                  </span>
                  <span className="text-[8px] text-slate-700 font-bold">{msg.timestamp}</span>
                </div>
                
                {msg.type === 'ai' && msg.content.includes('pt ') ? (
                  <div className="space-y-4">
                     <p className="text-xs leading-relaxed font-medium text-slate-400">{msg.content.split('pt ')[0]}</p>
                     <div className="p-4 bg-magenta-500/5 border border-magenta-500/10 rounded-xl">
                        <h5 className="text-[9px] font-black text-magenta-500 uppercase tracking-widest mb-3">Recommended</h5>
                        <code className="text-xs font-bold text-white bg-black/40 p-3 rounded-lg block mb-4 border border-white/5">
                           {msg.content.split('pt ')[1].split(' ')[0]}
                        </code>
                        <button 
                           onClick={() => copyToClipboard(msg.content.split('pt ')[1])}
                           className="w-full py-2.5 bg-magenta-500 text-black text-xs font-bold rounded-lg hover:bg-magenta-400 transition-colors flex items-center justify-center gap-2"
                        >
                           <Copy className="w-3.5 h-3.5" /> Copy String
                        </button>
                     </div>
                  </div>
                ) : (
                  <p className="text-xs leading-relaxed whitespace-pre-wrap font-medium text-slate-400">{msg.content}</p>
                )}
              </div>
            </div>
          ))}
          {isAgentThinking && (
            <div className="flex justify-start animate-pulse">
              <div className="bg-[#151515] border border-magenta-500/10 rounded-full px-5 py-3">
                <div className="flex gap-2">
                  <div className="w-1.5 h-1.5 bg-magenta-500 rounded-full" />
                  <div className="w-1.5 h-1.5 bg-magenta-500 rounded-full" />
                  <div className="w-1.5 h-1.5 bg-magenta-500 rounded-full" />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="p-6 border-t border-white/5 bg-[#0d0d0d]">
          <div className="relative flex items-center group">
            <input 
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Inject Strategic Query..."
              className="w-full bg-[#0a0a0a] border border-white/5 rounded-xl px-5 py-4 text-sm font-medium focus:outline-none focus:border-magenta-500/30 transition-all pr-12"
            />
            <button 
              onClick={handleSend}
              disabled={isSending}
              className="absolute right-4 text-magenta-500 hover:text-white transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </aside>

      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.05); border-radius: 10px; }
      `}</style>
    </main>
  );
}
