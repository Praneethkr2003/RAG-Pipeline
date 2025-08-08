"use client"

import { useState } from "react"
import { Plus, Search, Library, Settings, History, Trash2, Edit3, PanelLeft } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  useSidebar,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "./theme-toggle"

const chatHistory = [
  { id: 1, title: "Financial Analysis Q4", timestamp: "2h", status: "active" },
  { id: 2, title: "Legal Document Review", timestamp: "1d", status: "completed" },
  { id: 3, title: "Market Research Summary", timestamp: "2d", status: "completed" },
  { id: 4, title: "Technical Specification", timestamp: "3d", status: "completed" },
  { id: 5, title: "Product Strategy Doc", timestamp: "1w", status: "archived" },
  { id: 6, title: "Compliance Report", timestamp: "1w", status: "archived" },
]

const navigationItems = [
  { title: "Discover", icon: Search, url: "#", badge: "New" },
  { title: "Library", icon: Library, url: "#" },
  { title: "History", icon: History, url: "#" },
  { title: "Settings", icon: Settings, url: "#" },
]

interface AppSidebarProps {
  onNewChat: () => void
}

export function AppSidebar({ onNewChat }: AppSidebarProps) {
  const [hoveredChat, setHoveredChat] = useState<number | null>(null)
  const { toggleSidebar } = useSidebar()

  return (
    <Sidebar
      collapsible="icon"
      className="border-r-0 bg-zinc-50/50 dark:bg-zinc-950/90 backdrop-blur-sm transition-colors duration-300"
    >
      <SidebarHeader className="p-6 border-b border-zinc-200/50 dark:border-zinc-800/50 transition-colors duration-300 group-data-[collapsible=icon]:p-3 group-data-[collapsible=icon]:border-b-0 group-data-[collapsible=icon]:flex group-data-[collapsible=icon]:flex-col group-data-[collapsible=icon]:items-center">
        {/* Sidebar Toggle - Always visible */}
        <div className="flex items-center justify-start mb-6 animate-in fade-in-0 slide-in-from-left-4 duration-500 group-data-[collapsible=icon]:mb-4 group-data-[collapsible=icon]:justify-center">
          <Button
            onClick={toggleSidebar}
            variant="ghost"
            size="sm"
            className="h-10 w-10 p-0 hover:bg-zinc-100/80 dark:hover:bg-zinc-800/80 rounded-2xl transition-all duration-300 hover:scale-105 group-data-[collapsible=icon]:h-10 group-data-[collapsible=icon]:w-10 group-data-[collapsible=icon]:rounded-xl"
          >
            <PanelLeft className="w-4 h-4 text-zinc-600 dark:text-zinc-400 transition-all duration-300 group-hover:text-zinc-900 dark:group-hover:text-zinc-100" />
          </Button>
        </div>

        <div className="flex items-center justify-center mb-4 animate-in fade-in-0 slide-in-from-left-4 duration-500 group-data-[collapsible=icon]:mb-3">
          <Button
            onClick={onNewChat}
            className="w-full h-12 bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-zinc-200 text-white dark:text-zinc-900 font-semibold rounded-2xl transition-all duration-300 hover:scale-[0.98] active:scale-[0.96] animate-in fade-in-0 slide-in-from-bottom-4 duration-700 group-data-[collapsible=icon]:w-10 group-data-[collapsible=icon]:h-10 group-data-[collapsible=icon]:p-0 group-data-[collapsible=icon]:rounded-xl group-data-[collapsible=icon]:mx-auto group-data-[collapsible=icon]:flex group-data-[collapsible=icon]:items-center group-data-[collapsible=icon]:justify-center"
            style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
          >
            <Plus className="w-4 h-4 mr-2 transition-transform duration-300 group-hover:rotate-90 group-data-[collapsible=icon]:mr-0 group-data-[collapsible=icon]:w-4 group-data-[collapsible=icon]:h-4" />
            <span className="group-data-[collapsible=icon]:sr-only">New Conversation</span>
          </Button>
        </div>
      </SidebarHeader>

      <SidebarContent className="px-4 py-6 group-data-[collapsible=icon]:px-2 group-data-[collapsible=icon]:py-4">
        <SidebarGroup className="group-data-[collapsible=icon]:space-y-0">
          <SidebarGroupContent>
            <SidebarMenu className="space-y-1 group-data-[collapsible=icon]:space-y-3">
              {navigationItems.map((item, index) => (
                <SidebarMenuItem
                  key={item.title}
                  className="animate-in fade-in-0 slide-in-from-left-4 group-data-[collapsible=icon]:flex group-data-[collapsible=icon]:justify-center"
                  style={{ animationDelay: `${(index + 1) * 100}ms`, animationDuration: "500ms" }}
                >
                  <SidebarMenuButton
                    asChild
                    className="h-11 hover:bg-zinc-100/80 dark:hover:bg-zinc-800/60 rounded-2xl transition-all duration-300 hover:scale-[1.02] group-data-[collapsible=icon]:h-10 group-data-[collapsible=icon]:w-10 group-data-[collapsible=icon]:p-0 group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:rounded-xl"
                    tooltip={item.title}
                  >
                    <a
                      href={item.url}
                      className="flex items-center justify-between px-3 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:justify-center"
                    >
                      <div className="flex items-center gap-3 group-data-[collapsible=icon]:gap-0">
                        <item.icon className="w-4 h-4 text-zinc-600 dark:text-zinc-300 transition-colors duration-300 group-data-[collapsible=icon]:text-zinc-700 dark:group-data-[collapsible=icon]:text-zinc-200" />
                        <span
                          className="font-medium text-zinc-700 dark:text-zinc-200 transition-colors duration-300 group-data-[collapsible=icon]:sr-only"
                          style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
                        >
                          {item.title}
                        </span>
                      </div>
                      {item.badge && (
                        <span
                          className="text-xs bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 px-2 py-1 rounded-full font-semibold transition-all duration-300 animate-pulse group-data-[collapsible=icon]:hidden"
                          style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
                        >
                          {item.badge}
                        </span>
                      )}
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Hide Recent Sessions section when collapsed */}
        <SidebarGroup className="mt-8 group-data-[collapsible=icon]:hidden">
          <SidebarGroupLabel
            className="px-3 text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-widest mb-4 transition-colors duration-300"
            style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
          >
            Recent Sessions
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu className="space-y-1">
              {chatHistory.map((chat, index) => (
                <SidebarMenuItem
                  key={chat.id}
                  className="animate-in fade-in-0 slide-in-from-left-4"
                  style={{ animationDelay: `${(index + 5) * 100}ms`, animationDuration: "500ms" }}
                >
                  <div
                    className="group relative flex items-center justify-between px-3 py-3 rounded-2xl hover:bg-zinc-100/80 dark:hover:bg-zinc-800/80 cursor-pointer transition-all duration-300 hover:scale-[1.02]"
                    onMouseEnter={() => setHoveredChat(chat.id)}
                    onMouseLeave={() => setHoveredChat(null)}
                  >
                    <div className="flex items-center gap-3 min-w-0 flex-1">
                      <div
                        className={`w-2 h-2 rounded-full flex-shrink-0 transition-all duration-300 ${
                          chat.status === "active"
                            ? "bg-zinc-900 dark:bg-zinc-100 animate-pulse"
                            : chat.status === "completed"
                              ? "bg-zinc-400 dark:bg-zinc-500"
                              : "bg-zinc-200 dark:bg-zinc-700"
                        }`}
                      />
                      <div className="min-w-0 flex-1">
                        <p
                          className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 truncate transition-colors duration-300"
                          style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
                        >
                          {chat.title}
                        </p>
                        <p
                          className="text-xs text-zinc-500 dark:text-zinc-400 font-medium transition-colors duration-300"
                          style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
                        >
                          {chat.timestamp}
                        </p>
                      </div>
                    </div>
                    {hoveredChat === chat.id && (
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all duration-300 animate-in fade-in-0 slide-in-from-right-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0 hover:bg-zinc-200/80 dark:hover:bg-zinc-700/80 rounded-xl transition-all duration-300 hover:scale-110"
                        >
                          <Edit3 className="w-3 h-3 transition-transform duration-300 hover:rotate-12" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0 text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 hover:bg-zinc-200/80 dark:hover:bg-zinc-700/80 rounded-xl transition-all duration-300 hover:scale-110"
                        >
                          <Trash2 className="w-3 h-3 transition-transform duration-300 hover:rotate-12" />
                        </Button>
                      </div>
                    )}
                  </div>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-6 border-t border-zinc-200/50 dark:border-zinc-800/50 transition-colors duration-300 group-data-[collapsible=icon]:p-4 group-data-[collapsible=icon]:border-t-0 group-data-[collapsible=icon]:mt-auto group-data-[collapsible=icon]:flex group-data-[collapsible=icon]:justify-center">
        <div className="flex items-center gap-3 p-3 rounded-2xl bg-zinc-100/50 dark:bg-zinc-800/50 transition-all duration-300 hover:bg-zinc-100 dark:hover:bg-zinc-800/70 animate-in fade-in-0 slide-in-from-bottom-4 duration-1000 group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:p-0 group-data-[collapsible=icon]:bg-transparent group-data-[collapsible=icon]:hover:bg-transparent">
          <div className="w-10 h-10 rounded-2xl bg-zinc-900 dark:bg-zinc-100 flex items-center justify-center transition-all duration-300 hover:scale-105 group-data-[collapsible=icon]:w-6 group-data-[collapsible=icon]:h-6 group-data-[collapsible=icon]:rounded-full group-data-[collapsible=icon]:bg-zinc-900 dark:group-data-[collapsible=icon]:bg-zinc-100">
            <span
              className="text-white dark:text-zinc-900 text-sm font-bold transition-colors duration-300 group-data-[collapsible=icon]:sr-only"
              style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
            >
              U
            </span>
          </div>
          <div className="flex-1 min-w-0 group-data-[collapsible=icon]:hidden">
            <p
              className="text-sm font-bold text-zinc-900 dark:text-zinc-100 transition-colors duration-300"
              style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
            >
              User
            </p>
            <p
              className="text-xs text-zinc-500 dark:text-zinc-400 font-medium transition-colors duration-300"
              style={{ fontFamily: "var(--font-bricolage-grotesque)" }}
            >
              Free Tier
            </p>
          </div>
          <div className="group-data-[collapsible=icon]:hidden">
            <ThemeToggle />
          </div>
        </div>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
