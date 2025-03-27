package com.catalogap.web.controller.dto.scenarioinfo;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.validator.constraints.Length;

/**
 * GET シナリオリスト API のリクエストです.
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class GetScenarioListRequest {
  /**
   * ヒヤリハット種別.
   */
  @Valid
  private List<@Length(min = 3, max = 3, message = "「ヒヤリハット種別」の長さが無効です") String> nearmissType;

  /**
   * 発生日時.
   */
  private String happenTime;

  /**
   * 発生区間.
   */
  private String happenSection;

  /**
   * 発生場所.
   */
  private String happenLocation;

  /**
   * 要求ページ番号.
   */
  @NotNull(message = "要求ページ番号が必要です")
  private Integer requestPage;

  /**
   * 1ページあたりのレコード数.
   */
  @NotNull(message = "1ページあたりのレコード数が必要です")
  private Integer itemsPerPage;

}
