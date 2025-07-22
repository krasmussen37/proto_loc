const CubeApi = require('@cubejs-backend/server');

const server = new CubeApi();

server.listen().then(({ port }) => {
  console.log(`🚀 Cube server is running on http://localhost:${port}`);
});
