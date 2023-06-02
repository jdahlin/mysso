import { useContext } from 'react';

import type { AuthContextType as Auth0AuthContextType } from 'src/contexts/auth/auth0';
import { AuthContext } from 'src/contexts/auth/auth0';


export const useAuth = <T = Auth0AuthContextType>() => useContext(AuthContext) as T;
