import log from 'loglevel';
import { frontEndLogApi } from '@/api-client';

/**
 * ログレベル
 */
export class ConsoleLogLevel {
  static readonly TRACE = 'TRACE';
  static readonly DEBUG = 'DEBUG';
  static readonly INFO = 'INFO';
  static readonly WARN = 'WARN';
  static readonly ERROR = 'ERROR';
}

/**
 *カスタマイズログのツール
 * @param level ログレベル
 * @param content バクエンドに送付する内容
 * @param fileName エラーが発生したファイル名
 * @param functionName エラーが発生した関数名
 * @param backApiFlag バクエンド側送付するフラグ
 *  trueの場合は、送付する; falseの場合は、送付しない
 *  デフォルトはfalseだ
 * @param msg コンソールのメッセージ
 * @returns
 */
export function catalogConsoleLog(
  level: string,
  content: string,
  fileName: string,
  functionName: string,
  backApiFlag = false,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ...msg: any[]
): void {
  //ログを出力する
  if (level === ConsoleLogLevel.TRACE) {
    log.trace(...msg);
  } else if (level === ConsoleLogLevel.DEBUG) {
    log.debug(...msg);
  } else if (level === ConsoleLogLevel.INFO) {
    log.info(...msg);
  } else if (level === ConsoleLogLevel.WARN) {
    log.warn(...msg);
  } else if (level === ConsoleLogLevel.ERROR) {
    log.error(...msg);
  } else {
    //デフォルトは debugだ
    log.debug(...msg);
  }

  //backApiFlagはtrueの場合は、ログはバクエンドに送付する
  if (backApiFlag === true) {
    //バクエンドに送付する
    const requestParam = {
      level: level,
      content: content,
      fileName: fileName,
      functionName: functionName,
    };

    frontEndLogApi.uploadFrontendLog('', requestParam).catch((err) => {
      console.log(err);
    });
  }

  return;
}

/**
 * errorのオブジェクトを文字列に変更する
 * @error errorのオブジェクト
 * @returns 変更した文字列
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function errorToString(error: any) {
  const tryConvertedString = JSON.stringify(error !== undefined ? error : {});
  if (
    tryConvertedString === '{}' ||
    tryConvertedString === '' ||
    tryConvertedString === undefined ||
    tryConvertedString === null
  ) {
    return error;
  } else {
    return tryConvertedString;
  }
}
