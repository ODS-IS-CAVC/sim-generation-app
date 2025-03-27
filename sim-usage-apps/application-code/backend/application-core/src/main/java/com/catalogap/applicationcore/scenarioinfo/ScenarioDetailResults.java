package com.catalogap.applicationcore.scenarioinfo;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * シナリオ詳細情報の検索結果です.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioDetailResults {

  /**
   * シナリオ情報ドメインエンティティ.
   */
  private ScenarioInfoDomainEntity scenarioInfoDomainEntity;

  /*
   * シナリオデータリスト.
   */
  private List<ScenarioInfoDomainEntity> scenarioDataList;

  /*
   * 機械学習用データリスト.
   */
  private List<ScenarioInfoDomainEntity> machineLearningDataList;
}
