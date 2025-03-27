package com.catalogap.web.controller.dto.frontendlog;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * フロントエンドログ出力 API のリクエストです.
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class UploadFrontendLogRequest {

  /**
   * ログレベル.
   */
  private String level;

  /**
   * ログ内容.
   */
  private String content;

  /**
   * ファイル.
   */
  private String fileName;

  /**
   * メソッド.
   */
  private String functionName;

}
