import { lazy, StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import './styles/global.css'
import Layout from './components/shared/layout';
import {
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query'

// Create query client
const queryClient = new QueryClient()

// Lazily import pages to avoid unnecessary bundle size
const Home = lazy(() => import('./pages/index'));
const Error = lazy(() => import('./pages/error'));
const AppDetails = lazy(() => import('./pages/apps/[appName]'));

// Router
// Add new routes here
export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    errorElement: <Error />,
    children: [
      {
        index: true,
        element: <Home />
      },
      {
        path: 'apps/:appName',
        element: <AppDetails />
      }
    ]
  }
]);

// Entry point
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
)
