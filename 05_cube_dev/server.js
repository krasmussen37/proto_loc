// Standard Cube.js server startup
const CubeApi = require('@cubejs-backend/server');

const server = new CubeApi();

server.listen().then(({ port }) => {
  console.log(`🚀 Cube.js server is running on http://localhost:${port}`);
  console.log(`🧊 Schema files loaded from: ./schema/`);
});