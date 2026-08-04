"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { ChatInterface } from "@/components/ChatInterface";
import { AnalyticsDashboard } from "@/components/AnalyticsDashboard";
import { Message } from "@/components/ChatMessage";
import { Sparkles, BarChart3, Layers } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"chat" | "kpis" | "vector">("chat");
  const [selectedDomain, setSelectedDomain] = useState<string>("1. Supervisor Agent");
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      agent: "Supervisor Agent",
      content: "Welcome. I am your autonomous executive supervisor. How can I help you today?"
    }
  ]);

  const toggleTheme = () => {
    setTheme(prev => (prev === "dark" ? "light" : "dark"));
  };

  const handleNewChat = () => {
    setMessages([
      {
        role: "assistant",
        agent: "Supervisor Agent",
        content: "Welcome back. How can I assist with your schedule or business intelligence today?"
      }
    ]);
    setActiveTab("chat");
  };

  const isDark = theme === "dark";

  const tabs = [
    { id: "chat", label: "ChatGPT Orchestration", icon: Sparkles },
    { id: "kpis", label: "System Metrics", icon: BarChart3 },
    { id: "vector", label: "Vector DB", icon: Layers }
  ] as const;

  return (
    <div className={`flex h-screen overflow-hidden ${
      isDark ? "bg-[#212121] text-zinc-100" : "bg-[#ffffff] text-zinc-800"
    } font-sans transition-colors duration-200`}>
      {/* ChatGPT Style Sidebar with Toggle */}
      <Sidebar 
        selectedDomain={selectedDomain} 
        onSelectDomain={(dom) => {
          setSelectedDomain(dom);
          setActiveTab("chat");
        }} 
        kpis={{}}
        theme={theme}
        onToggleTheme={toggleTheme}
        onNewChat={handleNewChat}
      />

      {/* Main Workspace Area */}
      <main className={`flex-1 flex flex-col min-w-0 transition-colors ${
        isDark ? "bg-[#212121]" : "bg-[#ffffff]"
      }`}>
        {/* Sleek Top Header Navigation Bar */}
        <header className={`h-14 border-b px-6 flex items-center justify-between shrink-0 transition-colors ${
          isDark ? "border-[#343434] bg-[#212121]" : "border-zinc-200 bg-white"
        }`}>
          <div className="flex items-center space-x-2">
            <div className={`flex items-center p-1 rounded-xl border ${
              isDark ? "bg-[#171717] border-[#2f2f2f]" : "bg-zinc-100 border-zinc-200"
            }`}>
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                      isActive 
                        ? isDark ? "bg-[#2f2f2f] text-white font-semibold shadow-xs" : "bg-white text-zinc-900 font-semibold shadow-xs border border-zinc-200"
                        : isDark ? "text-zinc-400 hover:text-zinc-200" : "text-zinc-500 hover:text-zinc-800"
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 ${isActive ? "text-emerald-500" : "opacity-60"}`} />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex items-center space-x-3 text-xs font-sans">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className={`font-medium ${isDark ? "text-zinc-400" : "text-zinc-600"}`}>
              Port 8010 Online
            </span>
          </div>
        </header>

        {/* Dynamic Route Content */}
        <div className="flex-1 overflow-hidden relative">
          {activeTab === "chat" && (
            <ChatInterface 
              initialDomain={selectedDomain} 
              theme={theme}
              messages={messages}
              setMessages={setMessages}
            />
          )}
          {(activeTab === "kpis" || activeTab === "vector") && (
            <AnalyticsDashboard theme={theme} />
          )}
        </div>
      </main>
    </div>
  );
}
