import { useContext } from 'react';

import type { AuthContextType as Auth0AuthContextType } from 'src/contexts/auth/auth0';
import type { AuthContextType as JwtAuthContextType } from 'src/contexts/auth/jwt';
import { AuthContext } from 'src/contexts/auth/auth0';

type AuthContextType =
  | Auth0AuthContextType
  | JwtAuthContextType;

export const useAuth = <T = AuthContextType>() => useContext(AuthContext) as T;
