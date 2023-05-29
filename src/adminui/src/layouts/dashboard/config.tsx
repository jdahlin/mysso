import type { ReactNode } from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import SvgIcon from '@mui/material/SvgIcon';

import BarChartSquare02Icon from 'src/icons/untitled-ui/duocolor/bar-chart-square-02';
import GraduationHat01Icon from 'src/icons/untitled-ui/duocolor/graduation-hat-01';
import HomeSmileIcon from 'src/icons/untitled-ui/duocolor/home-smile';
import Lock01Icon from 'src/icons/untitled-ui/duocolor/lock-01';
import Users03Icon from 'src/icons/untitled-ui/duocolor/users-03';
import XSquareIcon from 'src/icons/untitled-ui/duocolor/x-square';
import { tokens } from 'src/locales/tokens';
import { paths } from 'src/paths';

export interface Item {
  disabled?: boolean;
  external?: boolean;
  icon?: ReactNode;
  items?: Item[];
  label?: ReactNode;
  path?: string;
  title: string;
}

export interface Section {
  items: Item[];
  subheader?: string;
}

export const useSections = () => {
  const { t } = useTranslation();

  return useMemo(
    () => {
      return [
        {
          items: [
            {
              title: t(tokens.nav.overview),
              path: paths.dashboard.analytics,
              icon: (
                <SvgIcon fontSize="small">
                  <HomeSmileIcon />
                </SvgIcon>
              )
            },
          ]
        },
        {
          items: [
            {
              title: t(tokens.nav.applications),
              path: paths.dashboard.applications.index,
              icon: (
                <SvgIcon fontSize="small">
                  <Users03Icon />
                </SvgIcon>
              ),
            },
            {
              title: t(tokens.nav.academy),
              path: paths.dashboard.academy.index,
              icon: (
                <SvgIcon fontSize="small">
                  <GraduationHat01Icon />
                </SvgIcon>
              ),
              items: [
                {
                  title: t(tokens.nav.dashboard),
                  path: paths.dashboard.academy.index
                },
                {
                  title: t(tokens.nav.course),
                  path: paths.dashboard.academy.courseDetails
                }
              ]
            }
          ]
        },
        {
          subheader: t(tokens.nav.pages),
          items: [
            {
              title: t(tokens.nav.auth),
              icon: (
                <SvgIcon fontSize="small">
                  <Lock01Icon />
                </SvgIcon>
              ),
              items: [
                {
                  title: t(tokens.nav.login),
                  items: [
                    {
                      title: 'Classic',
                      path: paths.authDemo.login.classic
                    },
                    {
                      title: 'Modern',
                      path: paths.authDemo.login.modern
                    }
                  ]
                },
                {
                  title: t(tokens.nav.register),
                  items: [
                    {
                      title: 'Classic',
                      path: paths.authDemo.register.classic
                    },
                    {
                      title: 'Modern',
                      path: paths.authDemo.register.modern
                    }
                  ]
                },
                {
                  title: t(tokens.nav.forgotPassword),
                  items: [
                    {
                      title: 'Classic',
                      path: paths.authDemo.forgotPassword.classic
                    },
                    {
                      title: 'Modern',
                      path: paths.authDemo.forgotPassword.modern
                    }
                  ]
                },
                {
                  title: t(tokens.nav.resetPassword),
                  items: [
                    {
                      title: 'Classic',
                      path: paths.authDemo.resetPassword.classic
                    },
                    {
                      title: 'Modern',
                      path: paths.authDemo.resetPassword.modern
                    }
                  ]
                },
                {
                  title: t(tokens.nav.verifyCode),
                  items: [
                    {
                      title: 'Classic',
                      path: paths.authDemo.verifyCode.classic
                    },
                    {
                      title: 'Modern',
                      path: paths.authDemo.verifyCode.modern
                    }
                  ]
                }
              ]
            },
            {
              title: t(tokens.nav.error),
              icon: (
                <SvgIcon fontSize="small">
                  <XSquareIcon />
                </SvgIcon>
              ),
              items: [
                {
                  title: '401',
                  path: paths.notAuthorized
                },
                {
                  title: '404',
                  path: paths.notFound
                },
                {
                  title: '500',
                  path: paths.serverError
                }
              ]
            }
          ]
        },
      ];
    },
    [t]
  );
};
