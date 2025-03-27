package com.catalogap.web.controller.dto.scenariocode;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * GET 場所データリスト API のレスポンスです.
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class GetLocationListResponse {

  /**
   * コードデータ.
   */
  private GetLocationListInfo results;

  /**
   * GetLocationListInfo内部データ.
   */
  @Data
  @AllArgsConstructor
  @NoArgsConstructor
  public static class GetLocationListInfo {

    /**
     * 発生場所.
     */
    private List<LocationData> happenLocation;

    /**
     * LocationData内部データ.
     */
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class LocationData {

      /**
       * 場所ID.
       */
      private String locationId;

      /**
       * 場所名.
       */
      private String locationName;

    }
  }
}
