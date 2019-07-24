const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {
    entry: 'src/web/js/index.js',
    output: {
        path: __dirname + '/dist',
        filename: '[name].[chunkhash:8].js'
    },
    resolve: {
        modules: [__dirname, 'node_modules'],
        alias: { handlebars: 'handlebars/dist/handlebars.min.js' }
    },
    plugins: [
        new CleanWebpackPlugin(),
        new HtmlWebpackPlugin({
            inject: true,
            filename: 'index.html',
            template: __dirname + '/src/web/index.html'
        }),
        new MiniCssExtractPlugin({
            filename: '[name].css'
        }),
        new webpack.ProvidePlugin({
            '$': 'jquery',
            'jQuery': 'jquery',
            'window.jQuery': 'jquery'
        })
    ],
    module: {
        rules: [
            {
                test: /\.css$/,
                use: [MiniCssExtractPlugin.loader, 'css-loader']
            }, {
                test: /\.(woff|woff2|eot|ttf)$/,
                use: { loader: 'file-loader', options: { name: '[path][name].[hash].[ext]' } }
            }, {
                test: /\.(jpe?g|png|gif|svg|ico)$/,
                loader: 'file-loader',
                options: { name: '[path][name].[ext]', context: '' }
            }, {
                test: /\.(html)$/,
                use: {
                    loader: 'html-loader'
                }
            }
        ],
    }
}