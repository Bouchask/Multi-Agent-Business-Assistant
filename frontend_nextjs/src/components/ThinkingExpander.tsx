"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronRight, Brain, Check } from "lucide-react";

interface ThinkingExpanderProps {
  thinkingText: string;
  theme: "light" | "dark";
}

export const ThinkingExpander: React.FC<ThinkingExpanderProps> = ({ thinkingText, theme }) => {
  const [isOpen, setIsOpen] = useState(false);
  const isDark = theme === "dark";
  
  // Clean up excessive markdown formatting (*, +, etc.) seen in raw prompts
  const cleanLine = (line: string) => {
    return line
      .replace(/[*+]{2,}/g, "") // remove ++ or **
      .replace(/^[-*+•>\s]+/, "") // remove leading bullet points
      .trim();
  };

  const lines = thinkingText.split("\n").filter(line => line.trim().length > 0);

  return (
    <div className="my-2.5 text-xs">
      {/* ChatGPT Reasoning / Thought Dropdown Toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 px-2.5 py-1.5 rounded-lg transition-colors border font-medium select-none ${
          isDark
            ? "bg-[#272727] border-[#383838] text-zinc-300 hover:bg-[#2e2e2e]"
            : "bg-zinc-100 border-zinc-300 text-zinc-700 hover:bg-zinc-200"
        }`}
      >
        <Brain className="w-3.5 h-3.5 text-emerald-500 shrink-0 animate-pulse" />
        <span>Mission Structure & Reasoning</span>
        <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
          isDark ? "bg-[#1a1a1a] text-zinc-400" : "bg-white text-zinc-600 border border-zinc-200"
        }`}>
          {isOpen ? "Expanded" : "Click to view"}
        </span>
        {isOpen ? <ChevronDown className="w-3.5 h-3.5 ml-1 opacity-60" /> : <ChevronRight className="w-3.5 h-3.5 ml-1 opacity-60" />}
      </button>

      {/* Clean Indented Reasoning Content */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className={`mt-2 ml-2 pl-3 border-l-2 space-y-2 py-1 ${
              isDark ? "border-[#383838] text-zinc-300" : "border-zinc-300 text-zinc-700"
            }`}>
              {lines.map((line, i) => {
                const cleaned = cleanLine(line);
                if (!cleaned) return null;

                // Style checkmark goals cleanly without excessive colored pills
                if (line.includes("✓") || line.includes("✅") || line.toLowerCase().includes("goal")) {
                  return (
                    <div key={i} className="flex items-start gap-2 font-mono text-[11px] text-emerald-500">
                      <Check className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                      <span className={isDark ? "text-zinc-300" : "text-zinc-700"}>{cleaned.replace(/[✓✅]/g, "").trim()}</span>
                    </div>
                  );
                }
                return (
                  <div key={i} className="leading-relaxed font-mono text-[11px] opacity-90">
                    {cleaned}
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
