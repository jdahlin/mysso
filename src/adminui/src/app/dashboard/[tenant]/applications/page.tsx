'use client';
import * as React from "react";
import PlusIcon from '@untitled-ui/icons-react/build/esm/Plus';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import Container from '@mui/material/Container';
import Stack from '@mui/material/Stack';
import SvgIcon from '@mui/material/SvgIcon';
import Typography from '@mui/material/Typography';

import {Seo} from 'src/components/seo';
import {ApplicationListTable} from "src/sections/dashboard/applications/application-list-table";
import type {Application} from 'src/types/application';
import {RouterLink} from "src/components/router-link";
import {paths} from "src/paths";
import {useTable, HttpError} from "@refinedev/core";
import {useAuth} from "src/hooks/use-auth";
import {AuthContextType} from "src/contexts/auth/auth0";

const AddButton = ({href}: { href: string }) => (
  <Button
    component={RouterLink}
    href={href}
    startIcon={(
      <SvgIcon>
        <PlusIcon/>
      </SvgIcon>
    )}
    variant="contained"
  >
    Add
  </Button>);

const Page = () => {
  const { token } = useAuth<AuthContextType>();
  const table = useTable<Application, HttpError>({
    resource: "application",
    syncWithLocation: true,
  });
  const applications = table.tableQueryResult?.data?.data
  if (!applications) {
    return <>Loading</>
  }
  const onRowsPerPageChange: React.ChangeEventHandler<HTMLInputElement> = (event) => {
    table.setPageSize(parseInt(event.target.value, 10))
  };
  const onPageChange = (event: React.MouseEvent<HTMLButtonElement> | null, newPage: number) =>
    table.setCurrent(newPage);

  return (
    <>
      <Seo title="Dashboard: Applications List"/>
      <Box
        component="main"
        sx={{flexGrow: 1, py: 8}}>
        <Container maxWidth="xl">
          <Stack spacing={4}>
            <Stack
              direction="row"
              justifyContent="space-between"
              spacing={4}
            >
              <Stack spacing={1}>
                <Typography variant="h4">
                  Applications
                </Typography>
              </Stack>
              <Stack
                alignItems="center"
                direction="row"
                spacing={3}
              >
                <AddButton href={paths.dashboard.applications.create}/>
              </Stack>
            </Stack>
            <Card>
              <ApplicationListTable
                count={table.pageCount}
                items={applications}
                onPageChange={onPageChange}
                onRowsPerPageChange={onRowsPerPageChange}
                page={table.current}
                rowsPerPage={table.pageSize}
              />
            </Card>
          </Stack>
        </Container>
      </Box>
    </>
  );
};

export default Page;
