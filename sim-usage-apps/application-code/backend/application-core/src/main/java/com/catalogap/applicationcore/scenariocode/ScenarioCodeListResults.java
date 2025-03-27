package com.catalogap.applicationcore.scenariocode;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * シナリオコードリストの検索結果です.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioCodeListResults {

  /*
   * ヒヤリハット種別.
   */
  private List<ScenarioCodeDomainEntity> nearmissTypeList;

  /*
   * 発生区間.
   */
  private List<ScenarioCodeDomainEntity> sectionList;
}
