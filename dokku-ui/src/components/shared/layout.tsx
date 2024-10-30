import { Suspense } from 'react'
import { Outlet } from 'react-router-dom'
import DokkuApiStatus from '../dokku-api-status'
import { Toaster } from "@/components/ui/sonner"
import Loader from '@/components/shared/loader'

export default function Layout() {
  return (
    <>
      <Suspense fallback={<Loader />}>

        {/* Layout */}
        <div className="flex flex-col min-h-screen container mx-auto py-6">

          {/* Header */}
          <header className="py-6">
            <h1 className="text-4xl font-bold text-center mb-4">Dokku Dashboard</h1>
            <DokkuApiStatus />
          </header>

          {/* Body */}
          <main className="flex-grow p-6 overflow-auto space-y-12">
            <Outlet />
          </main>

          <Toaster />
        </div>
      </Suspense>
    </>
  )
}
