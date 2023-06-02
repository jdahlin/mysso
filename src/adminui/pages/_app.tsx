import React from "react";
import type {NextPage} from "next";
import {AppProps} from "next/app";
import {Refine} from "@refinedev/core";
import routerProvider from "@refinedev/nextjs-router";
import {drfDataProvider} from "src/drfDataProvider";

export type NextPageWithLayout<P = {}, IP = P> = NextPage<P, IP> & {
  noLayout?: boolean;
};

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

const App = ({Component, pageProps: {...pageProps}}: AppPropsWithLayout) =>
  (
    <Refine
      routerProvider={routerProvider}
      dataProvider={drfDataProvider}
      resources={[
        {
          name: "application",
          list: "/applications",
          create: "/applications/create",
          edit: "/applications/edit/:id",
          show: "/applications/show/:id",
          meta: {
            canDelete: true,
          },
        },
      ]}
    >
      <Component {...pageProps} />
    </Refine>
  );

export default App;
