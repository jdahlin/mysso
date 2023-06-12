'use client';

import type { ChangeEvent } from 'react';
import { useCallback, useState } from 'react';
import ArrowLeftIcon from '@untitled-ui/icons-react/build/esm/ArrowLeft';
import ChevronDownIcon from '@untitled-ui/icons-react/build/esm/ChevronDown';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Container from '@mui/material/Container';
import Divider from '@mui/material/Divider';
import Grid from '@mui/material/Unstable_Grid2';
import Link from '@mui/material/Link';
import Stack from '@mui/material/Stack';
import SvgIcon from '@mui/material/SvgIcon';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Typography from '@mui/material/Typography';

import { RouterLink } from 'src/components/router-link';
import { Seo } from 'src/components/seo';
import { paths } from 'src/paths';
import { getInitials } from 'src/utils/get-initials';
import type { Application } from 'src/types/application';
import {usePathname} from "next/navigation";
import {ApplicationDetailsTab} from "src/sections/dashboard/applications/ApplicationDetailsTab";
import {useOne} from "@refinedev/core";

const tabs = [
  { label: 'Details', value: 'details' },
  { label: 'Invoices', value: 'invoices' },
  { label: 'Logs', value: 'logs' }
];

const Page = () => {
  const [currentTab, setCurrentTab] = useState<string>('details');
  const applicationId = usePathname()?.split('/').pop();
  const { data, isLoading, isError } = useOne<Application>({
    resource: 'application',
    id: applicationId
  })
  const handleTabsChange = useCallback(
    (event: ChangeEvent<any>, value: string): void => {
      setCurrentTab(value);
    },
    []
  );

  const application = data?.data;
  if (!application) {
    return null;
  }

  return (
    <>
      <Seo title="Dashboard: Customer Details" />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          py: 8
        }}
      >
        <Container maxWidth="xl">
          <Stack spacing={4}>
            <Stack spacing={4}>
              <div>
                <Link
                  color="text.primary"
                  component={RouterLink}
                  href={paths.dashboard.applications.index}
                  sx={{
                    alignItems: 'center',
                    display: 'inline-flex'
                  }}
                  underline="hover"
                >
                  <SvgIcon sx={{ mr: 1 }}>
                    <ArrowLeftIcon />
                  </SvgIcon>
                  <Typography variant="subtitle2">
                    Applications
                  </Typography>
                </Link>
              </div>
              <Stack
                alignItems="flex-start"
                direction={{
                  xs: 'column',
                  md: 'row'
                }}
                justifyContent="space-between"
                spacing={4}
              >
                <Stack
                  alignItems="center"
                  direction="row"
                  spacing={2}
                >
                  <Avatar
                    src={"xxx"}
                    sx={{
                      height: 64,
                      width: 64
                    }}
                  >
                    {getInitials(application.client_name)}
                  </Avatar>
                  <Stack spacing={1}>
                    <Typography variant="h4">
                      {application.client_name}
                    </Typography>
                    <Stack
                      alignItems="center"
                      direction="row"
                      spacing={1}
                    >
                      <Typography variant="subtitle2">
                        client_id:
                      </Typography>
                      <Chip
                        label={application.client_id}
                        size="small"
                      />
                    </Stack>
                  </Stack>
                </Stack>
                <Stack
                  alignItems="center"
                  direction="row"
                  spacing={2}
                >
                  <Button
                    endIcon={(
                      <SvgIcon>
                        <ChevronDownIcon />
                      </SvgIcon>
                    )}
                    variant="contained"
                  >
                    Actions
                  </Button>
                </Stack>
              </Stack>
              <div>
                <Tabs
                  indicatorColor="primary"
                  onChange={handleTabsChange}
                  scrollButtons="auto"
                  sx={{ mt: 3 }}
                  textColor="primary"
                  value={currentTab}
                  variant="scrollable"
                >
                  {tabs.map((tab) => (
                    <Tab
                      key={tab.value}
                      label={tab.label}
                      value={tab.value}
                    />
                  ))}
                </Tabs>
                <Divider />
              </div>
            </Stack>
            {currentTab === 'details' && (
              <div>
                <Grid
                  container
                  spacing={4}
                >
                  <ApplicationDetailsTab application={application} />
                </Grid>
              </div>
            )}
            {/*{currentTab === 'invoices' && <CustomerInvoices invoices={invoices} />}*/}
            {/*{currentTab === 'logs' && <CustomerLogs logs={logs} />}*/}
          </Stack>
        </Container>
      </Box>
    </>
  );
};

export default Page;
