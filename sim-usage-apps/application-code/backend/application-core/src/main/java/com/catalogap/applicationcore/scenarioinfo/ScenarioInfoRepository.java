package com.catalogap.applicationcore.scenarioinfo;

import java.util.List;
import org.springframework.stereotype.Repository;

/**
 * シナリオ情報リポジトリです.
 */
@Repository
public interface ScenarioInfoRepository {
  /**
   * ユーザーの検索権限を取得する.
   *
   * @param userId ユーザーID.
   * @return ユーザーの検索権限
   */
  List<ScenarioInfoDomainEntity> getSearchAuth(String userId);

  /**
   * 引数をもとにシナリオ検索画面の検索結果一覧に使用するデータをシナリオの情報テーブルから検索し、該当するデータを返却する.
   *
   * @param nearmissType ヒヤリハット種別.
   * @param skipRows スキップしたいレコード数.
   * @param itemsPerPage 1ページあたりのレコード数.
   * @param userId ユーザID.
   * @param happenTime 発生日時.
   * @param happenSection 発生区間.
   * @param happenLocation 発生場所.
   * @return 該当するデータ
   */
  List<ScenarioInfoDomainEntity> getScenarioList(List<String> nearmissType, int skipRows,
      int itemsPerPage, String userId, String happenTime, String happenSection,
      String happenLocation);

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
  int getScenarioCount(List<String> nearmissType, String userId, String happenTime,
      String happenSection, String happenLocation);

  /**
   * 引数をもとにシナリオ詳細画面に使用するデータをシナリオの情報テーブルから検索し、該当するデータを返却する.
   *
   * @param uuid UUID.
   * @return シナリオ情報
   */
  ScenarioInfoDomainEntity getScenarioDetailInfo(String uuid);

  /**
   * ダウンロード認可情報を取得する.
   *
   * @param userId ユーザーID.
   * @return ダウンロード認可情報
   */
  ScenarioInfoDomainEntity downloadAuth(String userId);
}
