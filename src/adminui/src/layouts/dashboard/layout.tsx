import type { FC, ReactNode } from 'react';
import PropTypes from 'prop-types';

import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { useSettings } from 'src/hooks/use-settings';

import { useSections } from './config';
import { HorizontalLayout } from './horizontal-layout';
import { VerticalLayout } from './vertical-layout';

interface LayoutProps {
  children?: ReactNode;
}

export const Layout: FC<LayoutProps> = withPageAuthRequired((props) => {
  const settings = useSettings();
  const sections = useSections();

  if (settings.layout === 'horizontal') {
    return (
      <HorizontalLayout
        sections={sections}
        navColor={settings.navColor}
        {...props}
      />
    );
  }

  return (
    <VerticalLayout
      sections={sections}
      navColor={settings.navColor}
      {...props}
    />
  );
});

Layout.propTypes = {
  children: PropTypes.node
};
