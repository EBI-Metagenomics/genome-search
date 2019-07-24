var merge = require('webpack-merge');
var base = require('./webpack.config.base.js');

module.exports = merge(base, {
    mode: 'development',
    devServer: {
        port: 8080
    },
    devtool: 'eval'
});