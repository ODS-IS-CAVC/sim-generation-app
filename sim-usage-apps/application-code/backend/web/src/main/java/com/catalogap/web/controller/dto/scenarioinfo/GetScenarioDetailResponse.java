package com.catalogap.web.controller.dto.scenarioinfo;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * GET シナリオ情報詳細取得 API のレスポンスです.
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class GetScenarioDetailResponse {

  /**
   * シナリオ情報詳細.
   */
  private ScenarioDetailInfo results;

  /**
   * ScenarioDetailInfo内部データ.
   */
  @Data
  @AllArgsConstructor
  @NoArgsConstructor
  public static class ScenarioDetailInfo {

    /**
     * ID.
     */
    private String id;

    /**
     * ヒヤリハット種別リスト.
     */
    private List<NearmissTypeInfo> nearmissTypeList;

    /**
     * 署名付き動画URL.
     */
    private String videoUrl;

    /**
     * 署名付き動画サムネル画像URL.
     */
    private String videoThumbnailUrl;

    /**
     * シナリオ作成日時.
     */
    private String scenarioCreateTime;

    /**
     * 区間名.
     */
    private String sectionName;

    /**
     * 場所名.
     */
    private String locationName;

    /**
     * 緯度.
     */
    private String latitude;

    /**
     * 経度.
     */
    private String longitude;

    /**
     * UUID.
     */
    private String uuid;

    /**
     * シナリオデータリスト.
     */
    private List<ScenarioData> scenarioDataList;

    /**
     * 機械学習用データリスト.
     */
    private List<MachineLearningData> machineLearningDataList;

    /**
     * NearmissType内部データ.
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

    /**
     * ScenarioData内部データ.
     */
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class ScenarioData {

      /**
       * シナリオデータの名前.
       */
      private String name;

      /**
       * データ区分.
       */
      private String dataDivision;

      /**
       * シナリオデータのサイズ.
       */
      private String size;
    }

    /**
     * MachineLearningData内部データ.
     */
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class MachineLearningData {

      /**
       * 機械学習用データの名前.
       */
      private String name;

      /**
       * データ区分.
       */
      private String dataDivision;

      /**
       * 機械学習用データのサイズ.
       */
      private String size;
    }
  }
}
