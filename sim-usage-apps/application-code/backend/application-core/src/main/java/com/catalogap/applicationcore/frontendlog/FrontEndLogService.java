package com.catalogap.applicationcore.frontendlog;

import com.catalogap.systemcommon.constant.SystemPropertyConstants;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

/**
 * フロントエンドログサービスクラス.
 */
@Service
public class FrontEndLogService {

  private static final Logger frontEndLogger =
      LoggerFactory.getLogger(SystemPropertyConstants.FRONTEND_LOG_LOGGER);

  /**
   * フロントエンドのログデータをアップロードする.
   *
   * @param frontendLogDomainEntity フロントエンドログドメインエンティティ.
   * @param userId ユーザーID.
   */
  public void saveLog(FrontendLogDomainEntity frontendLogDomainEntity, String userId) {
    String log = userId + ":" + frontendLogDomainEntity.getFileName() + ":"
        + frontendLogDomainEntity.getFunctionName() + ":" + frontendLogDomainEntity.getContent();
    String level = frontendLogDomainEntity.getLevel();
    if (level != null) {
      if (level.equalsIgnoreCase(SystemPropertyConstants.DEBUG)) {
        frontEndLogger.debug(log);
      } else if (level.equalsIgnoreCase(SystemPropertyConstants.WARN)) {
        frontEndLogger.warn(log);
      } else if (level.equalsIgnoreCase(SystemPropertyConstants.ERROR)) {
        frontEndLogger.error(log);
      } else {
        frontEndLogger.info(log);
      }
    }

  }
}
