'use client';

import type { ChangeEvent, MouseEvent } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import PlusIcon from '@untitled-ui/icons-react/build/esm/Plus';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import Container from '@mui/material/Container';
import Stack from '@mui/material/Stack';
import SvgIcon from '@mui/material/SvgIcon';
import Typography from '@mui/material/Typography';

import { applicationsApi } from 'src/service/applications/ApplicationApiService';
import { Seo } from 'src/components/seo';
import { useMounted } from 'src/hooks/use-mounted';
import { usePageView } from 'src/hooks/use-page-view';
import { useSelection } from 'src/hooks/use-selection';
import { ApplicationListTable } from "src/sections/dashboard/applications/application-list-table";
import type { Application } from 'src/types/application';
import {RouterLink} from "src/components/router-link";
import {paths} from "src/paths";

interface Filters {
  query?: string;
  hasAcceptedMarketing?: boolean;
  isProspect?: boolean;
  isReturning?: boolean;
}

interface ApplicationsSearchState {
  filters: Filters;
  page: number;
  rowsPerPage: number;
  sortBy: string;
  sortDir: 'asc' | 'desc';
}

const useApplicationsSearch = () => {
  const [state, setState] = useState<ApplicationsSearchState>({
    filters: {
      query: undefined,
      hasAcceptedMarketing: undefined,
      isProspect: undefined,
      isReturning: undefined
    },
    page: 0,
    rowsPerPage: 5,
    sortBy: 'updatedAt',
    sortDir: 'desc'
  });

  const handleFiltersChange = useCallback(
    (filters: Filters): void => {
      setState((prevState) => ({
        ...prevState,
        filters
      }));
    },
    []
  );

  const handleSortChange = useCallback(
    (sort: { sortBy: string; sortDir: 'asc' | 'desc'; }): void => {
      setState((prevState) => ({
        ...prevState,
        sortBy: sort.sortBy,
        sortDir: sort.sortDir
      }));
    },
    []
  );

  const handlePageChange = useCallback(
    (event: MouseEvent<HTMLButtonElement> | null, page: number): void => {
      setState((prevState) => ({
        ...prevState,
        page
      }));
    },
    []
  );

  const handleRowsPerPageChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>): void => {
      setState((prevState) => ({
        ...prevState,
        rowsPerPage: parseInt(event.target.value, 10)
      }));
    },
    []
  );

  return {
    handleFiltersChange,
    handleSortChange,
    handlePageChange,
    handleRowsPerPageChange,
    state
  };
};

type ApplicationsStoreState = {
  applications: Application[];
  applicationsCount: number;
}

const useApplicationsStore = (searchState: ApplicationsSearchState) => {
  const isMounted = useMounted();
  const [state, setState] = useState<ApplicationsStoreState>({
    applications: [],
    applicationsCount: 0
  });

  const handleCustomersGet = useCallback(
    async () => {
      try {
        const response = await applicationsApi.getApplications(searchState);

        if (isMounted()) {
          setState({
            applications: response.data,
            applicationsCount: response.count
          });
        }
      } catch (err) {
        console.error(err);
      }
    },
    [searchState, isMounted]
  );

  useEffect(
    () => {
      handleCustomersGet();
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [searchState]
  );

  return {
    ...state
  };
};

const useApplicationIds = (applications: Application[] = []) => {
  return useMemo(
    () => {
      return applications.map((application) => application.id);
    },
    [applications]
  );
};

const Page = () => {
  const applicationsSearch = useApplicationsSearch();
  const applicationsStore = useApplicationsStore(applicationsSearch.state);
  const applicationIds = useApplicationIds(applicationsStore.applications);
  const applicationSelection = useSelection<string>(applicationIds);

  usePageView();

  return (
    <>
      <Seo title="Dashboard: Applications List" />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          py: 8
        }}
      >
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
                <Button
                  component={RouterLink}
                  href={paths.dashboard.applications.create}
                  startIcon={(
                    <SvgIcon>
                      <PlusIcon />
                    </SvgIcon>
                  )}
                  variant="contained"
                >
                  Add
                </Button>
              </Stack>
            </Stack>
            <Card>
              <ApplicationListTable
                count={applicationsStore.applicationsCount}
                items={applicationsStore.applications}
                onDeselectAll={applicationSelection.handleDeselectAll}
                onDeselectOne={applicationSelection.handleDeselectOne}
                onPageChange={applicationsSearch.handlePageChange}
                onRowsPerPageChange={applicationsSearch.handleRowsPerPageChange}
                onSelectAll={applicationSelection.handleSelectAll}
                onSelectOne={applicationSelection.handleSelectOne}
                page={applicationsSearch.state.page}
                rowsPerPage={applicationsSearch.state.rowsPerPage}
                selected={applicationSelection.selected}
              />
            </Card>
          </Stack>
        </Container>
      </Box>
    </>
  );
};

export default Page;
