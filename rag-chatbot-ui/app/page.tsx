"use client"

import type React from "react"
import { useChat } from "@ai-sdk/react"
import { Bot, User, Loader2, ArrowUp, BarChart3, FileText, Calendar, Search, Paperclip, X } from "lucide-react"
import { useState, useRef } from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"

export default function ChatbotUI() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, setMessages } = useChat()


  const [attachedFiles, setAttachedFiles] = useState<File[]>([])
  const [showBanner, setShowBanner] = useState(true)
  const fileInputRef = useRef<HTMLInputElement>(null)



  const handleNewChat = () => {
    setMessages([])
    setAttachedFiles([])
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setAttachedFiles((prev) => [...prev, ...files])
  }

  const removeFile = (index: number) => {
    setAttachedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const suggestions = [
    { text: "Analyze financial performance metrics", icon: BarChart3 },
    { text: "Summarize key document insights", icon: FileText },
    { text: "Extract important dates and deadlines", icon: Calendar },
    { text: "Compare multiple document sections", icon: Search },
  ]

  return (
    <SidebarProvider>
      <AppSidebar onNewChat={handleNewChat} />
      <SidebarInset>
        <div className="flex flex-col h-screen bg-background transition-colors duration-300">
          {/* Header - Only show if showBanner is true */}
          {showBanner && (
            <div className="flex items-center justify-between border-b border-border px-8 py-6 bg-background/80 backdrop-blur-sm transition-colors duration-300">
              <div className="flex items-center gap-4 animate-in fade-in-0 slide-in-from-left-4 duration-500">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowBanner(false)}
                  className="h-8 w-8 p-0 hover:bg-accent rounded-xl transition-all duration-300 hover:scale-105"
                >
                  <X className="w-4 h-4 text-muted-foreground" />
                </Button>
              </div>

              <div className="flex items-center gap-3 animate-in fade-in-0 slide-in-from-right-4 duration-500">
                <div className="px-3 py-1.5 bg-accent rounded-full transition-colors duration-300">
                  <span
                    className="text-xs font-bold text-accent-foreground tracking-wider transition-colors duration-300"
                    style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
                  >
                    FREE TIER
                  </span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="font-semibold border-border hover:bg-accent bg-transparent rounded-2xl transition-all duration-300 hover:scale-105"
                  style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
                >
                  Upgrade
                </Button>
              </div>
            </div>
          )}

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto bg-gradient-to-b from-background to-muted/30 transition-colors duration-300">
            <div className="max-w-4xl mx-auto px-8 py-12">
              {messages.length === 0 ? (
                <div className="text-center py-24">
                  <Bot className="w-16 h-16 mx-auto text-muted-foreground mb-6 animate-pulse" />
                  <h2 className="text-2xl font-bold text-foreground mb-2" style={{ fontFamily: "var(--font-bricolage-grotesque)" }}>
                    AI Assistant
                  </h2>
                  <p className="text-muted-foreground max-w-md mx-auto">
                    Start a conversation by typing a message or uploading a file.
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  {messages.map((m) => (
                    <div key={m.id} className="flex items-start gap-4 animate-in fade-in-0 slide-in-from-bottom-4 duration-500">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-muted text-muted-foreground font-bold text-sm flex-shrink-0">
                        {m.role === "user" ? (
                          <User className="w-4 h-4" />
                        ) : (
                          <Bot className="w-4 h-4" />
                        )}
                      </div>
                      <div className="flex-1 space-y-2">
                        <div className="font-bold text-foreground text-sm" style={{ fontFamily: "var(--font-bricolage-grotesque)" }}>
                          {m.role === "user" ? "You" : "Assistant"}
                        </div>
                        <div className="prose prose-sm max-w-none text-foreground">
                          {m.content}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {isLoading && (
                <div className="flex items-start gap-4">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-muted text-muted-foreground font-bold text-sm flex-shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="font-bold text-foreground text-sm" style={{ fontFamily: "var(--font-bricolage-grotesque)" }}>
                      Assistant
                    </div>
                    <div className="prose prose-sm max-w-none text-foreground">
                      <Loader2 className="w-4 h-4 animate-spin" />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Chat Input */}
          <div className="bg-background/90 backdrop-blur-sm transition-colors duration-300">
            <div className="max-w-4xl mx-auto px-8 py-6">
              {suggestions.length > 0 && messages.length === 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 animate-in fade-in-0 slide-in-from-bottom-4 duration-500">
                  {suggestions.map((s, i) => (
                    <button
                      key={i}
                      onClick={() => handleInputChange({ target: { value: s.text } } as any)}
                      className="flex items-center gap-3 p-3 border border-border rounded-2xl hover:bg-accent transition-all duration-300 text-left"
                    >
                      <s.icon className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                      <span className="text-sm font-medium text-foreground" style={{ fontFamily: "var(--font-bricolage-grotesque)" }}>
                        {s.text}
                      </span>
                    </button>
                  ))}
                </div>
              )}

              {attachedFiles.length > 0 && (
                <div className="mb-4 animate-in fade-in-0 slide-in-from-bottom-4 duration-500">
                  <div className="flex flex-wrap gap-3">
                    {attachedFiles.map((file, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-2 pl-2 pr-3 py-1.5 bg-accent rounded-full text-accent-foreground"
                      >
                        <FileText className="w-4 h-4 text-accent-foreground" />
                        <span
                          className="text-sm font-medium text-accent-foreground max-w-32 truncate"
                          style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
                        >
                          {file.name}
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(index)}
                          className="h-5 w-5 p-0 hover:bg-accent/80 rounded-full transition-all duration-300 hover:scale-110"
                        >
                          <X className="w-3 h-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <form onSubmit={handleSubmit} className="relative">
                <div className="flex items-end gap-4 p-4 border border-border rounded-3xl bg-card shadow-lg shadow-primary/5 focus-within:border-ring focus-within:shadow-xl focus-within:shadow-primary/10 transition-all duration-300">
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    multiple
                    className="hidden"
                    accept=".pdf,.doc,.docx,.txt,.md"
                  />

                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                    className="h-10 w-10 p-0 text-muted-foreground hover:text-foreground hover:bg-accent rounded-2xl transition-all duration-300 hover:scale-110 hover:rotate-12"
                  >
                    <Paperclip className="w-4 h-4" />
                  </Button>

                  <div className="flex-1">
                    <textarea
                      value={input}
                      onChange={handleInputChange}
                      placeholder="Ask anything..."
                      className="w-full bg-transparent border-none outline-none text-sm placeholder-muted-foreground font-medium resize-none min-h-[20px] max-h-32 text-foreground transition-colors duration-300"
                      style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
                      disabled={isLoading}
                      rows={1}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          (e.target as HTMLTextAreaElement).form?.requestSubmit();
                        }
                      }}
                    />
                  </div>

                  <Button
                    type="submit"
                    disabled={(!input.trim() && attachedFiles.length === 0) || isLoading}
                    size="sm"
                    className="h-10 w-10 p-0 bg-primary hover:bg-primary/90 disabled:bg-muted text-primary-foreground rounded-3xl transition-all duration-300 hover:scale-105 active:scale-95 shadow-lg shadow-primary/20 disabled:hover:scale-100"
                  >
                    <ArrowUp className="w-4 h-4 transition-transform duration-300 group-hover:translate-y-[-1px]" />
                  </Button>
                </div>
              </form>

              <div
                className="flex items-center justify-center gap-6 mt-4 text-xs text-muted-foreground font-medium transition-colors duration-300"
                style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
              >
                <span>Press Enter to send</span>
                <span>•</span>
                <span>Shift + Enter for new line</span>
                <span>•</span>
                <span>Powered by AI</span>
              </div>
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
