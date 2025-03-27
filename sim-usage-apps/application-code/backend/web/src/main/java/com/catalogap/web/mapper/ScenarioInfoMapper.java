package com.catalogap.web.mapper;

import com.catalogap.applicationcore.scenarioinfo.ScenarioDetailResults;
import com.catalogap.applicationcore.scenarioinfo.ScenarioInfoDomainEntity;
import com.catalogap.applicationcore.scenarioinfo.ScenarioInfoListResults;
import com.catalogap.web.controller.dto.scenarioinfo.GetScenarioDetailResponse;
import com.catalogap.web.controller.dto.scenarioinfo.GetScenarioDetailResponse.ScenarioDetailInfo;
import com.catalogap.web.controller.dto.scenarioinfo.GetScenarioListResponse;
import com.catalogap.web.controller.dto.scenarioinfo.GetScenarioListResponse.GetScenarioListInfo;
import com.catalogap.web.controller.dto.scenarioinfo.GetScenarioListResponse.GetScenarioListInfo.ScenarioInfo.NearmissTypeInfo;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * ScenarioInfoController のマッパーです.
 */

public class ScenarioInfoMapper {
  /**
   * {@link ScenarioInfoListResults} オブジェクトを {@link GetScenarioListResponse} に変換します.
   *
   * @param scenarioInfoListResults オブジェクト.
   * @return {@link GetScenarioListResponse} オブジェクト.
   */
  public static GetScenarioListResponse convertToGetScenarioListResponse(
      ScenarioInfoListResults scenarioInfoListResults) {
    if (scenarioInfoListResults == null) {
      return null;
    }
    List<GetScenarioListInfo.ScenarioInfo> scenarioInfoList =
        scenarioInfoListResults.getScenarioInfoList().stream()
            .map(ScenarioInfoMapper::convertToScenarioInfoList).collect(Collectors.toList());

    return new GetScenarioListResponse(new GetScenarioListResponse.GetScenarioListInfo(
        scenarioInfoListResults.getCounts(), scenarioInfoList));
  }

  /**
   * {@link ScenarioInfoDomainEntity} オブジェクトを
   * {@link GetScenarioListResponse.GetScenarioListInfo.ScenarioInfo} に変換します.
   *
   * @param scenarioInfoDomainEntity オブジェクト.
   * @return {@link GetScenarioListResponse.GetScenarioListInfo.ScenarioInfo} オブジェクト.
   */
  private static GetScenarioListResponse.GetScenarioListInfo.ScenarioInfo convertToScenarioInfoList(
      ScenarioInfoDomainEntity scenarioInfoDomainEntity) {
    if (scenarioInfoDomainEntity == null) {
      return null;
    }

    List<String> nearmissTypeList = scenarioInfoDomainEntity.getNearmissTypeList();
    List<NearmissTypeInfo> nearmissTypeInfoList = new ArrayList<NearmissTypeInfo>();
    if (nearmissTypeList != null) {
      for (String nearmissType : nearmissTypeList) {
        NearmissTypeInfo nearmissTypeInfo = new NearmissTypeInfo();
        nearmissTypeInfo.setNearmissType(nearmissType);
        nearmissTypeInfoList.add(nearmissTypeInfo);
      }
    }

    return new GetScenarioListResponse.GetScenarioListInfo.ScenarioInfo(nearmissTypeInfoList,
        scenarioInfoDomainEntity.getVideoThumbnailUrl(), scenarioInfoDomainEntity.getSectionName(),
        scenarioInfoDomainEntity.getLocationName(), scenarioInfoDomainEntity.getUuid());
  }

