package com.catalogap.applicationcore.scenariocode;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * シナリオコードドメインエンティティです.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioCodeDomainEntity {

  /*
   * 場所ID.
   */
  private String locationId;

  /*
   * 場所名.
   */
  private String locationName;

  /*
   * コード.
   */
  private String code;

  /*
   * 値.
   */
  private String value;

  /*
   * コードタイプ.
   */
  private String codeType;

  /*
   * 区間ID.
   */
  private String sectionId;

  /*
   * 区間名.
   */
  private String sectionName;

}
