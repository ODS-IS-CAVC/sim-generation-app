package com.catalogap.infrastructure.repository;

import com.catalogap.applicationcore.scenariodownload.ScenarioDownloadDomainEntity;
import com.catalogap.applicationcore.scenariodownload.ScenarioDownloadRepository;
import com.catalogap.infrastructure.repository.mybatis.entity.ScenarioInfoEntity;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.DlHistory;
import com.catalogap.infrastructure.repository.mybatis.generated.mapper.DlHistoryMapper;
import com.catalogap.infrastructure.repository.mybatis.mapper.CustomDownloadScenarioMapper;
import com.catalogap.infrastructure.repository.translator.ScenarioDownloadDomainEntityTranslator;
import java.sql.Timestamp;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

/**
 * ScenarioDownloadRepositoryを実装したリポジトリクラス.
 */
@Repository
public class MyBatisDownloadScenarioRepository implements ScenarioDownloadRepository {

  @Autowired
  private DlHistoryMapper dlHistoryMapper;

  @Autowired
  private CustomDownloadScenarioMapper customDownloadScenarioMapper;

  /**
   * 区間IDを取得する.
   *
   * @param uuid UUID.
   * @return 該当データ
   */
  @Override
  public ScenarioDownloadDomainEntity getScenarioSectionId(String uuid) {

    Map<String, Object> params = new HashMap<>();
    params.put("uuid", uuid);
    ScenarioInfoEntity scenarioInfoEntity =
        customDownloadScenarioMapper.getScenarioSectionId(params);
    ScenarioDownloadDomainEntity scenarioDownloadDomainEntity =
        ScenarioDownloadDomainEntityTranslator
            .translatorScenarioDownloadDomainEntity(scenarioInfoEntity);

    return scenarioDownloadDomainEntity;
  }

  /**
   * ダウンロード履歴テーブルに新しい履歴を挿入する.
   *
   * @param uuid UUID.
   * @param userId ユーザID.
   * @param dataDivision データ区分.
   * @return 登録結果
   */
  @Override
  public int insertDownloadHistory(String uuid, String userId, String dataDivision) {
    // 現在の日時を取得する
    Date date = new Date();
    Timestamp nowTime = new Timestamp(date.getTime());

    // dlHistory オブジェクトを作成し、属性を設定する
    DlHistory dlHistory = new DlHistory();
    dlHistory.setUuid(uuid);
    dlHistory.setDataDivision(dataDivision);
    dlHistory.setDlDateTime(nowTime);
    dlHistory.setEmailAddress(userId);
    dlHistory.setDeleteFlag("0");
    dlHistory.setCreateTime(nowTime);
    dlHistory.setUpdateTime(nowTime);
    return dlHistoryMapper.insertSelective(dlHistory);
  }

}
