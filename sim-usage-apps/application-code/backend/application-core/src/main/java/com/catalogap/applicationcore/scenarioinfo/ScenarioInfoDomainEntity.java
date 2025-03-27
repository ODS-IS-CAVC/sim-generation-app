package com.catalogap.applicationcore.scenarioinfo;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * シナリオ情報ドメインエンティティです.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ScenarioInfoDomainEntity {

  /*
   * カンマで区切るヒヤリハット種別.
   */
  private String nearmissTypeWithComma;

  /**
   * ヒヤリハット種別リスト.
   */
  private List<String> nearmissTypeList;

  /*
   * 署名付き動画URL.
   */
  private String videoUrl;

  /*
   * 署名付き動画サムネル画像URL.
   */
  private String videoThumbnailUrl;

  /*
   * シナリオ作成日時.
   */
  private String scenarioCreateTime;

  /*
   * 区間名.
   */
  private String sectionName;

  /*
   * 場所名.
   */
  private String locationName;

  /*
   * 緯度.
   */
  private String latitude;

  /*
   * 経度.
   */
  private String longitude;

  /*
   * UUID.
   */
  private String uuid;

  /*
   * シナリオデータの名前/機械学習用データの名前.
   */
  private String name;

  /*
   * データ区分.
   */
  private String dataDivision;

  /*
   * シナリオデータのサイズ/機械学習用データのサイズ.
   */
  private String size;

  /*
   * シナリオ可否フラグ.
   */
  private String scenarioPossibilityFlag;

  /*
   * 機械学習可否フラグ.
   */
  private String mlPossibilityFlag;

  /*
   * ID.
   */
  private String id;

  /*
   * 区間ID.
   */
  private String sectionId;
}
