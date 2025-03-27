package com.catalogap.web.mapper;

import com.catalogap.applicationcore.frontendlog.FrontendLogDomainEntity;
import com.catalogap.web.controller.dto.frontendlog.UploadFrontendLogRequest;

/**
 * FrontendLogController のマッパーです.
 */

public class FrontEndLogMapper {
  /**
   * {@link UploadFrontendLogRequest} オブジェクトを {@link FrontendLogDomainEntity} に変換します.
   *
   * @param uploadFrontendLogRequest オブジェクト.
   * @return {@link SampleDataDomainEntity} オブジェクト.
   */
  public static FrontendLogDomainEntity convertToFrontendLogDomainEntity(
      UploadFrontendLogRequest uploadFrontendLogRequest) {
    if (uploadFrontendLogRequest == null) {
      return null;
    }
    return new FrontendLogDomainEntity(uploadFrontendLogRequest.getLevel(),
        uploadFrontendLogRequest.getContent(), uploadFrontendLogRequest.getFileName(),
        uploadFrontendLogRequest.getFunctionName());
  }

}
