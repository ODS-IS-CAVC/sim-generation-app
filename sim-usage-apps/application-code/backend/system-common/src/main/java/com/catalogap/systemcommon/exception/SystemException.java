package com.catalogap.systemcommon.exception;

import lombok.Getter;
import lombok.Setter;

/**
 * システム例外を表す例外クラスです.
 */
@Getter
@Setter
public class SystemException extends RuntimeException {

  private String exceptionId = null;

  private String[] logMessageValue = null;

  /**
   * コンストラクタ.
   *
   * @param cause 原因例外.
   * @param exceptionId 例外ID.
   * @param logMessageValue メッセージ用プレースフォルダ（ログ用）.
   */
  public SystemException(Throwable cause, String exceptionId, String[] logMessageValue) {
    super(cause);
    this.exceptionId = exceptionId;
    this.logMessageValue = logMessageValue;
  }
}
