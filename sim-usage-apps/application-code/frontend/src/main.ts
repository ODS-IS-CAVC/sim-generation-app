import { createApp, markRaw } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from '@/router';
import vuetify from '@/plugins/vuetify';
import log from 'loglevel';
import { createI18n } from 'vue-i18n';
import labelTextListJP from '@/locales/labelTextList_jp.json';
import labelTextListEN from '@/locales/labelTextList_en.json';
import messagesListJP from '@/locales/messagesList_jp.json';
import messagesListEN from '@/locales/messagesList_en.json';
import codesListJP from '@/locales/codesList_jp.json';
import codesListEN from '@/locales/codesList_en.json';
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { varLang } from '@/shared/helpers/languageHelper.ts';

import { authenticationGuard } from '@/shared/authentication/authenticationGuard';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import 'video.js/dist/video-js.css';
import {
  catalogConsoleLog,
  errorToString,
  ConsoleLogLevel,
} from '@/shared/helpers/consoleLogHelper';

const app = createApp(App);
const pinia = createPinia();

const langPackage = {
  en: { ...labelTextListEN, ...messagesListEN, ...codesListEN },
  ja: { ...labelTextListJP, ...messagesListJP, ...codesListJP },
};
const i18n = createI18n({
  legacy: false,
  locale: varLang,
  messages: langPackage,
});

app.component('VueDatePicker', VueDatePicker);

//環境識別子
const ENV_FLAG = import.meta.env.VITE_ENV_FLAG;
//デフォルトはlogのlevelがlog.levels.WARNです。
//今回はlog.levels.DEBUGを設定します。
log.setLevel(log.levels.DEBUG);
if (ENV_FLAG === 'stg' || ENV_FLAG === 'prd') {
  //stgとprd環境の場合は、ログlevelはerrorを設定する
  log.setLevel(log.levels.ERROR);
}

app.config.errorHandler = (err, vm, info) => {
  // 本サンプルAPではログの出力とエラー画面への遷移を行っています。
  // APの要件によってはサーバーやログ収集ツールにログを送信し、エラーを握りつぶすこともあります。
  // console.error(err, vm, info);
  catalogConsoleLog(
    ConsoleLogLevel.ERROR,
    'error log test ' + errorToString(err) + ':' + info,
    'main.ts',
    'errorHandler()',
    true,
    'error log test ' + errorToString(err) + ':' + info,
  );
  catalogConsoleLog(
    ConsoleLogLevel.WARN,
    'warn log test ' + errorToString(err) + ':' + info,
    'main.ts',
    'errorHandler()',
    true,
    'warn log test ' + errorToString(err) + ':' + info,
  );
  catalogConsoleLog(
    ConsoleLogLevel.INFO,
    'info log test ' + errorToString(err) + ':' + info,
    'main.ts',
    'errorHandler()',
    false,
    'info log test ' + errorToString(err) + ':' + info,
  );
  catalogConsoleLog(
    ConsoleLogLevel.DEBUG,
    'debug log test ' + errorToString(err) + ':' + info,
    'main.ts',
    'errorHandler()',
    false,
    'debug log test ' + errorToString(err) + ':' + info,
  );
  catalogConsoleLog(
    ConsoleLogLevel.TRACE,
    'trace log test ' + errorToString(err) + ':' + info,
    'main.ts',
    'errorHandler()',
    false,
    'trace log test ' + errorToString(err) + ':' + info,
  );

  router.replace({ name: 'error/system' });
};

window.addEventListener('error', (event) => {
  catalogConsoleLog(
    ConsoleLogLevel.ERROR,
    'Captured in error EventListener:' + errorToString(event.error),
    'main.ts',
    'addEventListener',
    true,
    'Captured in error EventListener:' + errorToString(event.error),
  );

  router.replace({ name: 'error/system' });
});

window.addEventListener('unhandledrejection', (event) => {
  catalogConsoleLog(
    ConsoleLogLevel.ERROR,
    'Captured in unhandledrejection EventListener:' + event.reason,
    'main.ts',
    'addEventListener',
    true,
    'Captured in unhandledrejection EventListener:' + event.reason,
  );
  router.replace({ name: 'error/system' });
});

pinia.use(({ store }) => {
  store.router = markRaw(router);
});
pinia.use(piniaPluginPersistedstate);
export default pinia;

app.use(pinia);
app.use(router);
app.use(i18n);
app.use(vuetify);

authenticationGuard(router);

app.mount('#app');
