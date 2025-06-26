import { Navigate, type RouteObject } from 'react-router-dom';

import { MainLayout } from '@/components/Layout';
import { JobDetailsPage } from './JobDetails';
import { JobListPage } from './JobList';
import { LoginPage } from './Login';
import { NovelDetailsPage } from './NovelDetails';
import { NovelListPage } from './NovelList';
import { NovelReaderPage } from './NovelReaderPage';
import { SignupPage } from './Signup';
import { SupportedSourcesPage } from './SupportedSources';
import { UserDetailsPage } from './UserDetails';
import { UserListPage } from './UserList';

export const AUTH_ROUTES: RouteObject[] = [
  {
    path: '/',
    children: [
      {
        path: '',
        element: <Navigate to="/login" replace />,
      },
      {
        path: '/login',
        element: <LoginPage />,
      },
      {
        path: '/signup',
        element: <SignupPage />,
      },
    ],
  },
];

export const USER_ROUTES: RouteObject[] = [
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        path: '',
        element: <JobListPage />,
      },
      {
        path: 'job/:id',
        element: <JobDetailsPage />,
      },
      {
        path: 'novels',
        element: <NovelListPage />,
      },
      {
        path: 'novel/:id',
        element: <NovelDetailsPage />,
      },
      {
        path: 'novel/:id/chapter/:hash',
        element: <NovelReaderPage />,
      },
      {
        path: 'meta',
        children: [
          {
            path: 'sources',
            element: <SupportedSourcesPage />,
          },
        ],
      },
    ],
  },
];

export const ADMIN_ROUTES: RouteObject[] = [
  ...USER_ROUTES,
  {
    path: '/admin',
    element: <MainLayout />,
    children: [
      {
        path: 'users',
        element: <UserListPage />,
      },
      {
        path: 'user/:id',
        element: <UserDetailsPage />,
      },
    ],
  },
];
