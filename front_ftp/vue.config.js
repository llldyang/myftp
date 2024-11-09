const { defineConfig } = require('@vue/cli-service')
const fs = require('fs');
module.exports = defineConfig({
  transpileDependencies: true
})
module.exports = {
  devServer: {
    https: {
      key: fs.readFileSync('./certs/Server_key.key'),
      cert: fs.readFileSync('./certs/localhost.crt'),
    },
    port: 8080, // 可选，指定开发服务器的端口
  },
};