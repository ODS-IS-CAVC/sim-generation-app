package com.catalogap.infrastructure.repository;

import com.catalogap.applicationcore.scenariocode.ScenarioCodeDomainEntity;
import com.catalogap.applicationcore.scenariocode.ScenarioCodeRepository;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.LocationMaster;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.SearchCodeMaster;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.SearchCodeMasterExample;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.SectionMaster;
import com.catalogap.infrastructure.repository.mybatis.generated.mapper.SearchCodeMasterMapper;
import com.catalogap.infrastructure.repository.mybatis.mapper.CustomScenarioCodeMapper;
import com.catalogap.infrastructure.repository.translator.ScenarioCodeDomainEntityTranslator;
import io.micrometer.common.util.StringUtils;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

/**
 * ScenarioCodeRepositoryを実装したリポジトリクラス.
 */
@Repository
public class MyBatisScenarioCodeRepository implements ScenarioCodeRepository {

  @Autowired
  SearchCodeMasterMapper searchCodeMasterMapper;


  @Autowired
  CustomScenarioCodeMapper customScenarioCodeMapper;

  /**
   * 検索条件コード値マスタから種別データを取得する.
   *
   * @return 種別データ
   */
  @Override
  public List<ScenarioCodeDomainEntity> getCodeList() {
    SearchCodeMasterExample searchCodeMasterExample = new SearchCodeMasterExample();
    searchCodeMasterExample.setOrderByClause("id");
    SearchCodeMasterExample.Criteria criteria = searchCodeMasterExample.createCriteria();
    criteria.andDeleteFlagEqualTo("0");

    // 種別データを取得する
    List<SearchCodeMaster> searchCodeList =
        searchCodeMasterMapper.selectByExample(searchCodeMasterExample);

    List<ScenarioCodeDomainEntity> scenarioCodeList = new ArrayList<ScenarioCodeDomainEntity>();

    // シナリオコードリストを設定する
    if (searchCodeList != null && searchCodeList.size() > 0) {
      for (SearchCodeMaster searchCodeMaster : searchCodeList) {
        List<ScenarioCodeDomainEntity> scenarioCodeDomainEntityList =
            ScenarioCodeDomainEntityTranslator.translatorToCore(searchCodeMaster);
        scenarioCodeList.addAll(scenarioCodeDomainEntityList);
      }
    }

    return scenarioCodeList;
  }

  /**
   * 区間マスタと検索認可から発生区間データを取得する.
   *
   * @param userId ユーザーID.
   * @return 発生区間データ
   */
  @Override
  public List<ScenarioCodeDomainEntity> getSectionList(String userId) {
    Map<String, Object> params = new HashMap<>();
    if (StringUtils.isNotBlank(userId)) {
      params.put("userId", userId);
    }

    // 発生区間リストを取得する
    List<SectionMaster> sectionMasterList = customScenarioCodeMapper.selectHappenSection(params);
    List<ScenarioCodeDomainEntity> happenSectionList = new ArrayList<ScenarioCodeDomainEntity>();
    for (SectionMaster sectionMaster : sectionMasterList) {
      ScenarioCodeDomainEntity scenarioCodeDomainEntity =
          ScenarioCodeDomainEntityTranslator.translatorToCore(sectionMaster);
      happenSectionList.add(scenarioCodeDomainEntity);
    }

    return happenSectionList;
  }

  /**
   * 場所マスタから場所データを取得する.
   *
   * @param sectionId 区間ID
   * @param userId ユーザーID
   * @return 場所データ
   */
  @Override
  public List<ScenarioCodeDomainEntity> getLocationList(String sectionId, String userId) {

    Map<String, Object> params = new HashMap<>();
    if (StringUtils.isNotBlank(sectionId)) {
      params.put("sectionId", sectionId);
    }
    if (StringUtils.isNotBlank(userId)) {
      params.put("userId", userId);
    }

    // 発生場所リストを取得する
    List<LocationMaster> locationList = customScenarioCodeMapper.selectHappenLocation(params);

    List<ScenarioCodeDomainEntity> locationListResults = new ArrayList<ScenarioCodeDomainEntity>();

    // 返却値を設定する
    for (LocationMaster locationMaster : locationList) {
      ScenarioCodeDomainEntity scenarioCodeDomainEntity =
          ScenarioCodeDomainEntityTranslator.translatorToCore(locationMaster);
      locationListResults.add(scenarioCodeDomainEntity);

    }
    return locationListResults;
  }
}
