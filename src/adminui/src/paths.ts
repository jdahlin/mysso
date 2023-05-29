export const paths = {
  index: '/',
  checkout: '/checkout',
  contact: '/contact',
  pricing: '/pricing',
  auth: {
    auth0: {
      callback: '/auth/auth0/callback',
      login: '/auth/auth0/login'
    },
    jwt: {
      login: '/auth/jwt/login',
      register: '/auth/jwt/register'
    },
  },
  authDemo: {
    forgotPassword: {
      classic: '/auth-demo/forgot-password/classic',
      modern: '/auth-demo/forgot-password/modern'
    },
    login: {
      classic: '/auth-demo/login/classic',
      modern: '/auth-demo/login/modern'
    },
    register: {
      classic: '/auth-demo/register/classic',
      modern: '/auth-demo/register/modern'
    },
    resetPassword: {
      classic: '/auth-demo/reset-password/classic',
      modern: '/auth-demo/reset-password/modern'
    },
    verifyCode: {
      classic: '/auth-demo/verify-code/classic',
      modern: '/auth-demo/verify-code/modern'
    }
  },
  dashboard: {
    index: '/dashboard',
    academy: {
      index: '/dashboard/academy',
      courseDetails: '/dashboard/academy/courses/:courseId'
    },
    account: '/dashboard/account',
    analytics: '/dashboard/analytics',
    applications: {
      index: '/dashboard/master/applications',
      details: '/dashboard/master/applications/[applicationId]',
      create: '/dashboard/master/applications/create',
    },
    blank: '/dashboard/blank',
  },
  components: {
    index: '/components',
    dataDisplay: {
      detailLists: '/components/data-display/detail-lists',
      tables: '/components/data-display/tables',
      quickStats: '/components/data-display/quick-stats'
    },
    lists: {
      groupedLists: '/components/lists/grouped-lists',
      gridLists: '/components/lists/grid-lists'
    },
    forms: '/components/forms',
    modals: '/components/modals',
    charts: '/components/charts',
    buttons: '/components/buttons',
    typography: '/components/typography',
    colors: '/components/colors',
    inputs: '/components/inputs'
  },
  docs: 'https://material-kit-pro-react-docs.devias.io',
  notAuthorized: '/errors/401',
  notFound: '/errors/404',
  serverError: '/errors/500'
};
