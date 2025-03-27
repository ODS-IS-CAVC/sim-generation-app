package com.catalogap.web.controller.dto.scenariocode;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * GET コードリスト API のレスポンスです.
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class GetCodeListResponse {

  /**
   * コードデータ.
   */
  private GetCodeListInfo results;

  /**
   * GetCodeListInfo内部データ.
   */
  @Data
  @AllArgsConstructor
  @NoArgsConstructor
  public static class GetCodeListInfo {

    /**
     * ヒヤリハット種別.
     */
    private List<NearMissInfo> nearmissType;

    /**
     * 発生区間.
     */
    private List<HappenSectionInfo> happenSection;

    /**
     * NearMissInfo内部データ.
     */
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class NearMissInfo {

      /**
       * ヒヤリハットコード.
       */
      private String code;

      /**
       * ヒヤリハット値.
       */
      private String value;
    }

    /**
     * HappenSectionInfo内部データ.
     */
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class HappenSectionInfo {

      /**
       * 区間ID.
       */
      private String sectionId;

      /**
       * 区間名.
       */
      private String sectionName;
    }
  }
}
