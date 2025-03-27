package com.catalogap.infrastructure.repository.mybatis.mapper;

import com.catalogap.infrastructure.repository.mybatis.entity.ScenarioInfoEntity;
import java.util.Map;
import org.apache.ibatis.annotations.Mapper;

/**
 * カスタムダウンロードシナリオマッパーファイル.
 */
@Mapper
public interface CustomDownloadScenarioMapper {

  /**
   * シナリオ区間IDを取得する.
   *
   * @param params 検索条件.
   * @return シナリオ区間ID.
   */
  ScenarioInfoEntity getScenarioSectionId(Map<String, Object> params);
}
