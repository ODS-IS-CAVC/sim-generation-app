package com.catalogap.web.controller.dto.scenarioinfo;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * GET シナリオリスト API のレスポンスです.
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class GetScenarioListResponse {

  /**
   * シナリオ情報.
   */
  private GetScenarioListInfo results;

  /**
   * GetScenarioListInfo内部データ.
   */
  @Data
  @AllArgsConstructor
  @NoArgsConstructor
  public static class GetScenarioListInfo {

    /**
     * 検索結果のレコード数.
     */
    private int counts;

    /**
     * シナリオ情報リスト.
     */
    private List<ScenarioInfo> lists;

    /**
     * ScenarioInfo内部データ.
     */
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class ScenarioInfo {

      /**
       * ヒヤリハット種別リスト.
       */
      private List<NearmissTypeInfo> nearmissTypeList;

      /**
       * 署名付き動画サムネル画像URL.
       */
      private String videoThumbnailUrl;

      /**
       * 区間名.
       */
      private String sectionName;

      /**
       * 場所名.
       */
      private String locationName;

      /**
       * UUID.
       */
      private String uuid;

      /**
       * NearmissTypeInfo内部データ.
       */
      @Data
      @AllArgsConstructor
      @NoArgsConstructor
      public static class NearmissTypeInfo {

        /**
         * ヒヤリハット種別.
         */
        private String nearmissType;
      }
    }
  }
}
