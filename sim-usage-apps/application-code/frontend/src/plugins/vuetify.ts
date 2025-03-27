// Styles
import '@mdi/font/css/materialdesignicons.css';
import 'vuetify/styles';

// Vuetify
import { createVuetify, type ThemeDefinition } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

/**
 * Custom Theme
 */
const myCustomLightTheme: ThemeDefinition = {
  dark: false,
  // Color Palette はツールを使って作成してください https://m3.material.io/theme-builder#/custom
  // TODO: Vuetify 3.0 は Material Design 3 の Color Palette を踏襲していないと思う。なので現時点では限界がある。
  colors: {
    background: '#FFFFFF',
    surface: '#F6F6F6',
    primary: '#00658B',
    secondary: '#1760A5',
    teritary: '#D3E3FF',
    error: '#EC8981',
    warning: '#F2DC9D',
    success: '#A3EBA6',
    info: '#B3E5FC',
  },
};

/**
 * コンポーネントの属性の既定値です。
 * v-defaults-provider や createVuetify のパラメータとして使用できます。
 */
export const componentDefaults = {
  global: {},
  VBtn: {
    color: 'secondary',
  },
  VCombobox: {
    density: 'compact',
    validateOn: 'blur',
  },
  VTextField: {
    density: 'compact',
    validateOn: 'blur',
  },
  VTextarea: {
    density: 'compact',
    validateOn: 'blur',
  },
  VSelect: {
    density: 'compact',
    validateOn: 'blur',
  },
  VSwitch: {
    color: 'primary',
  },
  VRadioGroup: {
    color: 'secondary',
  },
  VRow: {
    align: 'center',
  },
  VCheckboxBtn: {
    color: 'secondary',
  },
};

/**
 * Vuetify のための Vue プラグインを作成します。
 */
export default createVuetify({
  // TODO: デバッグ時の起動が遅いと思う場合は、Vuetify コンポーネントが多すぎて Tree Shaking が重いからかもしれない。
  // https://vuetifyjs.com/en/features/treeshaking/ にあるように、コンポーネントを Manual Import に切り替えた上で、
  // vite-plugin-vuetify の autoImport の値を mode === 'production'（プロダクションモードのときだけ true になる）ようにすればいいかも？
  defaults: componentDefaults,
  theme: {
    defaultTheme: 'light',
    variations: {
      colors: ['primary', 'secondary', 'surface'],
      lighten: 5,
      darken: 4,
    },
    themes: {
      light: myCustomLightTheme,
    },
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
});
