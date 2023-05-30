module.exports = {
  reactStrictMode: true,
  webpack(config) {
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack']


    });
    return config;
  },
  // async headers() {
  //   return [
  //     {
  //       source: '/service/(:path*)',
  //       headers: [
  //         {
  //           key: 'x-source',
  //           value: ':path',
  //         },
  //       ],
  //     },
  //   ];
  // },
  async rewrites() {
    return {
      fallback: [
        {
          source: '/api/:path*',
          destination: `http://127.0.0.1:8000/:path*`
        }
      ]
    }
  }
};
