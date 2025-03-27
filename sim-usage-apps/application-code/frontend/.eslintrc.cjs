/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution');

module.exports = {
  root: true,
  extends: [
    'plugin:vue/vue3-strongly-recommended',
    'eslint:recommended',
    '@vue/eslint-config-typescript/recommended',
    '@vue/eslint-config-prettier',
  ],
  env: {
    'vue/setup-compiler-macros': true,
  },

  rules: {
    // タプルなどを _ で受取って捨てたい場合があるので、それだけ許容する。
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_$' }],
    // タグ内の属性値に対して、統一した引用符「"」で囲む。
    'vue/html-quotes': ['error', 'double'],
  },
  ignorePatterns: ['postcss.config.js'],
};
