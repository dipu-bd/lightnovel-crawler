import MainLayout from '@/components/Layout';
import { lazy } from 'react';
import { Navigate, type RouteObject } from 'react-router-dom';

// auth
const LoginPage = lazy(() => import('./Login'));
const SignupPage = lazy(() => import('./Signup'));
// user
const HomePage = lazy(() => import('./Home'));
const JobDetailsPage = lazy(() => import('./JobDetails'));
const JobListPage = lazy(() => import('./JobList'));
const NovelDetailsPage = lazy(() => import('./NovelDetails'));
const NovelListPage = lazy(() => import('./NovelList'));
// admin
const UserDetailsPage = lazy(() => import('./UserDetails'));
const UserListPage = lazy(() => import('./UserList'));

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
        element: <HomePage />,
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
        path: 'jobs',
        element: <JobListPage />,
      },
      {
        path: 'job/:id',
        element: <JobDetailsPage />,
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
