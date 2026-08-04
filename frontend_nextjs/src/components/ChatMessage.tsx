"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { motion } from "framer-motion";
import { User, Sparkles, Calendar, ExternalLink } from "lucide-react";
import { ThinkingExpander } from "./ThinkingExpander";

export interface Message {
  role: "user" | "assistant";
  content: string;
  agent?: string;
  timestamp?: string;
}

interface ChatMessageProps {
  message: Message;
  theme: "light" | "dark";
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, theme }) => {
  const isUser = message.role === "user";
  const isDark = theme === "dark";
  
  let thinkingText = "";
  let mainText = message.content;

  if (!isUser && message.content.includes("---THINKING---") && message.content.includes("---THINKING_END---")) {
    const parts = message.content.split("---THINKING_END---");
    thinkingText = parts[0].replace("---THINKING---", "").trim();
    mainText = parts.length > 1 ? parts[1].trim() : "";
  }

  // Determine Agent Icon
  const getAgentIcon = (agentName: string = "Supervisor Agent") => {
    if (agentName.toUpperCase().includes("SCHEDULING") || agentName.toUpperCase().includes("CALENDAR")) {
      return Calendar;
    }
    return Sparkles;
  };

  const IconComp = getAgentIcon(message.agent);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex w-full py-4 ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div className={`flex gap-4 max-w-3xl w-full ${isUser ? "flex-row-reverse justify-start" : "flex-row"}`}>
        {/* ChatGPT Style Minimalist Avatar */}
        <div className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center font-bold text-xs ${
          isUser 
            ? isDark ? "bg-zinc-600 text-white" : "bg-zinc-800 text-white" 
            : "bg-emerald-600 text-white shadow-xs"
        }`}>
          {isUser ? <User className="w-4 h-4" /> : <IconComp className="w-4 h-4" />}
        </div>

        {/* Message Container - NO heavy bounding boxes for Assistant replies, exactly like ChatGPT! */}
        <div className={`space-y-2 flex-1 min-w-0 ${isUser ? "max-w-fit" : ""}`}>
          {!isUser && message.agent && (
            <div className="flex items-center space-x-2 text-xs font-semibold tracking-tight opacity-80">
              <span className={isDark ? "text-zinc-300" : "text-zinc-700"}>{message.agent}</span>
            </div>
          )}

          <div className={`text-sm md:text-base leading-relaxed ${
            isUser
              ? isDark 
                ? "bg-[#2f2f2f] text-zinc-100 px-4 py-2.5 rounded-2xl rounded-tr-sm inline-block shadow-xs" 
                : "bg-[#f4f4f4] text-zinc-900 px-4 py-2.5 rounded-2xl rounded-tr-sm inline-block shadow-xs border border-zinc-200"
              : isDark ? "text-zinc-200" : "text-zinc-800"
          }`}>
            {/* Thinking Accordion */}
            {thinkingText && <ThinkingExpander thinkingText={thinkingText} theme={theme} />}

            {/* Clean Markdown Content */}
            <div className="prose prose-sm max-w-none space-y-2.5 font-normal">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  p: ({ node, ...props }) => <p {...props} className={`my-2 leading-relaxed ${isDark ? "text-zinc-200" : "text-zinc-800"}`} />,
                  a: ({ node, ...props }) => {
                    const isGCal = String(props.href || "").includes("google.com/calendar");
                    return (
                      <a 
                        {...props} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className={`inline-flex items-center gap-1.5 font-medium px-3 py-1.5 rounded-lg transition-all text-xs my-2 ${
                          isGCal 
                            ? "bg-emerald-600 hover:bg-emerald-500 text-white no-underline shadow-sm font-semibold" 
                            : isDark ? "text-emerald-400 underline hover:text-emerald-300" : "text-emerald-600 underline hover:text-emerald-700"
                        }`}
                      >
                        <span>{props.children}</span>
                        <ExternalLink className="w-3.5 h-3.5 inline shrink-0" />
                      </a>
                    );
                  },
                  table: ({ node, ...props }) => (
                    <div className={`overflow-x-auto my-3 rounded-lg border ${isDark ? "border-[#383838]" : "border-zinc-300"}`}>
                      <table {...props} className="w-full text-left border-collapse text-xs font-sans" />
                    </div>
                  ),
                  th: ({ node, ...props }) => <th {...props} className={`p-2.5 font-semibold border-b ${isDark ? "bg-[#272727] text-zinc-200 border-[#383838]" : "bg-zinc-100 text-zinc-800 border-zinc-300"}`} />,
                  td: ({ node, ...props }) => <td {...props} className={`p-2.5 border-b ${isDark ? "border-[#383838]/60 text-zinc-300" : "border-zinc-200 text-zinc-700"}`} />,
                  code: ({ node, ...props }) => <code {...props} className={`px-1.5 py-0.5 rounded font-mono text-xs ${isDark ? "bg-[#272727] text-emerald-400" : "bg-zinc-200 text-zinc-800"}`} />,
                  blockquote: ({ node, ...props }) => <blockquote {...props} className={`border-l-4 border-emerald-500 pl-3 py-1 my-2 not-italic ${isDark ? "text-zinc-300 bg-[#242424]" : "text-zinc-700 bg-zinc-50"}`} />,
                  ul: ({ node, ...props }) => <ul {...props} className="list-disc list-inside space-y-1 my-2" />,
                  ol: ({ node, ...props }) => <ol {...props} className="list-decimal list-inside space-y-1 my-2" />
                }}
              >
                {mainText}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
