module.exports = {
    root: true,
    env: {
        node: true,
    },
    extends: [
        'plugin:vue/essential',
        'eslint:recommended',
    ],
    rules: {
        'vue/multi-word-component-names': 'off', // 关闭多词组件名称的警告
    },
    parserOptions: {
        parser: 'babel-eslint',
    },
};
