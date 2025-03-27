package com.catalogap.applicationcore.scenariodownload;

import com.catalogap.applicationcore.scenarioinfo.ScenarioInfoDomainEntity;
import com.catalogap.applicationcore.scenarioinfo.ScenarioInfoRepository;
import com.catalogap.systemcommon.constant.MessageIdConstant;
import com.catalogap.systemcommon.constant.SystemPropertyConstants;
import com.catalogap.systemcommon.exception.LogicException;
import com.catalogap.systemcommon.util.LogUtil;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.cloudfront.CloudFrontUtilities;
import software.amazon.awssdk.services.cloudfront.model.CannedSignerRequest;
import software.amazon.awssdk.services.cloudfront.url.SignedUrl;

/**
 * シナリオダウンロードサービスクラス.
 */
@Service
public class ScenarioDownloadService {

  @Value("${aws.cloudfront.key-id}")
  private String keyPairId;

  @Value("${aws.cloudfront.key}")
  private String privateKey;

  @Value("${aws.cloudfront.distribution_domain}")
  private String distributionDomain;

  @Value("${s3.prefix.path}")
  private String prefixPath;

  @Value("${aws.cloudfront.dl.expiration.hours}")
  private int expirationHours;

  @Value("${s3.document.suffix-opendrive}")
  private String openDrive;

  @Value("${s3.document.suffix-vehicletrajectory}")
  private String vehicleTrajectory;

  @Value("${s3.document.suffix-sdmgscenario}")
  private String sdmgScenario;

  @Value("${s3.document.suffix-openscenario}")
  private String openScenario;

  @Value("${s3.document.suffix-machinelearning}")
  private String machineLearning;

  @Value("${s3.scenario.path}")
  private String scenarioPath;

  @Value("${s3.ml_img.path}")
  private String machinePath;

  @Autowired
  private ScenarioDownloadRepository scenarioDownloadRepository;

  @Autowired
  private ScenarioInfoRepository scenarioInfoRepository;


  /**
   * 引数をもとにシナリオのデータおよび機械学習用の画像のデータをダウンロードする.
   *
   * @param uuid UUID.
   * @param dataDivision データ区分.
   * @param userId ユーザーID.
   * @return シナリオデータのダウンロードurl
   * @throws LogicException ロジック異常
   */
  public ScenarioDownloadDomainEntity downloadScenarioData(String uuid, String dataDivision,
      String userId) throws LogicException {
    // ユーザーの検索権限を取得する
    List<ScenarioInfoDomainEntity> searchAuthInfo = scenarioInfoRepository.getSearchAuth(userId);
    List<String> sectionIdList = null;
    if (searchAuthInfo != null && searchAuthInfo.size() > 0) {
      sectionIdList = searchAuthInfo.stream().map(ScenarioInfoDomainEntity::getSectionId)
          .collect(Collectors.toList());
    }
    ScenarioDownloadDomainEntity scenarioDownloadDomainEntity = new ScenarioDownloadDomainEntity();
    if (sectionIdList == null) {
      return scenarioDownloadDomainEntity;
    } else {
      // シナリオ情報の区間IDを取得する
      ScenarioDownloadDomainEntity scenarioInfoSectionId =
          scenarioDownloadRepository.getScenarioSectionId(uuid);
      String sectionId = null;
      if (scenarioInfoSectionId != null) {
        sectionId = scenarioInfoSectionId.getSectionId();
      }

      if (sectionId == null || !sectionIdList.contains(sectionId)) {
        return scenarioDownloadDomainEntity;
      } else {
        // データ区別により、ファイル名を取得する
        Map<String, String> fileNameMap = setFileNameByDataDivision(dataDivision);
        String fileName = null;
        String contentPath = null;

        // fileNameMapに1つの要素しか含まれていないため、直接その要素のキーと値を取得できます。
        if (!fileNameMap.isEmpty()) {
          Map.Entry<String, String> entry = fileNameMap.entrySet().iterator().next();
          fileName = entry.getKey();
          contentPath = entry.getValue();
        }

        // シナリオデータダウンロードの署名 URLを作成する
        CloudFrontUtilities cloudFrontUtilities = CloudFrontUtilities.create();
        String resourceUrl =
            distributionDomain + prefixPath + uuid + contentPath + "/" + uuid + fileName;
        CannedSignerRequest cannedRequest = null;
        String url = null;

        // 期限は、発行後1時間
        Instant expirationDate = Instant.now().plus(expirationHours, ChronoUnit.HOURS);

        try {
          cannedRequest = CannedSignerRequest.builder().resourceUrl(resourceUrl)
              .privateKey(new java.io.File(privateKey).toPath()).keyPairId(keyPairId)
              .expirationDate(expirationDate).build();
          SignedUrl signedUrl = cloudFrontUtilities.getSignedUrlWithCannedPolicy(cannedRequest);
          url = signedUrl.url();
        } catch (Exception e) {
          throw new LogicException(null, MessageIdConstant.E4L004, new String[] {"URL"});
        }
        scenarioDownloadDomainEntity.setDownloadUrl(url);

        // ダウンロード履歴テーブルに新しい履歴を挿入する
        this.scenarioDownloadRepository.insertDownloadHistory(uuid, userId, dataDivision);
        LogUtil.info("ダウンロード履歴テーブルに新しい履歴を挿入しました。");
        return scenarioDownloadDomainEntity;
      }
    }
  }

  /**
   * データ区別により、ファイル名とコンテンツタイプを取得する.
   *
   * @param dataDivision データ区分.
   * @return ファイル名とコンテンツタイプ
   */
  private Map<String, String> setFileNameByDataDivision(String dataDivision) {
    Map<String, String> fileNameMap = new HashMap<>();
    if (dataDivision.equals(SystemPropertyConstants.OPEN_DRIVE)) {
      fileNameMap.put(openDrive, scenarioPath);
    } else if (dataDivision.equals(SystemPropertyConstants.VEHICLE_TRAJECTORY)) {
      fileNameMap.put(vehicleTrajectory, scenarioPath);
    } else if (dataDivision.equals(SystemPropertyConstants.SDMG_SCENARIO)) {
      fileNameMap.put(sdmgScenario, scenarioPath);
    } else if (dataDivision.equals(SystemPropertyConstants.OPEN_SCENARIO)) {
      fileNameMap.put(openScenario, scenarioPath);
    } else if (dataDivision.equals(SystemPropertyConstants.MACHINE_LEARNING)) {
      fileNameMap.put(machineLearning, machinePath);
    } else {
      LogUtil.warn("存在しないデータ区別が入力されました。");
    }
    return fileNameMap;
  }
}