  /**
   * {@link ScenarioDetailResults} オブジェクトを {@link GetScenarioDetailResponse} に変換します.
   *
   * @param scenarioDetailResults オブジェクト.
   * @return {@link GetScenarioDetailResponse} オブジェクト.
   */
  public static GetScenarioDetailResponse convertToGetScenarioDetailResponse(
      ScenarioDetailResults scenarioDetailResults) {
    if (scenarioDetailResults == null || scenarioDetailResults.getScenarioInfoDomainEntity() == null
        || scenarioDetailResults.getMachineLearningDataList() == null
        || scenarioDetailResults.getScenarioDataList() == null) {
      return null;
    }

    // シナリオ情報のヒヤリハット種別をリストに変換する
    List<ScenarioDetailInfo.NearmissTypeInfo> nearmissTypesResponse = new ArrayList<>();
    List<String> nearmissTypeList =
        scenarioDetailResults.getScenarioInfoDomainEntity().getNearmissTypeList();
    if (nearmissTypeList != null) {
      for (String nearmissType : nearmissTypeList) {
        GetScenarioDetailResponse.ScenarioDetailInfo.NearmissTypeInfo nearmissTypeInfo =
            new GetScenarioDetailResponse.ScenarioDetailInfo.NearmissTypeInfo();
        nearmissTypeInfo.setNearmissType(nearmissType);
        nearmissTypesResponse.add(nearmissTypeInfo);
      }
    }

    List<ScenarioDetailInfo.ScenarioData> scenarioDataResponse =
        scenarioDetailResults.getScenarioDataList().stream()
            .map(ScenarioInfoMapper::convertToScenarioDataResponse).collect(Collectors.toList());

    List<ScenarioDetailInfo.MachineLearningData> machineLearningDataResponse = scenarioDetailResults
        .getMachineLearningDataList().stream()
        .map(ScenarioInfoMapper::convertToMachineLearningDataResponse).collect(Collectors.toList());

    return new GetScenarioDetailResponse(new GetScenarioDetailResponse.ScenarioDetailInfo(
        scenarioDetailResults.getScenarioInfoDomainEntity().getId(), nearmissTypesResponse,
        scenarioDetailResults.getScenarioInfoDomainEntity().getVideoUrl(),
        scenarioDetailResults.getScenarioInfoDomainEntity().getVideoThumbnailUrl(),
        scenarioDetailResults.getScenarioInfoDomainEntity().getScenarioCreateTime(),
        scenarioDetailResults.getScenarioInfoDomainEntity().getSectionName(),
        scenarioDetailResults.getScenarioInfoDomainEntity().getLocationName(),
        scenarioDetailResults.getScenarioInfoDomainEntity().getLatitude(),
        scenarioDetailResults.getScenarioInfoDomainEntity().getLongitude(),
        scenarioDetailResults.getScenarioInfoDomainEntity().getUuid(), scenarioDataResponse,
        machineLearningDataResponse));
  }

  /**
   * {@link ScenarioInfoDomainEntity} オブジェクトを
   * {@link GetScenarioDetailResponse.ScenarioDetailInfo.ScenarioData} に変換します.
   *
   * @param scenarioInfoDomainEntity オブジェクト.
   * @return {@link GetScenarioDetailResponse.ScenarioDetailInfo.ScenarioData} オブジェクト.
   */
  private static ScenarioDetailInfo.ScenarioData convertToScenarioDataResponse(
      ScenarioInfoDomainEntity scenarioInfoDomainEntity) {
    if (scenarioInfoDomainEntity == null) {
      return null;
    }
    return new GetScenarioDetailResponse.ScenarioDetailInfo.ScenarioData(
        scenarioInfoDomainEntity.getName(), scenarioInfoDomainEntity.getDataDivision(),
        scenarioInfoDomainEntity.getSize());
  }

  /**
   * {@link ScenarioInfoDomainEntity} オブジェクトを
   * {@link GetScenarioDetailResponse.ScenarioDetailInfo.MachineLearningData} に変換します.
   *
   * @param scenarioInfoDomainEntity オブジェクト.
   * @return {@link GetScenarioDetailResponse.ScenarioDetailInfo.MachineLearningData} オブジェクト.
   */
  private static ScenarioDetailInfo.MachineLearningData convertToMachineLearningDataResponse(
      ScenarioInfoDomainEntity scenarioInfoDomainEntity) {
    if (scenarioInfoDomainEntity == null) {
      return null;
    }
    return new GetScenarioDetailResponse.ScenarioDetailInfo.MachineLearningData(
        scenarioInfoDomainEntity.getName(), scenarioInfoDomainEntity.getDataDivision(),
        scenarioInfoDomainEntity.getSize());
  }
}
