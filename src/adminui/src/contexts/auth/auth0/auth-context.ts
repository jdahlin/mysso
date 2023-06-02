import type { User } from 'src/types/user';
import { Issuer } from 'src/utils/auth';
import { createContext } from 'react';

export interface State {
  isInitialized: boolean;
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
}

export const initialState: State = {
  isAuthenticated: false,
  isInitialized: false,
  user: null,
  token: null
};

const DISABLE_AUTH = 0;
if (DISABLE_AUTH) {
  initialState.isAuthenticated = true;
  initialState.user = { id: '1', username: 'johan', email: 'jdahlin@gmail.com', name: 'Johan', avatar: 'null'};
  initialState.isInitialized = true;
  initialState.token = 'foo';
}

type AppState = {
  returnTo?: string;
};

export interface AuthContextType extends State {
  issuer: Issuer.Auth0;
  loginWithRedirect: (appState?: AppState) => Promise<void>;
  handleRedirectCallback: () => Promise<AppState | undefined>;
  logout: () => Promise<void>;
  getTokenSilently: () => Promise<string>;
}

export const AuthContext = createContext<AuthContextType>({
  ...initialState,
  issuer: Issuer.Auth0,
  loginWithRedirect: () => Promise.resolve(),
  getTokenSilently: () => Promise.resolve(''),
  handleRedirectCallback: () => Promise.resolve(undefined),
  logout: () => Promise.resolve()
});
