package com.catalogap.applicationcore.scenarioinfo;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * シナリオ情報リストの検索結果です.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioInfoListResults {

  /*
   * 検索結果のレコード数.
   */
  private int counts;

  /*
   * シナリオ情報リスト.
   */
  private List<ScenarioInfoDomainEntity> scenarioInfoList;
}
