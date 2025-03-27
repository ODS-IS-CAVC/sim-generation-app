package com.catalogap.applicationcore.scenarioinfo;

import com.catalogap.systemcommon.constant.MessageIdConstant;
import com.catalogap.systemcommon.constant.SystemPropertyConstants;
import com.catalogap.systemcommon.exception.LogicException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.cloudfront.CloudFrontUtilities;
import software.amazon.awssdk.services.cloudfront.model.CannedSignerRequest;
import software.amazon.awssdk.services.cloudfront.url.SignedUrl;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.ListObjectsV2Request;
import software.amazon.awssdk.services.s3.model.S3Object;
import software.amazon.awssdk.services.s3.paginators.ListObjectsV2Iterable;

/**
 * シナリオ情報サービスクラス.
 */
@Service
public class ScenarioInfoService {

  @Value("${aws.cloudfront.key-id}")
  private String keyPairId;

  @Value("${aws.cloudfront.key}")
  private String privateKey;

  @Value("${my-bucket-name}")
  private String bucketName;

  @Value("${aws.cloudfront.distribution_domain}")
  private String distributionDomain;

  @Value("${s3.prefix.path}")
  private String prefixPath;

  @Value("${aws.cloudfront.thumbnail.video.expiration.minutes}")
  private int expirationMinutes;

  @Value("${s3.format.path}")
  private String formatPath;

  @Value("${s3.scenario.path}")
  private String scenarioPath;

  @Value("${s3.ml_img.path}")
  private String machinePath;

  @Value("${s3.jpeg.suffix}")
  private String jpegSuffix;

  @Value("${s3.mp4.suffix}")
  private String mp4Suffix;

  @Value("${s3.zip.suffix}")
  private String zipSuffix;

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

  @Autowired
  private ScenarioInfoRepository scenarioInfoRepository;

  private final Region region = Region.AP_NORTHEAST_1;


  /**
   * 引数をもとにシナリオ検索画面の検索結果一覧に使用するデータをシナリオの情報テーブルから検索し、該当するデータを返却する.
   *
   * @param nearmissType ヒヤリハット種別.
   * @param requestPage 要求ページ番号.
   * @param itemsPerPage 1ページあたりのレコード数.
   * @param happenTime 発生日時.
   * @param happenSection 発生区間.
   * @param happenLocation 発生場所.
   * @param userId ユーザーID.
   * @return 該当するデータ
   * @throws LogicException ロジック異常
   */
  public ScenarioInfoListResults getScenarioList(List<String> nearmissType, int requestPage,
      int itemsPerPage, String happenTime, String happenSection, String happenLocation,
      String userId) throws LogicException {
    // requestPage とitemsPerPageからスキップしたいレコード数を算出する
    int skipRows = (requestPage - 1) * itemsPerPage;

    // シナリオ情報を取得する
    List<ScenarioInfoDomainEntity> scenarioInfoList = this.scenarioInfoRepository.getScenarioList(
        nearmissType, skipRows, itemsPerPage, userId, happenTime, happenSection, happenLocation);

    S3Client s3 = S3Client.builder().region(region).build();


    for (ScenarioInfoDomainEntity scenarioInfoDomainEntity : scenarioInfoList) {

      // カンマで区切るヒヤリハット種別をリストに変換して、ヒヤリハット種別リストを作成する
      String nearmissTypeWithComma = scenarioInfoDomainEntity.getNearmissTypeWithComma();
      if (nearmissTypeWithComma != null) {
        scenarioInfoDomainEntity
            .setNearmissTypeList(Arrays.asList(nearmissTypeWithComma.split(",")));
      }

      // サムネイル画像の署名URLを作成する
      String prefix = prefixPath + scenarioInfoDomainEntity.getUuid() + formatPath;
      String url = createPresignedUrlForCloudFront(s3, prefix, jpegSuffix);
      scenarioInfoDomainEntity.setVideoThumbnailUrl(url);
    }

    // シナリオ情報数量を取得する
    int counts = this.scenarioInfoRepository.getScenarioCount(nearmissType, userId, happenTime,
        happenSection, happenLocation);

    ScenarioInfoListResults scenarioInfoListResults = new ScenarioInfoListResults();
    scenarioInfoListResults.setScenarioInfoList(scenarioInfoList);
    scenarioInfoListResults.setCounts(counts);
    return scenarioInfoListResults;
  }

