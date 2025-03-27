package com.catalogap.systemcommon.util;

import com.catalogap.systemcommon.constant.SystemPropertyConstants;
import com.catalogap.systemcommon.exception.LogicException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


/**
 * logに関する関数ツールです.
 */
public class LogUtil {
  private static final Logger appLog =
      LoggerFactory.getLogger(SystemPropertyConstants.APPLICATION_LOG_LOGGER);

  /**
   * 引数に渡されたメッセージをERRORレベルでログに出力します.
   *
   * @param message メッセージ.
   */
  public static void error(String message) {
    appLog.error(message);
  }

  /**
   * 指定されたIDのメッセージをERRORレベルでログに出力します.
   *
   * @param id ID.
   * @param placeholder プレースホルダ.
   */
  public static void error(String id, String[] placeholder) {
    appLog.error(MessageUtil.getMessage(id, placeholder));
  }

  /**
   * 指定された例外に対応するメッセージをERRORレベルでログに出力します.
   *
   * @param ex 異常.
   */
  public static void error(LogicException ex) {
    error(ex.getExceptionId(), ex.getLogMessageValue());
  }

  /**
   * 引数に渡されたメッセージをINFOレベルでログに出力します.
   *
   * @param message メッセージ.
   */
  public static void info(String message) {
    appLog.info(message);
  }

  /**
   * 指定されたIDのメッセージをINFOレベルでログに出力します.
   *
   * @param id ID.
   * @param placeholder プレースホルダ.
   */
  public static void info(String id, String[] placeholder) {
    appLog.info(MessageUtil.getMessage(id, placeholder));
  }

  /**
   * 指定された例外に対応するメッセージをINFOレベルでログに出力します.
   *
   * @param ex 異常.
   */
  public static void info(LogicException ex) {
    info(ex.getExceptionId(), ex.getLogMessageValue());
  }


  /**
   * 引数に渡されたメッセージをWARNレベルでログに出力します.
   *
   * @param message メッセージ.
   */
  public static void warn(String message) {
    appLog.warn(message);
  }

  /**
   * 指定されたIDのメッセージをWARNレベルでログに出力します.
   *
   * @param id ID.
   * @param placeholder プレースホルダ.
   */
  public static void warn(String id, String[] placeholder) {
    appLog.warn(MessageUtil.getMessage(id, placeholder));
  }

  /**
   * 指定された例外に対応するメッセージをWARNレベルでログに出力します.
   *
   * @param ex 異常.
   */
  public static void warn(LogicException ex) {
    warn(ex.getExceptionId(), ex.getLogMessageValue());
  }

  /**
   * 引数に渡されたメッセージをDEBUGレベルでログに出力します.
   *
   * @param message メッセージ.
   */
  public static void debug(String message) {
    appLog.debug(message);
  }

  /**
   * 指定されたIDのメッセージをDEBUGレベルでログに出力します.
   *
   * @param id ID.
   * @param placeholder プレースホルダ.
   */
  public static void debug(String id, String[] placeholder) {
    appLog.debug(MessageUtil.getMessage(id, placeholder));
  }

  /**
   * 指定された例外に対応するメッセージをDEBUGレベルでログに出力します.
   *
   * @param ex 異常.
   */
  public static void debug(LogicException ex) {
    debug(ex.getExceptionId(), ex.getLogMessageValue());
  }

}
