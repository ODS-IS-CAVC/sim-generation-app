package com.catalogap.infrastructure.repository;

import com.catalogap.applicationcore.scenarioinfo.ScenarioInfoDomainEntity;
import com.catalogap.applicationcore.scenarioinfo.ScenarioInfoRepository;
import com.catalogap.infrastructure.repository.mybatis.entity.ScenarioInfoEntity;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.DlAuth;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.DlAuthExample;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.DlAuthExample.Criteria;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.SearchAuth;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.SearchAuthExample;
import com.catalogap.infrastructure.repository.mybatis.generated.mapper.DlAuthMapper;
import com.catalogap.infrastructure.repository.mybatis.generated.mapper.SearchAuthMapper;
import com.catalogap.infrastructure.repository.mybatis.mapper.CustomScenarioInfoMapper;
import com.catalogap.infrastructure.repository.translator.ScenarioInfoDomainEntityTranslator;
import io.micrometer.common.util.StringUtils;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

/**
 * ScenarioInfoRepositoryを実装したリポジトリクラス.
 */
@Repository
public class MyBatisScenarioInfoRepository implements ScenarioInfoRepository {

  @Autowired
  private CustomScenarioInfoMapper customScenarioInfoMapper;

  @Autowired
  private DlAuthMapper dlAuthMapper;

  @Autowired
  private SearchAuthMapper searchAuthMapper;

  /**
   * ユーザーの検索権限を取得する.
   *
   * @param userId ユーザーID.
   * @return ユーザーの検索権限
   */
  @Override
  public List<ScenarioInfoDomainEntity> getSearchAuth(String userId) {
    SearchAuthExample searchAuthExample = new SearchAuthExample();
    SearchAuthExample.Criteria criteria = searchAuthExample.createCriteria();
    criteria.andEmailAddressEqualTo(userId);
    criteria.andDeleteFlagEqualTo("0");

    List<SearchAuth> searchAuthList = searchAuthMapper.selectByExample(searchAuthExample);
    List<ScenarioInfoDomainEntity> scenarioInfoDomainEntityList =
        new ArrayList<ScenarioInfoDomainEntity>();
    if (searchAuthList.size() > 0) {
      for (SearchAuth searchAuth : searchAuthList) {
        ScenarioInfoDomainEntity scenarioInfoDomainEntity =
            ScenarioInfoDomainEntityTranslator.translatorSearchAuthToDomainEntity(searchAuth);
        scenarioInfoDomainEntityList.add(scenarioInfoDomainEntity);
      }

    }
    return scenarioInfoDomainEntityList;
  }

  /**
   * シナリオ情報リストを取得する.
   *
   * @param nearmissType ヒヤリハット種別.
   * @param skipRows スキップしたいレコード数.
   * @param itemsPerPage 1ページあたりのレコード数.
   * @param userId ユーザID.
   * @param happenTime 発生日時.
   * @param happenSection 発生区間.
   * @param happenLocation 発生場所.
   * @return シナリオ情報リスト
   */
  @Override
  public List<ScenarioInfoDomainEntity> getScenarioList(List<String> nearmissType, int skipRows,
      int itemsPerPage, String userId, String happenTime, String happenSection,
      String happenLocation) {
    Map<String, Object> params = new HashMap<>();
    params.put("skipRows", skipRows);
    params.put("itemsPerPage", itemsPerPage);

    if (nearmissType != null && nearmissType.size() != 0) {
      params.put("nearmissType", nearmissType);
    }
    if (StringUtils.isNotBlank(userId)) {
      params.put("userId", userId);
    }
    if (StringUtils.isNotBlank(happenTime)) {
      params.put("happenTime", happenTime);
    }
    if (StringUtils.isNotBlank(happenSection)) {
      params.put("happenSection", happenSection);
    }
    if (StringUtils.isNotBlank(happenLocation)) {
      params.put("happenLocation", happenLocation);
    }
    List<ScenarioInfoEntity> scenarioInfoRet = customScenarioInfoMapper.getScenarioList(params);
    List<ScenarioInfoDomainEntity> scenarioInfoList = new ArrayList<ScenarioInfoDomainEntity>();
    for (ScenarioInfoEntity scenarioInfoEntity : scenarioInfoRet) {
      ScenarioInfoDomainEntity scenarioInfoDomainEntity = ScenarioInfoDomainEntityTranslator
          .translatorScenarioInfoEntityToDomainEntity(scenarioInfoEntity);
      scenarioInfoList.add(scenarioInfoDomainEntity);
    }
    return scenarioInfoList;
  }

  /**
   * シナリオ情報数量を取得する.
   *
   * @param nearmissType ヒヤリハット種別.
   * @param userId ユーザID.
   * @param happenTime 発生日時.
   * @param happenSection 発生区間.
   * @param happenLocation 発生場所.
   * @return シナリオ情報数量
   */
  @Override
  public int getScenarioCount(List<String> nearmissType, String userId, String happenTime,
      String happenSection, String happenLocation) {
    Map<String, Object> params = new HashMap<>();
    if (nearmissType != null && nearmissType.size() != 0) {
      params.put("nearmissType", nearmissType);
    }
    if (StringUtils.isNotBlank(userId)) {
      params.put("userId", userId);
    }
    if (StringUtils.isNotBlank(happenTime)) {
      params.put("happenTime", happenTime);
    }
    if (StringUtils.isNotBlank(happenSection)) {
      params.put("happenSection", happenSection);
    }
    if (StringUtils.isNotBlank(happenLocation)) {
      params.put("happenLocation", happenLocation);
    }
    int scenarioInfoCount = customScenarioInfoMapper.getScenarioCount(params);
    return scenarioInfoCount;
  }

  /**
   * シナリオ情報を取得する.
   *
   * @param uuid UUID.
   * @return シナリオ情報
   */
  @Override
  public ScenarioInfoDomainEntity getScenarioDetailInfo(String uuid) {
    Map<String, Object> params = new HashMap<>();
    if (StringUtils.isNotBlank(uuid)) {
      params.put("uuid", uuid);
    }
    ScenarioInfoEntity scenarioDetailInfo = customScenarioInfoMapper.getScenarioDetailInfo(params);
    ScenarioInfoDomainEntity scenarioInfoDomainEntity = ScenarioInfoDomainEntityTranslator
        .translatorScenarioInfoEntityToDomainEntity(scenarioDetailInfo);
    return scenarioInfoDomainEntity;
  }

  /**
   * ダウンロード認可情報を取得する.
   *
   * @param userId ユーザーID.
   * @return ダウンロード認可情報
   */
  @Override
  public ScenarioInfoDomainEntity downloadAuth(String userId) {
    DlAuthExample dlAuthExample = new DlAuthExample();
    Criteria criteria = dlAuthExample.createCriteria();
    criteria.andEmailAddressEqualTo(userId);
    criteria.andDeleteFlagEqualTo("0");

    ScenarioInfoDomainEntity scenarioInfoDomainEntity = new ScenarioInfoDomainEntity();
    List<DlAuth> dlAuthList = dlAuthMapper.selectByExample(dlAuthExample);
    if (dlAuthList.size() > 0) {
      DlAuth dlAuth = dlAuthList.get(0);
      scenarioInfoDomainEntity =
          ScenarioInfoDomainEntityTranslator.translatorDlAuthToDomainEntity(dlAuth);
    }
    return scenarioInfoDomainEntity;
  }

}
