package com.catalogap.web.controller;

import com.catalogap.applicationcore.frontendlog.FrontEndLogService;
import com.catalogap.systemcommon.exception.LogicException;
import com.catalogap.web.controller.dto.frontendlog.UploadFrontendLogRequest;
import com.catalogap.web.mapper.FrontEndLogMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * フロントエンドログ出力APIコントローラーです.
 */
@RestController
@Tag(name = "FrontEndLog", description = "フロントエンドログ出力APIコントローラー")
@RequestMapping("/api/frontendlog")
@Validated
@AllArgsConstructor
public class FrontendLogController {

  @Autowired
  private FrontEndLogService service;

  /**
   * フロントエンドのログデータをアップロードする.
   *
   * @param uploadFrontendLogRequest 検索条件
   * @param userId ユーザーID
   * @return 該当するデータ
   */
  @Operation(summary = "フロントエンドのログデータをアップロードする.", description = "フロントエンドのログデータをアップロードする.")
  @ApiResponses(value = {@ApiResponse(responseCode = "200", description = "成功"),
      @ApiResponse(responseCode = "500", description = "想定外例外",
          content = @Content(mediaType = "application/json"))})
  @PostMapping("/upload")
  public ResponseEntity<Void> uploadFrontendLog(
      @RequestBody @Valid UploadFrontendLogRequest uploadFrontendLogRequest, String userId) {
    userId = "sample@email.com";
    this.service.saveLog(
        FrontEndLogMapper.convertToFrontendLogDomainEntity(uploadFrontendLogRequest), userId);
    return ResponseEntity.noContent().build();
  }
}
