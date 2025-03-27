package com.catalogap.systemcommon.exception.response;

import com.catalogap.systemcommon.exception.LogicException;
import com.catalogap.systemcommon.exception.SystemException;
import com.catalogap.systemcommon.util.MessageUtil;
import lombok.Getter;
import lombok.Setter;
import org.slf4j.MDC;

/**
 * エラーレスポンス。 フロントへのレスポンスボディにJSONでマッピングされるエラー情報のクラス.
 */
@Getter
@Setter
public class ErrorResponse {
  /**
   * エラーコード.
   */
  private String code;

  /** エラーコードに対応するメッセージ. */
  private String message;

  /** リクエストID. */
  private String requestId;

  /** MDCに保存したのリクエストIDのキー. */
  public static final String DEFAULT_MDC_UUID_TOKEN_KEY = "Slf4jMDCFilter.UUID";

  /** システム例外用コンストラクタ. */
  public ErrorResponse(SystemException e) {
    this.code = e.getExceptionId();
    this.message = MessageUtil.getMessage(e.getExceptionId(), e.getLogMessageValue());
    this.requestId = MDC.get(DEFAULT_MDC_UUID_TOKEN_KEY);
  }

  /** 業務例外用コンストラクタ. */
  public ErrorResponse(LogicException e) {
    this.code = e.getExceptionId();
    this.message = MessageUtil.getMessage(e.getExceptionId(), e.getLogMessageValue());
    this.requestId = MDC.get(DEFAULT_MDC_UUID_TOKEN_KEY);
  }
}
