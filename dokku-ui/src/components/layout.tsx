import { Suspense } from 'react'
import { Outlet } from 'react-router-dom'

export default function Layout() {
  return (
    <>
      <div className="flex flex-col min-h-screen container mx-auto py-6">
        <Suspense fallback={<div>Loading...</div>}>
          <Outlet />
        </Suspense>
      </div>
    </>
  )
}
