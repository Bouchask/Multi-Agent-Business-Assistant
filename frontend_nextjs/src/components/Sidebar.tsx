"use client";

import React, { useState } from "react";
import { 
  Sparkles, 
  Activity, 
  Cpu, 
  Database, 
  Layers, 
  ChevronDown, 
  ChevronRight,
  Terminal,
  Calendar,
  Search,
  Mail,
  TrendingUp,
  FileText,
  Lock,
  MessageSquare,
  Sun,
  Moon,
  Plus,
  PanelLeftClose,
  PanelLeft
} from "lucide-react";

interface SidebarProps {
  selectedDomain: string;
  onSelectDomain: (domain: string) => void;
  kpis: any;
  theme: "light" | "dark";
  onToggleTheme: () => void;
  onNewChat?: () => void;
}

const AGENT_DOMAINS = [
  { name: "1. Supervisor Agent", icon: Sparkles, tag: "Core" },
  { name: "2. Research Agent", icon: Search, tag: "Web" },
  { name: "3. Developer Agent", icon: Terminal, tag: "Code" },
  { name: "4. Email Agent", icon: Mail, tag: "Gmail" },
  { name: "5. Calendar Agent", icon: Calendar, tag: "Sync" },
  { name: "6. Business Analytics", icon: TrendingUp, tag: "Finance" },
  { name: "7. Document Synthesis", icon: FileText, tag: "PDFs" },
  { name: "8. Security & Audit", icon: Lock, tag: "Argon2" },
  { name: "9. Customer Support", icon: MessageSquare, tag: "Support" },
  { name: "10. Strategic Marketing", icon: TrendingUp, tag: "Marketing" }
];

