export const auth0Config = {
  base_url: process.env.NEXT_PUBLIC_AUTH0_BASE_URL,
  client_id: process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID,
  issuer_base_url: process.env.NEXT_PUBLIC_AUTH0_ISSUER_BASE_URL
};

export const gtmConfig = {
  containerId: process.env.NEXT_PUBLIC_GTM_CONTAINER_ID
};

export const mapboxConfig = {
  apiKey: process.env.NEXT_PUBLIC_MAPBOX_API_KEY
};
