import type { Application } from 'src/types/application';
import { applyPagination } from 'src/utils/apply-pagination';
import { applySort } from 'src/utils/apply-sort';

type GetApplicationsRequest = {
  filters?: {
    query?: string;
    hasAcceptedMarketing?: boolean;
    isProspect?: boolean;
    isReturning?: boolean;
  };
  page?: number;
  rowsPerPage?: number;
  sortBy?: string;
  sortDir?: 'asc' | 'desc';
};

type GetApplicationsResponse = Promise<{
  data: Application[];
  count: number;
}>;

type GetApplicationRequest = {
  applicationId?: number;
};

type GetApplicationResponse = Promise<Application>;

type CreateApplicationRequest = {
    application: Omit<Application, 'id'>
}

type UpdateApplicationRequest = {
    application: Omit<Application, 'id'>
}


class ApplicationApiService {
  async getApplications(token: string, request: GetApplicationsRequest = {}): GetApplicationsResponse {
    const { filters, page, rowsPerPage, sortBy, sortDir } = request;

    const headers = new Headers();
    headers.set('X-Tenant', 'master')
    headers.set('Authorization', `Bearer ${token}`)
    const response = await fetch('/api/application', { headers })

    let data = await response.json() as Application[]
    //let data = deepCopy(applications) as Application[];
    let count = data.length;

    if (typeof filters !== 'undefined') {
      data = data.filter((application) => {
        if (typeof filters.query !== 'undefined' && filters.query !== '') {
          let queryMatched = false;
          const properties: ('client_id')[] = ['client_id'];

          properties.forEach((property) => {
            if ((application[property]).toLowerCase().includes(filters.query!.toLowerCase())) {
              queryMatched = true;
            }
          });

          if (!queryMatched) {
            return false;
          }
        }

        return true;
      });
      count = data.length;
    }
    if (typeof sortBy !== 'undefined' && typeof sortDir !== 'undefined') {
      data = applySort(data, sortBy, sortDir);
    }
    if (typeof page !== 'undefined' && typeof rowsPerPage !== 'undefined') {
      data = applyPagination(data, page, rowsPerPage);
    }

    return Promise.resolve({ data, count });
  }

  async getApplication(token: string, request: GetApplicationRequest): GetApplicationResponse {
    const { applicationId } = request;
    if (!applicationId) {
      return Promise.reject(new Error('Application ID required'))
    }
    const headers = new Headers();
    headers.set('Content-Type', 'application/json')
    headers.set('Authorization', `Bearer ${token}`)
    headers.set('X-Tenant', 'master');
    const response = await fetch(`/api/application/${applicationId}`, { headers })
    return await response.json() as Application;
  }

  async updateApplication(token: string, request: UpdateApplicationRequest) {
    const { application } = request;
    const headers = new Headers();
    headers.set('Content-Type', 'application/json')
    headers.set('Authorization', `Bearer ${token}`)
    headers.set('X-Tenant', 'master')
    const response = await fetch(`/api/application/${application.client_id}`, { method: 'PUT', headers, body: JSON.stringify(application) })
    return await response.json() as Application;
  }
  async createApplication(token: string, request: CreateApplicationRequest) {
    const { application } = request;
    const headers = new Headers();
    headers.set('Content-Type', 'application/json')
    headers.set('Authorization', `Bearer ${token}`)
    headers.set('X-Tenant', 'master')
    const response = await fetch(`/api/application/`, { method: 'POST', headers, body: JSON.stringify(application) })
    return await response.json() as Application;
  }
}

export const applicationsApi = new ApplicationApiService();
