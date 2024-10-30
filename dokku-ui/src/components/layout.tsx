import { Suspense } from 'react'
import { Outlet } from 'react-router-dom'

export default function Layout() {
  return (
    <>
      <main>
        <Suspense fallback={<div>Loading...</div>}>
          <Outlet />
        </Suspense>
      </main>
    </>
  )
}