  /**
   * 引数をもとにシナリオ検索画面の検索結果一覧に使用するデータをシナリオの情報テーブルから検索し、該当するデータを返却する.
   *
   * @param uuid UUID.
   * @param userId ユーザーID.
   * @return 該当するデータ
   * @throws LogicException ロジック異常
   */
  public ScenarioDetailResults getScenarioDetail(String uuid, String userId) throws LogicException {
    // ユーザーの検索権限を取得する
    List<ScenarioInfoDomainEntity> searchAuthInfo = scenarioInfoRepository.getSearchAuth(userId);
    List<String> sectionIdList = null;
    if (searchAuthInfo != null && searchAuthInfo.size() > 0) {
      sectionIdList = searchAuthInfo.stream().map(ScenarioInfoDomainEntity::getSectionId)
          .collect(Collectors.toList());
    }

    ScenarioDetailResults scenarioDetailResults = new ScenarioDetailResults();
    if (sectionIdList == null) {
      return scenarioDetailResults;
    } else {
      // シナリオ情報を取得する
      ScenarioInfoDomainEntity scenarioInfo =
          this.scenarioInfoRepository.getScenarioDetailInfo(uuid);
      String sectionId = null;
      if (scenarioInfo != null) {
        sectionId = scenarioInfo.getSectionId();
      }
      if (sectionId == null || !sectionIdList.contains(sectionId)) {
        return scenarioDetailResults;
      } else {
        S3Client s3 = S3Client.builder().region(region).build();

        // 動画の署名URLの作成
        String prefix = prefixPath + uuid + formatPath;
        String url = createPresignedUrlForCloudFront(s3, prefix, mp4Suffix);
        scenarioInfo.setVideoUrl(url);

        // サムネイル画像の署名URLの作成
        String thumbnailSignedUrl = createPresignedUrlForCloudFront(s3, prefix, jpegSuffix);
        scenarioInfo.setVideoThumbnailUrl(thumbnailSignedUrl);

        // ダウンロード認可情報を取得する
        String scenarioPrefix = prefixPath + uuid + scenarioPath;
        ListObjectsV2Request scenarioReq =
            ListObjectsV2Request.builder().bucket(bucketName).prefix(scenarioPrefix).build();
        ListObjectsV2Iterable scenarioListing = s3.listObjectsV2Paginator(scenarioReq);

        String machineLearningPrefix = prefixPath + uuid + machinePath;
        ListObjectsV2Request machineLearningReq =
            ListObjectsV2Request.builder().bucket(bucketName).prefix(machineLearningPrefix).build();
        ListObjectsV2Iterable machineLearningListing =
            s3.listObjectsV2Paginator(machineLearningReq);

        // シナリオ可否フラグと機械学習可否フラグを取得する
        ScenarioInfoDomainEntity scenarioInfoFlag =
            this.scenarioInfoRepository.downloadAuth(userId);

        List<ScenarioInfoDomainEntity> scenarioDataList = new ArrayList<>();
        List<ScenarioInfoDomainEntity> machineLearningDataList = new ArrayList<>();

        // シナリオデータリストと機械学習用データリストを設定する
        if (scenarioInfoFlag.getScenarioPossibilityFlag() != null
            && scenarioInfoFlag.getScenarioPossibilityFlag()
                .equals(SystemPropertyConstants.SCENARIO_POSSIBILITY_FLAG_YES)) {
          processListing(scenarioListing, scenarioDataList);
          scenarioDataList.sort(Comparator.comparing(ScenarioInfoDomainEntity::getDataDivision));
        }
        if (scenarioInfoFlag.getMlPossibilityFlag() != null && scenarioInfoFlag
            .getMlPossibilityFlag().equals(SystemPropertyConstants.ML_POSSIBILITY_FLAG_YES)) {
          processListing(machineLearningListing, machineLearningDataList);
        }

        // カンマで区切るヒヤリハット種別をリストに変換して、ヒヤリハット種別リストを作成する
        String nearmissTypeWithComma = scenarioInfo.getNearmissTypeWithComma();
        if (nearmissTypeWithComma != null) {
          scenarioInfo.setNearmissTypeList(Arrays.asList(nearmissTypeWithComma.split(",")));
        }
        scenarioDetailResults.setScenarioInfoDomainEntity(scenarioInfo);
        scenarioDetailResults.setMachineLearningDataList(machineLearningDataList);
        scenarioDetailResults.setScenarioDataList(scenarioDataList);
        return scenarioDetailResults;
      }
    }
  }

