'use client';

import type { FC, ReactNode } from 'react';
import Head from 'next/head';
import { NextAppDirEmotionCacheProvider } from 'tss-react/next/appDir';
import Cookies from 'js-cookie';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';

import { RTL } from 'src/components/rtl';
import { SplashScreen } from 'src/components/splash-screen';
import { Toaster } from 'src/components/toaster';
import { SettingsConsumer, SettingsProvider } from 'src/contexts/settings';
import { useNprogress } from 'src/hooks/use-nprogress';
import { createTheme } from 'src/theme';
import type { Settings } from 'src/types/settings';

import {Refine} from "@refinedev/core";

// Remove if locales are not used
import 'src/locales/i18n';
import routerProvider from "@refinedev/nextjs-router";
import {drfDataProvider} from "src/drfDataProvider";
import {UserProvider, useUser} from "@auth0/nextjs-auth0/client";

const SETTINGS_STORAGE_KEY = 'app.settings';

const resetSettings = (): void => {
  try {
    Cookies.remove(SETTINGS_STORAGE_KEY);
    window.location.reload();
  } catch (err) {
    console.error(err);
  }
};

const updateSettings = (settings: Settings): void => {
  try {
    Cookies.set(SETTINGS_STORAGE_KEY, JSON.stringify(settings));
    window.location.reload();
  } catch (err) {
    console.error(err);
  }
};

interface LayoutProps {
  children: ReactNode;
  settings?: Settings;
}

export const Layout: FC<LayoutProps> = (props: LayoutProps) => {
  const { children, settings } = props;
  const { user, error, isLoading } = useUser();
  // useAnalytics(gtmConfig);
  useNprogress();

  return (
    <NextAppDirEmotionCacheProvider options={{ key: 'css' }}>
      <LocalizationProvider dateAdapter={AdapterDateFns}>
          <SettingsProvider
            onReset={resetSettings}
            onUpdate={updateSettings}
            settings={settings}
          >
            <SettingsConsumer>
              {(settings) => {
                const theme = createTheme({
                  colorPreset: settings.colorPreset,
                  contrast: settings.contrast,
                  direction: settings.direction,
                  paletteMode: settings.paletteMode,
                  responsiveFontSizes: settings.responsiveFontSizes
                });

                // Prevent guards from redirecting
                const showSlashScreen = !user || isLoading;
                return (
                  <ThemeProvider theme={theme}>
                    <Head>
                      <meta
                        name="color-scheme"
                        content={settings.paletteMode}
                      />
                      <meta
                        name="theme-color"
                        content={theme.palette.neutral[900]}
                      />
                    </Head>
                    <RTL direction={settings.direction}>
                      <Refine
                        dataProvider={drfDataProvider}
                        resources={[
                          {
                            name: "application",
                            list: "/applications2",
                            create: "/applications2/create",
                            edit: "/applications2/edit/:id",
                            show: "/applications2/show/:id",
                            meta: {
                              canDelete: true,
                            },
                          },
                        ]}
                      >
                        <CssBaseline />
                        {
                          showSlashScreen
                            ? <SplashScreen />
                            : <>{children}</>
                        }
                        <Toaster />
                      </Refine>
                    </RTL>
                  </ThemeProvider>
                );
              }}
            </SettingsConsumer>
          </SettingsProvider>
      </LocalizationProvider>
    </NextAppDirEmotionCacheProvider>
  );
};
