import type React from "react"
import type { Metadata } from "next"
import { Bricolage_Grotesque } from "next/font/google"
import { ThemeProvider } from "@/components/theme-provider"
import "./globals.css"

const bricolageGrotesque = Bricolage_Grotesque({
  subsets: ["latin"],
  variable: "--font-bricolage-grotesque",
  display: "swap",
  weight: ["200", "300", "400", "500", "600", "700", "800"],
})

export const metadata: Metadata = {
  title: "Chat - AI Assistant",
  description: "Modern AI-powered chat interface with sophisticated design",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={bricolageGrotesque.variable} suppressHydrationWarning>
      <body className={`${bricolageGrotesque.className} antialiased transition-colors duration-300`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange={false}
          storageKey="chat-theme"
        >
          <div className="min-h-screen bg-background text-foreground transition-colors duration-300">{children}</div>
        </ThemeProvider>
      </body>
    </html>
  )
}