export const Sidebar: React.FC<SidebarProps> = ({ 
  selectedDomain, 
  onSelectDomain, 
  theme, 
  onToggleTheme,
  onNewChat 
}) => {
  const [showSpecs, setShowSpecs] = useState(true);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const isDark = theme === "dark";

  if (isCollapsed) {
    return (
      <aside className={`w-14 border-r flex flex-col items-center py-4 justify-between h-screen shrink-0 transition-all ${
        isDark ? "bg-[#171717] border-[#2d2d2d] text-zinc-300" : "bg-[#f9f9f9] border-zinc-200 text-zinc-700"
      }`}>
        <div className="flex flex-col items-center gap-4">
          <button 
            onClick={() => setIsCollapsed(false)}
            className={`p-2 rounded-lg transition-colors ${isDark ? "hover:bg-zinc-800 text-zinc-400" : "hover:bg-zinc-200 text-zinc-600"}`}
            title="Expand Sidebar"
          >
            <PanelLeft className="w-5 h-5" />
          </button>
          <button 
            onClick={onNewChat}
            className={`p-2 rounded-lg border transition-all shadow-sm ${
              isDark ? "bg-zinc-800 border-zinc-700 text-white hover:bg-zinc-700" : "bg-white border-zinc-300 text-zinc-800 hover:bg-zinc-100"
            }`}
            title="New Chat"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>

        <button 
          onClick={onToggleTheme} 
          className={`p-2 rounded-lg transition-colors ${isDark ? "hover:bg-zinc-800 text-amber-400" : "hover:bg-zinc-200 text-zinc-700"}`}
          title="Toggle Theme"
        >
          {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
      </aside>
    );
  }

  return (
    <aside className={`w-64 border-r p-3.5 flex flex-col justify-between h-screen overflow-y-auto shrink-0 transition-all select-none ${
      isDark ? "bg-[#171717] border-[#2d2d2d] text-zinc-200" : "bg-[#f9f9f9] border-zinc-200 text-zinc-800"
    }`}>
      <div className="space-y-5">
        {/* ChatGPT Style Header Button Dock */}
        <div className="flex items-center justify-between gap-2">
          <button
            onClick={onNewChat}
            className={`flex-1 flex items-center justify-between px-3 py-2 rounded-lg border text-xs font-medium transition-all shadow-xs ${
              isDark 
                ? "bg-[#212121] border-[#343434] text-zinc-200 hover:bg-[#2a2a2a]" 
                : "bg-white border-zinc-300 text-zinc-800 hover:bg-zinc-50"
            }`}
          >
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-500" />
              <span className="font-semibold">New Chat</span>
            </div>
            <Plus className="w-4 h-4 opacity-60" />
          </button>

          <button
            onClick={() => setIsCollapsed(true)}
            className={`p-2 rounded-lg transition-colors ${isDark ? "hover:bg-zinc-800 text-zinc-400" : "hover:bg-zinc-200 text-zinc-600"}`}
            title="Collapse Sidebar"
          >
            <PanelLeftClose className="w-4 h-4" />
          </button>
        </div>

        {/* System Services Status */}
        <div className="space-y-2">
          <h2 className="text-[11px] font-semibold uppercase tracking-wider opacity-50 px-1 flex items-center gap-1.5">
            <Activity className="w-3 h-3 text-emerald-500" />
            Connected Services
          </h2>
          <div className="grid grid-cols-2 gap-1.5 text-[11px]">
            <div className={`p-2 rounded-lg border flex items-center justify-between ${
              isDark ? "bg-[#212121] border-[#2d2d2d]" : "bg-white border-zinc-200"
            }`}>
              <span>FastAPI</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            </div>
            <div className={`p-2 rounded-lg border flex items-center justify-between ${
              isDark ? "bg-[#212121] border-[#2d2d2d]" : "bg-white border-zinc-200"
            }`}>
              <span>GPT-4o</span>
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
            </div>
            <div className={`p-2 rounded-lg border flex items-center justify-between ${
              isDark ? "bg-[#212121] border-[#2d2d2d]" : "bg-white border-zinc-200"
            }`}>
              <span>SQLite</span>
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
            </div>
            <div className={`p-2 rounded-lg border flex items-center justify-between ${
              isDark ? "bg-[#212121] border-[#2d2d2d]" : "bg-white border-zinc-200"
            }`}>
              <span>Qdrant</span>
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
            </div>
          </div>
        </div>

        {/* Domain Specialist Selector */}
        <div className="pt-2 border-t border-inherit">
          <button 
            onClick={() => setShowSpecs(!showSpecs)} 
            className="w-full flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider opacity-50 px-1 mb-2 hover:opacity-80 transition-opacity"
          >
            <span>Agent Specialists (20)</span>
            {showSpecs ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          </button>
          
          {showSpecs && (
            <div className="space-y-0.5 max-h-60 overflow-y-auto pr-1 text-xs">
              {AGENT_DOMAINS.map((agent, idx) => {
                const IconComponent = agent.icon;
                const isSelected = selectedDomain === agent.name;
                return (
                  <button
                    key={idx}
                    onClick={() => onSelectDomain(agent.name)}
                    className={`w-full text-left px-2.5 py-2 rounded-lg transition-colors flex items-center justify-between ${
                      isSelected 
                        ? isDark ? "bg-[#2d2d2d] text-white font-medium" : "bg-zinc-200 text-zinc-900 font-medium"
                        : isDark ? "hover:bg-[#212121] text-zinc-400" : "hover:bg-zinc-100 text-zinc-600"
                    }`}
                  >
                    <div className="flex items-center space-x-2 truncate">
                      <IconComponent className={`w-3.5 h-3.5 shrink-0 ${isSelected ? "text-emerald-500" : "opacity-60"}`} />
                      <span className="truncate">{agent.name}</span>
                    </div>
                    <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded ${
                      isDark ? "bg-zinc-800 text-zinc-400" : "bg-zinc-200 text-zinc-600"
                    }`}>
                      {agent.tag}
                    </span>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Footer & Light/Dark Theme Switch */}
      <div className="pt-3 border-t border-inherit flex items-center justify-between">
        <div className="flex items-center space-x-2 text-xs opacity-70">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span className="font-mono text-[11px]">System Active</span>
        </div>

        <button
          onClick={onToggleTheme}
          className={`p-2 rounded-lg border transition-colors flex items-center gap-1.5 text-xs font-medium ${
            isDark 
              ? "bg-[#212121] border-[#343434] text-amber-400 hover:bg-[#2a2a2a]" 
              : "bg-white border-zinc-300 text-zinc-800 hover:bg-zinc-100 shadow-xs"
          }`}
          title={`Switch to ${isDark ? "Light" : "Night"} Mode`}
        >
          {isDark ? (
            <>
              <Sun className="w-4 h-4 text-amber-400" />
              <span>Light</span>
            </>
          ) : (
            <>
              <Moon className="w-4 h-4 text-zinc-700" />
              <span>Night</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
};
