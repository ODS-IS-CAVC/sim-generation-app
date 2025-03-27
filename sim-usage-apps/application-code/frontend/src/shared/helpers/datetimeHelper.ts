import { format as dateFnsTzFormat } from 'date-fns-tz';
import { useI18n } from 'vue-i18n';
/**
 * 日時を現在のロケールでフォーマットします。
 * @param date フォーマットする日時です。
 * @returns date の文字列表現。
 */
export function formatDate(date: Date) {
  // language
  const { locale } = useI18n({ useScope: 'global' });
  if (locale.value == 'ja') {
    return dateFnsTzFormat(date, 'yyyy/MM/dd HH:mm:ss (z)');
  } else if (locale.value == 'en') {
    return dateFnsTzFormat(date, 'MM/dd/yyyy HH:mm:ss (z)');
  }
}

/**
 * フォーマットの型を戻る。
 * @param language 言語。
 * @returns string フォーマット文字列。
 */
export function formatReturnString(language: string) {
  if (language == '日本語') {
    return 'yyyy/MM/dd hh:mm';
  } else if (language == 'English') {
    return 'MM/dd/yyyy hh:mm';
  }
}
/**
 * 日時をフォーマットします。
 * @param date フォーマットする日時です。
 * @returns date の文字列表現。
 */
export function formatDateString(date: Date | string) {
  return dateFnsTzFormat(date, 'yyyy/MM/dd HH:mm:ss (z)');
}

/**
 *現在のUNIX時刻を取得する
 * @returns 現在のUNIX時刻の秒
 */
export function getCurrentTimeStamp(): number {
  return Math.round(Date.now() / 1000);
}

/* 日時をフォーマットします。
 * @param date フォーマットする日時です。
 * @returns date の文字列表現。
 */
export function dateFormat(date: string) {
  const dateNew = new Date(date);
  return dateFnsTzFormat(dateNew, 'yyyy/MM/dd HH:mm');
}
