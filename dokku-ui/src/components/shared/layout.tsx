import { Suspense } from 'react'
import { Outlet } from 'react-router-dom'
import { Toaster } from "@/components/ui/sonner"
import Loader from '@/components/shared/loader'
import Header from '@/components/shared/header'

export default function Layout() {
  return (
    <>
      <Suspense fallback={<Loader />}>

        {/* Layout */}
        <div className="flex flex-col min-h-screen container mx-auto py-6">

          {/* Header */}
          <Header />

          {/* Body */}
          <main className="flex-grow py-6 space-y-12">
            <Outlet />
          </main>

          {/* Toaster to provide notifications */}
          <Toaster />
        </div>
      </Suspense>
    </>
  )
}
