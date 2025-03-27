package com.catalogap.infrastructure.repository.mybatis.mapper;

import com.catalogap.infrastructure.repository.mybatis.generated.entity.LocationMaster;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.SectionMaster;
import java.util.List;
import java.util.Map;
import org.apache.ibatis.annotations.Mapper;

/**
 * カスタムシナリオコードマッパーファイル.
 */
@Mapper
public interface CustomScenarioCodeMapper {

  /**
   * 発生区間を取得する.
   *
   * @param params 検索条件.
   * @return 発生区間.
   */
  List<SectionMaster> selectHappenSection(Map<String, Object> params);

  /**
   * 発生場所を取得する.
   *
   * @param params 検索条件.
   * @return 発生場所.
   */
  List<LocationMaster> selectHappenLocation(Map<String, Object> params);
}
