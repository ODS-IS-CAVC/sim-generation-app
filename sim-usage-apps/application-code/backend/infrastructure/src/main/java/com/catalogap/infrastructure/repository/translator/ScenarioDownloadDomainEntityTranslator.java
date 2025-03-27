package com.catalogap.infrastructure.repository.translator;

import com.catalogap.applicationcore.scenariodownload.ScenarioDownloadDomainEntity;
import com.catalogap.infrastructure.repository.mybatis.entity.ScenarioInfoEntity;
import org.springframework.beans.BeanUtils;

/**
 * エンティティオブジェクトをドメインオブジェクトに変換するユーティリティ.
 */
public class ScenarioDownloadDomainEntityTranslator {
  /**
   * {@link ScenarioInfoEntity} オブジェクトを {@link ScenarioDownloadDomainEntity} に変換します.
   *
   * @param scenarioInfoEntity オブジェクト.
   * @return {@link ScenarioDownloadDomainEntity} オブジェクト.
   */
  public static ScenarioDownloadDomainEntity translatorScenarioDownloadDomainEntity(
      ScenarioInfoEntity scenarioInfoEntity) {
    if (scenarioInfoEntity == null) {
      return null;
    }
    ScenarioDownloadDomainEntity scenarioDownloadDomainEntity = new ScenarioDownloadDomainEntity();
    BeanUtils.copyProperties(scenarioInfoEntity, scenarioDownloadDomainEntity);
    return scenarioDownloadDomainEntity;
  }
}
