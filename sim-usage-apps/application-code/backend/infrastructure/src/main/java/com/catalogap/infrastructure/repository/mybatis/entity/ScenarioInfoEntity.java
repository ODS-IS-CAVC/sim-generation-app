package com.catalogap.infrastructure.repository.mybatis.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * シナリオ情報エンティティです.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioInfoEntity {

  /*
   * ヒヤリハット種別.
   */
  private String newNearmissType;

  /*
   * 区間名.
   */
  private String sectionName;

  /*
   * 場所名.
   */
  private String locationName;

  /*
   * UUID.
   */
  private String uuid;

  /*
   * ID.
   */
  private String id;

  /*
   * シナリオ作成日時.
   */
  private String scenarioCreateTime;

  /*
   * 緯度.
   */
  private String latitude;

  /*
   * 経度.
   */
  private String longitude;

  /*
   * 区間ID.
   */
  private String sectionId;
}
