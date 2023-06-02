import axios from "axios";
import {DataProvider, HttpError} from "@refinedev/core";
import {stringify} from "query-string";

const axiosInstance = axios.create();

axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const customError: HttpError = {
      ...error,
      message: error.response?.data?.message,
      statusCode: error.response?.status,
    };

    return Promise.reject(customError);
  },
);

const apiUrl = '/api'

type ModelViewSetParams = {
  page?: number
  size?: number
  // https://www.django-rest-framework.org/api-guide/filtering/#orderingfilter
  // [{ field: 'created', order: 'desc'}, { field: 'id', order: 'asc'}] -> ordering=-created_at,id
  ordering?: string
}

export const drfDataProvider: DataProvider = {
  getApiUrl: () => "",
  getList: async ({resource, pagination, sorters}) => {
    const params: ModelViewSetParams = {
      page: pagination?.current ?? 1,
      size: pagination?.pageSize ?? 10
    }

    if (sorters && sorters.length > 0) {
      let ordering: string[] = [];
      for (let {field, order} of sorters) {
        if (order === 'desc') {
          field = `-${field}`
        }
        ordering.push(field)
      }
      params.ordering = ordering.join(',');
    }
    const {data} = await axiosInstance.get(
      `${apiUrl}/${resource}`, { params }
    );
    return {
      data: data.results,
      total: data.count
    };
  },
  create: async ({resource, variables, meta}) => {
    const url = `${apiUrl}/${resource}`;
    const {data} = await axiosInstance.post(url, variables);
    return {data};
  },
  update: async ({resource, id, variables, meta}) => {
    const url = `${apiUrl}/${resource}/${id}`;
    const {data} = await axiosInstance.patch(url, variables);
    return {data};
  },
  deleteOne: async ({resource, id, variables, meta}) => {
    const url = `${apiUrl}/${resource}/${id}`;
    const {data} = await axiosInstance.delete(url, {data: variables});
    return {data};
  },
  getOne: async ({resource, id, meta}) => {
    const url = `${apiUrl}/${resource}/${id}`;
    const {data} = await axiosInstance.get(url);
    return {data};
  },
  // optional methods
  getMany: async ({resource, ids, meta}) => {
    return {data: []};
  },
  createMany: async ({resource, variables, meta}) => {
    return {data: []}
  },
  deleteMany: async ({resource, ids, variables, meta}) => {
    return {data: []}
  },
  updateMany: async ({resource, ids, variables, meta}) => {
    return {data: []}
  },
  custom: async ({ url, method, sorters, payload, query, headers }) => {
    let requestUrl = url;

    if (sorters && sorters.length > 0) {
      const sortQuery = {
        _sort: sorters[0].field,
        _order: sorters[0].order,
      };
      requestUrl = `${requestUrl}&${stringify(sortQuery)}`;
    }

    if (query) {
      requestUrl = `${requestUrl}&${stringify(query)}`;
    }

    if (headers) {
      axiosInstance.defaults.headers = {
        ...axiosInstance.defaults.headers,
        ...headers,
      };
    }

    let axiosResponse;
    switch (method) {
      case "put":
      case "post":
      case "patch":
        axiosResponse = await axiosInstance[method](url, payload);
        break;
      case "delete":
        axiosResponse = await axiosInstance.delete(url, {
          data: payload,
        });
        break;
      default:
        axiosResponse = await axiosInstance.get(requestUrl);
        break;
    }

    const {data} = axiosResponse;

    return {data};
  },
};
