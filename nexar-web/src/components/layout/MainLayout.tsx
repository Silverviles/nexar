import type { ReactNode } from 'react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'

interface MainLayoutProps {
  children: ReactNode
  title: string
  description?: string
}

export function MainLayout({ children, title, description }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-canvas">
      <Sidebar />
      <div className="transition-all duration-200 md:ml-64">
        <Header title={title} description={description} />
        <main className="min-h-[calc(100vh-4rem)] bg-canvas">
          <div className="p-4 pt-16 md:p-6 md:pt-6">{children}</div>
        </main>
      </div>
    </div>
  )
}
