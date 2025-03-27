package com.catalogap.applicationcore.scenariocode;

import java.util.List;
import org.springframework.stereotype.Repository;

/**
 * シナリオコードリポジトリです.
 */
@Repository
public interface ScenarioCodeRepository {

  /**
   * 検索条件コード値マスタから種別データを取得する.
   *
   * @return 種別データ
   */
  List<ScenarioCodeDomainEntity> getCodeList();

  /**
   * 区間マスタと検索認可から発生区間データを取得する.
   *
   * @param userId ユーザーID.
   * @return 発生区間データ
   */
  List<ScenarioCodeDomainEntity> getSectionList(String userId);

  /**
   * 引数をもとにシナリオ検索画面の検索条件に使用するデータを場所マスタテーブルから検索し、該当するデータを返却する.
   *
   * @param sectionId 区間ID.
   * @param userId ユーザーID.
   * @return 該当するデータ
   */
  List<ScenarioCodeDomainEntity> getLocationList(String sectionId, String userId);

}
