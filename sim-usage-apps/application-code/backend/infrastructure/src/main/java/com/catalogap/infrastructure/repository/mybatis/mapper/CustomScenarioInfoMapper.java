package com.catalogap.infrastructure.repository.mybatis.mapper;

import com.catalogap.infrastructure.repository.mybatis.entity.ScenarioInfoEntity;
import java.util.List;
import java.util.Map;
import org.apache.ibatis.annotations.Mapper;

/**
 * カスタムシナリオ情報マッパーファイル.
 */
@Mapper
public interface CustomScenarioInfoMapper {

  /**
   * シナリオ情報リストを取得する.
   *
   * @param params 検索条件.
   * @return シナリオ情報リスト.
   */
  List<ScenarioInfoEntity> getScenarioList(Map<String, Object> params);

  /**
   * シナリオ情報数量を取得する.
   *
   * @param params 検索条件.
   * @return シナリオ情報数量.
   */
  int getScenarioCount(Map<String, Object> params);

  /**
   * シナリオ情報を取得する.
   *
   * @param params 検索条件.
   * @return シナリオ情報.
   */
  ScenarioInfoEntity getScenarioDetailInfo(Map<String, Object> params);

}
