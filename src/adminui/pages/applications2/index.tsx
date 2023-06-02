import React from "react";
import { useMany } from "@refinedev/core";
import { List, useDataGrid, DateField } from "@refinedev/mui";
import { DataGrid, GridColumns } from "@mui/x-data-grid";


export type Application = {
  // FIXME: change id to nanoid and remove client_id
  id: number;
  client_name: string;
  client_id: string;
  client_secret: string;
  allowed_callback_uris?: string;
  authorization_code_grant: boolean;
  client_credentials_grant: boolean;
  implicit_grant: boolean;
  password_grant: boolean;
  refresh_token_grant: boolean;
  device_code_grant: boolean;
  require_code_challenge?: boolean;
  require_nounce?: boolean;
  response_type?: string;
  scope?: string;
  tenant?: string;
  token_endpoint_auth_method?: string;
  description?: string;
}

export default function ApplicationList() {
    const { dataGridProps } = useDataGrid();

    const { data: categoryData, isLoading: categoryIsLoading } = useMany({
        resource: "applications",
        ids: dataGridProps?.rows?.map((item: any) => item?.category?.id) ?? [],
        queryOptions: {
            enabled: !!dataGridProps?.rows,
        },
    });

    const columns = React.useMemo<GridColumns<Application>>(
        () => [
            {
                field: "client_id",
                headerName: "Id",
                minWidth: 300,
                align: "left",
            },
            {
                field: "client_name",
                headerName: "Name",
                minWidth: 200,
            },
            {
                field: "token_endpoint_auth_method",
                headerName: "Auth Method",
                minWidth: 160,
            },
            {
                field: "require_code_challenge",
                headerName: "Require PKCE",
            },
            {
                field: "require_nonce",
                headerName: "Require Nonce",
            },
            {
                field: "createdAt",
                headerName: "Created",
                minWidth: 250,
                renderCell: function render({ value }) {
                    return <DateField value={value} />;
                },
            },
        ],
        [categoryData?.data],
    );

    return (
        <List>
            <DataGrid {...dataGridProps} columns={columns} autoHeight />
        </List>
    );
}
