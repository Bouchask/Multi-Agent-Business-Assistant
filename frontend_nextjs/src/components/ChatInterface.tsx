"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { ChatMessage, Message } from "./ChatMessage";
import { Send, Sparkles, Loader2, Calendar, Search, Terminal, Mail } from "lucide-react";

interface ChatInterfaceProps {
  initialDomain?: string;
  onRefreshKpis?: () => void;
  theme: "light" | "dark";
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  initialDomain, 
  onRefreshKpis, 
  theme,
  messages,
  setMessages 
}) => {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const isDark = theme === "dark";

  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (customPrompt?: string) => {
    const textToSend = customPrompt || input;
    if (!textToSend.trim() || loading) return;

    const userMsg: Message = { role: "user", content: textToSend };
    const historyPayload = messages.map(m => ({ role: m.role, content: m.content }));
    
    setMessages(prev => [...prev, userMsg]);
    if (!customPrompt) setInput("");
    setLoading(true);

    try {
      // Direct communication with FastAPI multi-agent backend on port 8010
      const response = await fetch("http://localhost:8010/api/v1/chat/direct", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: textToSend, history: historyPayload }),
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();
      const assistantMsg: Message = {
        role: "assistant",
        content: data.reply || "Task completed successfully.",
        agent: data.agent_triggered || "Supervisor Agent",
      };

      setMessages(prev => [...prev, assistantMsg]);
      if (onRefreshKpis) onRefreshKpis();
    } catch (err) {
      console.error("Error calling multi-agent backend:", err);
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          agent: "System Diagnostic",
          content: `⚠️ **Connection Notice**: Could not communicate with FastAPI Backend (http://localhost:8010). Ensure ./run_backend.sh is active in terminal.\n\n*Error details*: ${String(err)}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const sampleCommands = [
    { label: "Schedule Ayoub Meeting", cmd: "insert meet with ayoub in 24-08-2026", icon: Calendar },
    { label: "Search Web Formation Python", cmd: "search in web formation for python", icon: Search },
    { label: "Check Calendar Overview", cmd: "give me calander overview", icon: Mail },
    { label: "Create Python AST Tool", cmd: "create clean python ast code review tool and commit", icon: Terminal }
  ];

  const isEmptyState = messages.length === 0 || (messages.length === 1 && messages[0].agent === "Supervisor Agent" && !messages[0].content.includes("---THINKING---"));

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] max-w-3xl mx-auto w-full px-4 justify-between relative z-10">
      {/* Message Stream or ChatGPT Empty State Hero */}
      <div className="flex-1 overflow-y-auto pr-2 pb-4 pt-6 space-y-2">
        {isEmptyState && messages.length <= 1 ? (
          <div className="h-full flex flex-col items-center justify-center text-center pb-12 select-none">
            <motion.h1 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`text-2xl md:text-3xl font-semibold mb-8 tracking-tight ${isDark ? "text-zinc-100" : "text-zinc-800"}`}
            >
              How can I help you today?
            </motion.h1>

            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-w-xl w-full px-4"
            >
              {sampleCommands.map((item, idx) => {
                const Icon = item.icon;
                return (
                  <button
                    key={idx}
                    onClick={() => handleSend(item.cmd)}
                    className={`p-3 rounded-2xl text-left border transition-all text-xs flex flex-col gap-1.5 shadow-xs ${
                      isDark
                        ? "bg-[#212121] border-[#383838] hover:bg-[#2a2a2a] text-zinc-300"
                        : "bg-white border-zinc-200 hover:bg-zinc-50 text-zinc-700"
                    }`}
                  >
                    <Icon className="w-4 h-4 text-emerald-500" />
                    <span className="font-semibold">{item.label}</span>
                  </button>
                );
              })}
            </motion.div>
          </div>
        ) : (
          <>
            {messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} theme={theme} />
            ))}

            {loading && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center space-x-3 text-xs text-zinc-400 py-3 ml-12"
              >
                <Loader2 className="w-4 h-4 text-emerald-500 animate-spin" />
                <span>Thinking...</span>
              </motion.div>
            )}
            <div ref={bottomRef} />
          </>
        )}
      </div>

      {/* ChatGPT Iconic Bottom Input Console */}
      <div className="pb-6 pt-2 shrink-0">
        <div className={`rounded-3xl flex items-center p-2 transition-shadow ${
          isDark ? "chatgpt-input-dark" : "chatgpt-input-light"
        }`}>
          <div className={`p-2 rounded-full text-emerald-500 ml-1 ${isDark ? "hover:bg-zinc-800" : "hover:bg-zinc-200"}`}>
            <Sparkles className="w-5 h-5" />
          </div>

          <input
            type="text"
            disabled={loading}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSend()}
            placeholder="Ask anything or run autonomous task..."
            className={`flex-1 bg-transparent border-0 outline-none px-3 py-1.5 text-sm md:text-base font-normal disabled:opacity-50 ${
              isDark ? "text-white placeholder:text-zinc-500" : "text-zinc-900 placeholder:text-zinc-400"
            }`}
          />

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={loading || !input.trim()}
            onClick={() => handleSend()}
            className={`w-9 h-9 rounded-full flex items-center justify-center transition-colors disabled:opacity-30 cursor-pointer ${
              isDark 
                ? input.trim() ? "bg-white text-zinc-900" : "bg-[#383838] text-zinc-400" 
                : input.trim() ? "bg-zinc-900 text-white" : "bg-zinc-200 text-zinc-500"
            }`}
          >
            <Send className="w-4 h-4" />
          </motion.button>
        </div>
        <p className={`text-[11px] text-center mt-2.5 font-sans select-none ${
          isDark ? "text-zinc-500" : "text-zinc-400"
        }`}>
          Antigravity Multi-Agent OS can make errors. Check Google Calendar & database verified records.
        </p>
      </div>
    </div>
  );
};
