package com.catalogap.applicationcore.frontendlog;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * フロントエンドログドメインエンティティ.
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class FrontendLogDomainEntity {
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
