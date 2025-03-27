package com.catalogap.web.controller.dto.scenariodownload;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * ダウンロード シナリオデータ API のリクエストです.
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class DownloadScenarioDataRequest {
  /**
   * UUID.
   */
  @NotEmpty(message = "シナリオのIDは必須です")
  private String uuid;

  /**
   * データ区分.
   */
  @NotNull(message = "データ区分は必須です")
  private String dataDivision;

}
