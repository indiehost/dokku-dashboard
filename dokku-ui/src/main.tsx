import { lazy, StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import './styles/global.css'
import Layout from './components/layout';


// Lazily import pages to avoid unnecessary bundle size
const Home = lazy(() => import('./pages/index'));
const Test = lazy(() => import('./pages/test'));
const Error = lazy(() => import('./pages/error'));

// Router
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
        path: '/test',
        element: <Test />
      }
    ]
  }
]);

// Entry point
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
