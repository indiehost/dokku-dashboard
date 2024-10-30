import { Suspense } from 'react'
import { Outlet } from 'react-router-dom'
import DokkuApiStatus from '../dokku-api-status'
import { Toaster } from "@/components/ui/sonner"
import Loader from '@/components/shared/loader'
import { DarkModeToggle } from '@/components/ui/dark-mode-toggle'
import BackButton from '@/components/shared/back-button'

export default function Layout() {
  return (
    <>
      <Suspense fallback={<Loader />}>

        {/* Layout */}
        <div className="flex flex-col min-h-screen container mx-auto py-6">

          {/* Added flex container for dark mode toggle */}
          <div className="flex justify-between items-center">
            <BackButton />

            {/* Header */}
            <header className="py-6">
              <h1 className="text-4xl font-bold text-center">Dokku Dashboard</h1>
              <DokkuApiStatus />
            </header>

            <DarkModeToggle />

          </div>

          {/* Body */}
          <main className="flex-grow py-6 overflow-auto space-y-12">
            <Outlet />
          </main>

          <Toaster />
        </div>
      </Suspense>
    </>
  )
}