  /**
   * CloudFrontによって、PresignedURLを作成する.
   *
   * @param s3 S3クライアントオブジェクト.
   * @param prefix S3オブジェクトのキーのプレフィックス.
   * @param suffix S3オブジェクトのキーのサフィックス.
   * @return PresignedURL
   * @throws LogicException ロジック異常
   */
  private String createPresignedUrlForCloudFront(S3Client s3, String prefix, String suffix)
      throws LogicException {
    CannedSignerRequest cannedRequest = null;
    String url = null;
    try {
      // S3 バケットから指定されたプレフィックスとサフィックスを持つファイルのキーを抽出する
      ListObjectsV2Request req =
          ListObjectsV2Request.builder().bucket(bucketName).prefix(prefix).build();
      ListObjectsV2Iterable listing = s3.listObjectsV2Paginator(req);
      String mediaKey = listing.stream().flatMap(r -> r.contents().stream()).map(S3Object::key)
          .filter(key -> key.endsWith(suffix)).collect(Collectors.joining());

      // CloudFrontによって、署名付きURLを生成する
      CloudFrontUtilities cloudFrontUtilities = CloudFrontUtilities.create();
      String resourceUrl = distributionDomain + mediaKey;

      // 期限は、発行後60分
      Instant expirationDate = Instant.now().plus(expirationMinutes, ChronoUnit.MINUTES);

      cannedRequest = CannedSignerRequest.builder().resourceUrl(resourceUrl)
          .privateKey(new java.io.File(privateKey).toPath()).keyPairId(keyPairId)
          .expirationDate(expirationDate).build();
      SignedUrl signedUrl = cloudFrontUtilities.getSignedUrlWithCannedPolicy(cannedRequest);
      url = signedUrl.url();
    } catch (Exception e) {
      throw new LogicException(e, MessageIdConstant.E4L004, new String[] {"URL"});
    }
    return url;
  }

  /**
   * .zip で終わるファイルを見つけ、ファイル名とサイズを取得する.
   *
   * @param listing S3 バケットから取得したオブジェクトの一覧を表す ListObjectsV2Result オブジェクト.
   * @param list シナリオ情報ドメインエンティティリスト.
   */
  private void processListing(ListObjectsV2Iterable listing, List<ScenarioInfoDomainEntity> list) {

    Map<String, Long> zipList = listing.stream().flatMap(r -> r.contents().stream())
        .filter(s3Object -> s3Object.key().endsWith(zipSuffix))
        .collect(Collectors.toMap(S3Object::key, S3Object::size));

    for (Map.Entry<String, Long> entry : zipList.entrySet()) {
      ScenarioInfoDomainEntity scenarioInfoDomainEntity = new ScenarioInfoDomainEntity();

      String key = entry.getKey();
      String fileName = key.substring(key.lastIndexOf('/') + 1);

      double fileSizeByte = entry.getValue();
      double fileSize = 0;
      if (fileSizeByte < SystemPropertyConstants.MB_TO_BYTES) {
        fileSize = fileSizeByte / SystemPropertyConstants.KB_TO_BYTES;
        scenarioInfoDomainEntity
            .setSize(String.format("%.2f", fileSize) + SystemPropertyConstants.KB);
      } else {
        fileSize = fileSizeByte / SystemPropertyConstants.MB_TO_BYTES;
        scenarioInfoDomainEntity
            .setSize(String.format("%.2f", fileSize) + SystemPropertyConstants.MB);
      }

      setDataDivisionByFileName(fileName, scenarioInfoDomainEntity);
      scenarioInfoDomainEntity.setName(fileName);
      list.add(scenarioInfoDomainEntity);
    }
  }

  /**
   * ファイル名に基づいて データ区分 の値を設定する.
   *
   * @param fileName ファイル名.
   * @param scenarioInfoDomainEntity シナリオ情報ドメインエンティティ.
   */
  private void setDataDivisionByFileName(String fileName,
      ScenarioInfoDomainEntity scenarioInfoDomainEntity) {
    int underscoreIndex = fileName.indexOf("_");
    if (underscoreIndex != -1) {
      String nameFromUnderscore = fileName.substring(underscoreIndex);
      if (nameFromUnderscore.equals(openDrive)) {
        scenarioInfoDomainEntity.setDataDivision(SystemPropertyConstants.OPEN_DRIVE);
      } else if (nameFromUnderscore.equals(vehicleTrajectory)) {
        scenarioInfoDomainEntity.setDataDivision(SystemPropertyConstants.VEHICLE_TRAJECTORY);
      } else if (nameFromUnderscore.equals(sdmgScenario)) {
        scenarioInfoDomainEntity.setDataDivision(SystemPropertyConstants.SDMG_SCENARIO);
      } else if (nameFromUnderscore.equals(openScenario)) {
        scenarioInfoDomainEntity.setDataDivision(SystemPropertyConstants.OPEN_SCENARIO);
      } else if (nameFromUnderscore.equals(machineLearning)) {
        scenarioInfoDomainEntity.setDataDivision(SystemPropertyConstants.MACHINE_LEARNING);
      }
    }
  }
}
