const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  // 开发服务器配置
  devServer: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        ws: false
      },
      '/ws': {
        target: 'ws://localhost:8765',
        changeOrigin: true,
        ws: true
      }
    }
  },

  // 构建配置
  outputDir: 'dist',
  assetsDir: 'static',
  
  // PWA 配置
  pwa: {
    name: 'Mobile Agent',
    themeColor: '#4DBA87',
    msTileColor: '#000000',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black'
  },

  // 其他配置
  configureWebpack: {
    performance: {
      hints: false
    },
    optimization: {
      splitChunks: {
        chunks: 'all',
        minSize: 20000
      }
    }
  },

  // CSS 配置
  css: {
    loaderOptions: {
      sass: {
        additionalData: `
          @import "@/assets/styles/variables.scss";
        `
      }
    }
  }
})
