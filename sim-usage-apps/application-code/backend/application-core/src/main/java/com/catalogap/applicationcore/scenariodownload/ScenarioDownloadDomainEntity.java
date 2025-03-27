package com.catalogap.applicationcore.scenariodownload;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * シナリオダウンロードドメインエンティティです.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioDownloadDomainEntity {

  /*
   * シナリオデータのダウンロードurl.
   */
  private String downloadUrl;

  /*
   * 区間ID.
   */
  private String sectionId;
}
