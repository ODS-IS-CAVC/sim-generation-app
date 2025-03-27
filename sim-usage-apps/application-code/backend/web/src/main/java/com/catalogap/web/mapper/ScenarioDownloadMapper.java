package com.catalogap.web.mapper;

import com.catalogap.applicationcore.scenariodownload.ScenarioDownloadDomainEntity;
import com.catalogap.web.controller.dto.scenariodownload.DownloadScenarioDataResponse;

/**
 * ScenarioDownloadController のマッパーです.
 */

public class ScenarioDownloadMapper {
  /**
   * {@link ScenarioDownloadDomainEntity} オブジェクトを {@link DownloadScenarioDataResponse} に変換します.
   *
   * @param scenarioDownloadDomainEntity オブジェクト.
   * @return {@link DownloadScenarioDataResponse} オブジェクト.
   */
  public static DownloadScenarioDataResponse convertToDownloadScenarioDataResponse(
      ScenarioDownloadDomainEntity scenarioDownloadDomainEntity) {
    if (scenarioDownloadDomainEntity == null) {
      return null;
    }
    DownloadScenarioDataResponse.ScenarioDownloadData scenarioDataDownloadResponse =
        new DownloadScenarioDataResponse.ScenarioDownloadData();
    if (scenarioDownloadDomainEntity.getDownloadUrl() != null) {
      scenarioDataDownloadResponse.setDownloadUrl(scenarioDownloadDomainEntity.getDownloadUrl());
    }
    DownloadScenarioDataResponse downloadScenarioDataResponse = new DownloadScenarioDataResponse();
    downloadScenarioDataResponse.setResults(scenarioDataDownloadResponse);
    return downloadScenarioDataResponse;
  }
}
