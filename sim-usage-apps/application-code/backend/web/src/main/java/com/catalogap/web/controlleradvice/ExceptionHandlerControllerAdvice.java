package com.catalogap.web.controlleradvice;

import com.catalogap.systemcommon.constant.MessageIdConstant;
import com.catalogap.systemcommon.constant.SystemPropertyConstants;
import com.catalogap.systemcommon.exception.LogicException;
import com.catalogap.systemcommon.exception.SystemException;
import com.catalogap.systemcommon.exception.response.ErrorResponse;
import com.catalogap.systemcommon.util.MessageUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ConstraintViolationException;
import java.io.PrintWriter;
import java.io.StringWriter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataAccessException;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

/**
 * コントローラーのアドバイスクラスです.
 */
@ControllerAdvice
public class ExceptionHandlerControllerAdvice extends ResponseEntityExceptionHandler {

  private static Logger appLog =
      LoggerFactory.getLogger(SystemPropertyConstants.APPLICATION_LOG_LOGGER);

  // Junitテストために、追加する。Junit中にだけを利用してください。
  public static void setLogger(Logger logger) {
    appLog = logger;
  }

  /**
   * 入力チェックエラー（コントローラの引数：@RequestBody Dto）の場合ステータースコード400で返却する.
   *
   * @param ex 入力チェック例外.
   * @param headers リクエストヘッダー.
   * @param status HTTPステータスコード.
   * @param request リクエスト.
   * @return ステータースコード400のレスポンス.
   */
  @Override
  protected ResponseEntity<Object> handleMethodArgumentNotValid(MethodArgumentNotValidException ex,
      HttpHeaders headers, HttpStatusCode status, WebRequest request) {

    StringBuilder errorMessage = new StringBuilder();
    for (FieldError fieldError : ex.getBindingResult().getFieldErrors()) {
      errorMessage.append(fieldError.getDefaultMessage()).append(";");
    }

    // 最後の「;」を削除する
    if (errorMessage.length() > 0) {
      errorMessage.deleteCharAt(errorMessage.length() - 1);
    }

    LogicException le = new LogicException(ex, MessageIdConstant.E4V001,
        new String[] {errorMessage.toString().trim()});
    appLog.debug(createLogMessageStackTrace(le, le.getExceptionId(), le.getLogMessageValue()));
    return ResponseEntity.status(HttpStatus.BAD_REQUEST).contentType(MediaType.APPLICATION_JSON)
        .body(new ErrorResponse(le));
  }


  /**
   * 入力チェックエラー（コントローラの引数に直接@Validをかける）の場合ステータースコード400で返却する.
   *
   * @param ex 入力チェック例外.
   * @param request リクエスト.
   * @return ステータースコード400のレスポンス.
   */
  @ExceptionHandler(ConstraintViolationException.class)
  public ResponseEntity<ErrorResponse> handleConstraintViolation(ConstraintViolationException ex,
      WebRequest request) {
    StringBuilder errorMessage = new StringBuilder();
    for (ConstraintViolation<?> violation : ex.getConstraintViolations()) {
      errorMessage.append(violation.getMessage()).append(";");
    }

    // 最後の「;」を削除する
    if (errorMessage.length() > 0) {
      errorMessage.deleteCharAt(errorMessage.length() - 1);
    }
    LogicException le = new LogicException(ex, MessageIdConstant.E4V001,
        new String[] {errorMessage.toString().trim()});
    appLog.debug(createLogMessageStackTrace(le, le.getExceptionId(), le.getLogMessageValue()));
    return ResponseEntity.status(HttpStatus.BAD_REQUEST).contentType(MediaType.APPLICATION_JSON)
        .body(new ErrorResponse(le));
  }

  /**
   * その他の業務エラーをステータースコード400で返却する.
   *
   * @param e 業務例外.
   * @param req リクエスト.
   * @return ステータースコード400のレスポンス.
   */
  @ExceptionHandler(LogicException.class)
  public ResponseEntity<ErrorResponse> handleLogicException(LogicException e,
      HttpServletRequest req) {
    appLog.error(createLogMessageStackTrace(e, e.getExceptionId(), e.getLogMessageValue()));
    return ResponseEntity.status(HttpStatus.BAD_REQUEST).contentType(MediaType.APPLICATION_JSON)
        .body(new ErrorResponse(e));
  }

  /**
   * DBアクセス時のシステムエラーをステータースコード500で返却する.
   *
   * @param e DBアクセス例外.
   * @param req リクエスト.
   * @return ステータースコード500のレスポンス.
   */
  @ExceptionHandler(DataAccessException.class)
  public ResponseEntity<ErrorResponse> handleException(DataAccessException e,
      HttpServletRequest req) {
    SystemException ex =
        new SystemException(e, MessageIdConstant.E5D001, new String[] {e.getMessage()});
    appLog.error(createLogMessageStackTrace(ex, ex.getExceptionId(), ex.getLogMessageValue()));
    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
        .contentType(MediaType.APPLICATION_JSON).body(new ErrorResponse(ex));
  }

  /**
   * その他のシステムエラーをステータースコード500で返却する.
   *
   * @param e その他の例外.
   * @param req リクエスト.
   * @return ステータースコード500のレスポンス.
   */
  @ExceptionHandler(SystemException.class)
  public ResponseEntity<ErrorResponse> handleException(SystemException e, HttpServletRequest req) {
    appLog.error(createLogMessageStackTrace(e, e.getExceptionId(), e.getLogMessageValue()));
    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
        .contentType(MediaType.APPLICATION_JSON).body(new ErrorResponse(e));
  }

  /**
   * 上記のいずれにも当てはまらない例外をステータースコード500で返却する.
   *
   * @param e その他の例外.
   * @param req リクエスト.
   * @return ステータースコード500のレスポンス.
   */
  @ExceptionHandler(Exception.class)
  public ResponseEntity<ErrorResponse> handleException(Exception e, HttpServletRequest req) {
    appLog.error(createLogMessageStackTrace(e, MessageIdConstant.E5S001, null));
    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
        .contentType(MediaType.APPLICATION_JSON)
        .body(new ErrorResponse(new SystemException(e, MessageIdConstant.E5S001, null)));
  }

  /**
   * ログメッセージを作成する.
   *
   * @param e 例外.
   * @param exceptionId 例外のID.
   * @param logMessageValue メッセージ.
   * @return ログメッセージ.
   */
  public static String createLogMessageStackTrace(Exception e, String exceptionId,
      String[] logMessageValue) {
    StringBuilder builder = new StringBuilder();
    String exceptionMessage = MessageUtil.getMessage(exceptionId, logMessageValue);
    builder.append(exceptionId).append(" ").append(exceptionMessage)
        .append(SystemPropertyConstants.LINE_SEPARATOR);
    StringWriter writer = new StringWriter();
    e.printStackTrace(new PrintWriter(writer));
    builder.append(writer.getBuffer().toString());
    return builder.toString();
  }

}
