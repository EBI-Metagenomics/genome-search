var merge = require('webpack-merge');
var base = require('./webpack.config.base.js');

module.exports = merge(base, {
    mode: 'production'
})