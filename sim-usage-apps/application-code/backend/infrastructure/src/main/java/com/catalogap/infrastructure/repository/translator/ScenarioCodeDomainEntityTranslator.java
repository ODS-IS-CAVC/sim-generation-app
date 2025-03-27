package com.catalogap.infrastructure.repository.translator;

import com.catalogap.applicationcore.scenariocode.ScenarioCodeDomainEntity;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.LocationMaster;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.SearchCodeMaster;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.SectionMaster;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.springframework.beans.BeanUtils;

/**
 * エンティティオブジェクトをドメインオブジェクトに変換するユーティリティ.
 */
public class ScenarioCodeDomainEntityTranslator {

  /**
   * サーチコードマスタオブジェクトをシナリオコードドメインエンティティリストに変換する.
   *
   * @param searchCodeMaster オブジェクト.
   * @return シナリオコードリスト.
   */
  public static List<ScenarioCodeDomainEntity> translatorToCore(SearchCodeMaster searchCodeMaster) {
    List<ScenarioCodeDomainEntity> scenarioCodeDomainEntityList = new ArrayList<>();

    Object typeOjb = searchCodeMaster.getType();
    Object choiceOjb = searchCodeMaster.getChoice();
    if (typeOjb != null && choiceOjb != null) {
      @SuppressWarnings("unchecked")
      Map<String, String> typeMap = (Map<String, String>) typeOjb;
      Map.Entry<String, String> firstEntry = typeMap.entrySet().iterator().next();
      String codeType = firstEntry.getKey();

      @SuppressWarnings("unchecked")
      Map<String, String> codeMap = (Map<String, String>) choiceOjb;

      for (Map.Entry<String, String> entry : codeMap.entrySet()) {
        ScenarioCodeDomainEntity domainEntity = new ScenarioCodeDomainEntity();
        domainEntity.setCode(entry.getKey());
        domainEntity.setValue(entry.getValue());
        domainEntity.setCodeType(codeType);
        scenarioCodeDomainEntityList.add(domainEntity);
      }
    }

    return scenarioCodeDomainEntityList;
  }

  /**
   * {@link SectionMaster} オブジェクトを {@link ScenarioCodeDomainEntity} に変換します.
   *
   * @param sectionMaster オブジェクト.
   * @return {@link ScenarioCodeDomainEntity} オブジェクト.
   */
  public static ScenarioCodeDomainEntity translatorToCore(SectionMaster sectionMaster) {
    if (sectionMaster == null) {
      return null;
    }
    ScenarioCodeDomainEntity scenarioCodeDomainEntity = new ScenarioCodeDomainEntity();
    BeanUtils.copyProperties(sectionMaster, scenarioCodeDomainEntity);
    return scenarioCodeDomainEntity;
  }

  /**
   * {@link LocationMaster} オブジェクトを {@link ScenarioCodeDomainEntity} に変換します.
   *
   * @param locationMaster オブジェクト.
   * @return {@link ScenarioCodeDomainEntity} オブジェクト.
   */
  public static ScenarioCodeDomainEntity translatorToCore(LocationMaster locationMaster) {
    if (locationMaster == null) {
      return null;
    }
    ScenarioCodeDomainEntity scenarioCodeDomainEntity = new ScenarioCodeDomainEntity();
    BeanUtils.copyProperties(locationMaster, scenarioCodeDomainEntity);
    return scenarioCodeDomainEntity;
  }
}
