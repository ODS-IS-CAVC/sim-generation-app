package com.catalogap.web.controller.dto.scenariodownload;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * ダウンロード シナリオデータ API のレスポンスです.
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class DownloadScenarioDataResponse {

  /**
   * シナリオデータダウンロード結果.
   */
  private ScenarioDownloadData results;

  /**
   * ScenarioDownloadData内部データ.
   */
  @Data
  @AllArgsConstructor
  @NoArgsConstructor
  public static class ScenarioDownloadData {

    /**
     * シナリオデータのダウンロードurl.
     */
    private String downloadUrl;

  }
}
