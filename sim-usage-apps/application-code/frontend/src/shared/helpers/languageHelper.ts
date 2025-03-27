// 言語
const lang = window.navigator.languages || window.navigator.language;
let varLang = 'ja';
if (typeof lang === 'object') {
  // ブラウザの言語設定が日本だった場合には、日本後、それ以外は英語が選択されること
  if (lang[0] !== 'ja' && lang[0] !== 'en') {
    varLang = 'en';
  } else {
    varLang = lang[0];
  }
} else if (typeof lang === 'string') {
  // ブラウザの言語設定が日本だった場合には、日本後、それ以外は英語が選択されること
  if (lang !== 'ja' && lang !== 'en') {
    varLang = 'en';
  } else {
    varLang = lang;
  }
}
export { varLang };
