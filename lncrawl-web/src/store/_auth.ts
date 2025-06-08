import type { AuthLoginResponse, User } from '@/types';
import { UserRole } from '@/types/enums';
import { parseJwt } from '@/utils/jwt';
import type { PayloadAction } from '@reduxjs/toolkit';
import { createSelector, createSlice } from '@reduxjs/toolkit';
import axios from 'axios';
import type { PersistConfig } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import type { RootState } from '.';

//
// Initial State
//

export interface AuthState {
  user: User | null;
  token: string | null;
  tokenExpiresAt: number;
  emailVerified: boolean;
}

const buildInitialState = (): AuthState => ({
  user: null,
  token: null,
  tokenExpiresAt: 0,
  emailVerified: true,
});

//
// Slice
//
export const AuthSlice = createSlice({
  name: 'auth',
  initialState: buildInitialState(),
  reducers: {
    setAuth(state, action: PayloadAction<AuthLoginResponse>) {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.emailVerified = action.payload.is_verified;
      state.tokenExpiresAt = 1000 * parseJwt(state.token).exp;
      axios.defaults.headers.common.Authorization = `Bearer ${state.token}`;
    },
    clearAuth(state) {
      state.user = null;
      state.token = null;
      state.tokenExpiresAt = 0;
      axios.defaults.headers.common.Authorization = undefined;
    },
    setEmailVerified(state) {
      state.emailVerified = true;
    },
  },
});

//
// Actions & Selectors
//
const selectAuth = (state: RootState) => state.auth;
const selectLoggedIn = createSelector(
  selectAuth, //
  (auth) => auth.token && auth.tokenExpiresAt > Date.now()
);
const selectUser = createSelector(
  selectAuth, //
  (auth) => auth.user
);
const selectIsAdmin = createSelector(
  selectUser, //
  (user) => user?.role === UserRole.ADMIN
);
const selectAuthorization = createSelector(
  selectAuth,
  selectLoggedIn, //
  (auth, loggedIn) => (loggedIn ? `Bearer ${auth.token}` : undefined)
);
const selectEmailVerified = createSelector(
  selectAuth, //
  (auth) => auth.emailVerified
);

export const Auth = {
  action: AuthSlice.actions,
  select: {
    loggedIn: selectLoggedIn,
    user: selectUser,
    isAdmin: selectIsAdmin,
    isVerified: selectEmailVerified,
    authorization: selectAuthorization,
  },
};

//
// Persist Config
//
const blacklist: Array<keyof AuthState> = [
  // items to exclude from local storage
];

export const authPersistConfig: PersistConfig<AuthState> = {
  key: 'auth',
  version: 1,
  storage,
  blacklist,
};
