export type Application = {
  id: string;
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

export type ApplicationLog = {
  id: string;
  createdAt: number;
  description: string;
  ip: string;
  method: string;
  route: string;
  status: number;
}
