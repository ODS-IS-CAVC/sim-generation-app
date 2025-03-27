package com.catalogap.applicationcore.scenariocode;

import com.catalogap.systemcommon.constant.MessageIdConstant;
import com.catalogap.systemcommon.exception.LogicException;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * シナリオコードサービスクラス.
 */
@Service
public class ScenarioCodeService {
  // ヒヤリハット種別
  private static final String NEAR_MISS_TYPE = "1";

  @Autowired
  private ScenarioCodeRepository scenarioCodeRepository;


  /**
   * 引数をもとにシナリオ検索画面の検索条件に使用するデータをシナリオの属性管理テーブルから検索し、該当するデータを返却する.
   *
   * @param userId ユーザーID
   * @return 該当するデータ
   * @throws LogicException ロジック異常
   */
  public ScenarioCodeListResults getCodeList(String userId) throws LogicException {
    // ヒヤリハット種別データを取得する
    List<ScenarioCodeDomainEntity> codeList = this.scenarioCodeRepository.getCodeList();
    List<ScenarioCodeDomainEntity> nearmissTypeList = codeList.stream()
        .filter(domain -> domain.getCodeType().equals(NEAR_MISS_TYPE)).collect(Collectors.toList());

    // 発生区間データを取得する
    List<ScenarioCodeDomainEntity> sectionList = this.scenarioCodeRepository.getSectionList(userId);

    ScenarioCodeListResults scenarioCodeListResults = new ScenarioCodeListResults();

    // リストのサイズが0に等しい場合は、エーラのLogicException異常をスローする
    if (nearmissTypeList == null || nearmissTypeList.size() <= 0) {
      throw new LogicException(null, MessageIdConstant.E4L001, new String[] {"ヒヤリハット種別"});
    } else {
      // ヒヤリハット種別リストを昇順に並べ替える
      Collections.sort(nearmissTypeList, Comparator.comparing(ScenarioCodeDomainEntity::getCode));
      scenarioCodeListResults.setNearmissTypeList(nearmissTypeList);
    }
    if (sectionList == null || sectionList.size() <= 0) {
      throw new LogicException(null, MessageIdConstant.E4L001, new String[] {"区間"});
    } else {
      scenarioCodeListResults.setSectionList(sectionList);
    }
    return scenarioCodeListResults;
  }

  /**
   * 引数をもとにシナリオ検索画面の検索条件に使用するデータを場所マスタテーブルから検索し、該当するデータを返却する.
   *
   * @param sectionId 区間ID
   * @param userId ユーザーID
   * @return 該当するデータ
   * @throws LogicException ロジック異常
   */
  public List<ScenarioCodeDomainEntity> getLocationList(String sectionId, String userId)
      throws LogicException {
    List<ScenarioCodeDomainEntity> locationListInfo =
        this.scenarioCodeRepository.getLocationList(sectionId, userId);

    if (locationListInfo == null || locationListInfo.size() <= 0) {
      throw new LogicException(null, MessageIdConstant.E4L003, new String[] {"発生場所"});
    } else {
      return locationListInfo;
    }

  }
}
