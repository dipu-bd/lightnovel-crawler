import { Auth } from '@/store/_auth';
import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import {
  Navigate,
  RouterProvider,
  createBrowserRouter,
} from 'react-router-dom';
import { ADMIN_ROUTES, AUTH_ROUTES, USER_ROUTES } from './router';

export const App: React.FC<any> = () => {
  const loggedIn = useSelector(Auth.select.loggedIn);
  const adminUser = useSelector(Auth.select.isAdmin);

  const routes = useMemo(() => {
    if (!loggedIn) {
      return AUTH_ROUTES;
    }
    if (adminUser) {
      return ADMIN_ROUTES;
    }
    return USER_ROUTES;
  }, [loggedIn, adminUser]);

  const router = useMemo(
    () =>
      createBrowserRouter([
        ...routes,
        {
          path: '*',
          element: <Navigate to="/" replace />,
        },
      ]),
    [routes]
  );

  return <RouterProvider router={router} />;
};
