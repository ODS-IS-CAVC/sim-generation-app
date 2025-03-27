package com.catalogap.infrastructure.repository.translator;

import com.catalogap.applicationcore.scenarioinfo.ScenarioInfoDomainEntity;
import com.catalogap.infrastructure.repository.mybatis.entity.ScenarioInfoEntity;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.DlAuth;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.SearchAuth;
import org.springframework.beans.BeanUtils;

/**
 * エンティティオブジェクトをドメインオブジェクトに変換するユーティリティ.
 */
public class ScenarioInfoDomainEntityTranslator {

  /**
   * {@link SearchAuth} オブジェクトを {@link ScenarioInfoDomainEntity} に変換します.
   *
   * @param searchAuth オブジェクト.
   * @return {@link ScenarioInfoDomainEntity} オブジェクト.
   */
  public static ScenarioInfoDomainEntity translatorSearchAuthToDomainEntity(SearchAuth searchAuth) {
    if (searchAuth == null) {
      return null;
    }
    ScenarioInfoDomainEntity scenarioInfoDomainEntity = new ScenarioInfoDomainEntity();
    BeanUtils.copyProperties(searchAuth, scenarioInfoDomainEntity);
    return scenarioInfoDomainEntity;
  }

  /**
   * {@link ScenarioInfoEntity} オブジェクトを {@link ScenarioInfoDomainEntity} に変換します.
   *
   * @param scenarioInfoEntity オブジェクト.
   * @return {@link ScenarioInfoDomainEntity} オブジェクト.
   */
  public static ScenarioInfoDomainEntity translatorScenarioInfoEntityToDomainEntity(
      ScenarioInfoEntity scenarioInfoEntity) {
    if (scenarioInfoEntity == null) {
      return null;
    }
    ScenarioInfoDomainEntity scenarioInfoDomainEntity = new ScenarioInfoDomainEntity();
    BeanUtils.copyProperties(scenarioInfoEntity, scenarioInfoDomainEntity);
    scenarioInfoDomainEntity.setNearmissTypeWithComma(scenarioInfoEntity.getNewNearmissType());
    return scenarioInfoDomainEntity;
  }

  /**
   * {@link DlAuth} オブジェクトを {@link ScenarioInfoDomainEntity} に変換します.
   *
   * @param dlAuth オブジェクト.
   * @return {@link ScenarioInfoDomainEntity} オブジェクト.
   */
  public static ScenarioInfoDomainEntity translatorDlAuthToDomainEntity(DlAuth dlAuth) {
    if (dlAuth == null) {
      return null;
    }
    ScenarioInfoDomainEntity scenarioInfoDomainEntity = new ScenarioInfoDomainEntity();
    BeanUtils.copyProperties(dlAuth, scenarioInfoDomainEntity);
    return scenarioInfoDomainEntity;
  }
}
