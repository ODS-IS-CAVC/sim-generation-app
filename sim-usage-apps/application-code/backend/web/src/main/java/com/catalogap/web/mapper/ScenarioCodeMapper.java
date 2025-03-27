package com.catalogap.web.mapper;

import com.catalogap.applicationcore.scenariocode.ScenarioCodeDomainEntity;
import com.catalogap.applicationcore.scenariocode.ScenarioCodeListResults;
import com.catalogap.web.controller.dto.scenariocode.GetCodeListResponse;
import com.catalogap.web.controller.dto.scenariocode.GetCodeListResponse.GetCodeListInfo;
import com.catalogap.web.controller.dto.scenariocode.GetLocationListResponse;
import java.util.List;
import java.util.stream.Collectors;

/**
 * ScenarioCodeController のマッパーです.
 */

public class ScenarioCodeMapper {

  /**
   * {@link ScenarioCodeListResults} オブジェクトを {@link GetCodeListResponse} に変換します.
   *
   * @param scenarioCodeListResults オブジェクト.
   * @return {@link GetCodeListResponse} オブジェクト.
   */
  public static GetCodeListResponse convertToGetCodeListResponse(
      ScenarioCodeListResults scenarioCodeListResults) {
    if (scenarioCodeListResults == null) {
      return null;
    }

    List<GetCodeListResponse.GetCodeListInfo.NearMissInfo> nearMissInfoList =
        scenarioCodeListResults.getNearmissTypeList().stream()
            .map(ScenarioCodeMapper::convertToNearMissTypeList).collect(Collectors.toList());

    List<GetCodeListResponse.GetCodeListInfo.HappenSectionInfo> happenSectionInfoList =
        scenarioCodeListResults.getSectionList().stream()
            .map(ScenarioCodeMapper::convertToHappenSectionInfoList).collect(Collectors.toList());

    return new GetCodeListResponse(
        new GetCodeListResponse.GetCodeListInfo(nearMissInfoList, happenSectionInfoList));
  }

  /**
   * {@link ScenarioCodeDomainEntity} オブジェクトを
   * {@link GetCodeListResponse.GetCodeListInfo.NearMissInfo} に変換します.
   *
   * @param scenarioCodeDomainEntity オブジェクト.
   * @return {@link GetCodeListResponse.GetCodeListInfo.NearMissInfo} オブジェクト.
   */
  private static GetCodeListResponse.GetCodeListInfo.NearMissInfo convertToNearMissTypeList(
      ScenarioCodeDomainEntity scenarioCodeDomainEntity) {
    if (scenarioCodeDomainEntity == null) {
      return null;
    }
    return new GetCodeListResponse.GetCodeListInfo.NearMissInfo(scenarioCodeDomainEntity.getCode(),
        scenarioCodeDomainEntity.getValue());
  }

  /**
   * {@link ScenarioCodeDomainEntity} オブジェクトを
   * {@link GetCodeListResponse.GetCodeListInfo.HappenSectionInfo} に変換します.
   *
   * @param scenarioCodeDomainEntity オブジェクト.
   * @return {@link GetCodeListResponse.GetCodeListInfo.HappenSectionInfo} オブジェクト.
   */
  private static GetCodeListInfo.HappenSectionInfo convertToHappenSectionInfoList(
      ScenarioCodeDomainEntity scenarioCodeDomainEntity) {
    if (scenarioCodeDomainEntity == null) {
      return null;
    }
    return new GetCodeListResponse.GetCodeListInfo.HappenSectionInfo(
        scenarioCodeDomainEntity.getSectionId(), scenarioCodeDomainEntity.getSectionName());
  }

  /**
   * List<{@link ScenarioCodeDomainEntity}> を {@link GetLocationListResponse} に変換します.
   *
   * @param scenarioCodeDomainEntityList シナリオドメインエンティティリスト.
   * @return {@link GetLocationListResponse} オブジェクト.
   */
  public static GetLocationListResponse convertToGetLocationListResponse(
      List<ScenarioCodeDomainEntity> scenarioCodeDomainEntityList) {
    if (scenarioCodeDomainEntityList == null || scenarioCodeDomainEntityList.size() <= 0) {
      return null;
    }

    List<GetLocationListResponse.GetLocationListInfo.LocationData> locationDataList =
        scenarioCodeDomainEntityList.stream().map(ScenarioCodeMapper::convertToLocationData)
            .collect(Collectors.toList());

    return new GetLocationListResponse(
        new GetLocationListResponse.GetLocationListInfo(locationDataList));
  }

  /**
   * {@link ScenarioCodeDomainEntity} オブジェクトを
   * {@link GetLocationListResponse.GetLocationListInfo.LocationData} に変換します.
   *
   * @param scenarioCodeDomainEntity オブジェクト.
   * @return {@link GetLocationListResponse.GetLocationListInfo.LocationData} オブジェクト.
   */
  private static GetLocationListResponse.GetLocationListInfo.LocationData convertToLocationData(
      ScenarioCodeDomainEntity scenarioCodeDomainEntity) {
    if (scenarioCodeDomainEntity == null) {
      return null;
    }
    return new GetLocationListResponse.GetLocationListInfo.LocationData(
        scenarioCodeDomainEntity.getLocationId(), scenarioCodeDomainEntity.getLocationName());
  }

}
