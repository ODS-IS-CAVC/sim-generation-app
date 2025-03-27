package com.catalogap.applicationcore.scenariodownload;

import org.springframework.stereotype.Repository;

/**
 * シナリオダウンロードリポジトリです.
 */
@Repository
public interface ScenarioDownloadRepository {

  /**
   * 区間IDを取得する.
   *
   * @param uuid UUID.
   * @return 該当データ
   */
  ScenarioDownloadDomainEntity getScenarioSectionId(String uuid);

  /**
   * ダウンロード履歴テーブルに新しい履歴を挿入する.
   *
   * @param uuid UUID.
   * @param userId ユーザID.
   * @param dataDivision データ区分.
   * @return 登録結果
   */
  int insertDownloadHistory(String uuid, String userId, String dataDivision);
}
