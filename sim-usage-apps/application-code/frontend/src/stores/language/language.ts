import { defineStore } from 'pinia';
import { formatReturnString } from '@/shared/helpers/datetimeHelper';

export const useLanguageStore = defineStore({
  id: 'language',
  state: () => ({
    _language: '',
    _languageCode: '',
    _datePickerFormat: '',
  }),
  persist: true,
  actions: {
    /**
     * 言語を設定する。
     */
    async setLanguage(language: string) {
      this._language = language;
      if (language !== '') {
        this._datePickerFormat = formatReturnString(language);
        if (language === '日本語') {
          this._languageCode = 'ja';
        } else if (language === 'English') {
          this._languageCode = 'en';
        }
      } else {
        this._datePickerFormat = '';
        this._languageCode = '';
      }
    },
  },
  getters: {
    /**
     * 言語を取得する。
     */
    getLanguage(state) {
      return state._language;
    },
    /**
     * 言語コードを取得する。
     */
    getLanguageCode(state) {
      return state._languageCode;
    },

    /**
     * カレンダーのフォマードを取得する。
     */
    getDatePickerFormat(state) {
      return state._datePickerFormat;
    },
  },
});
