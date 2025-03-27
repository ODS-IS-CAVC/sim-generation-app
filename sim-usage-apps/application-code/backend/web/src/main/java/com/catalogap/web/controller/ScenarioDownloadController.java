package com.catalogap.web.controller;

import com.catalogap.applicationcore.scenariodownload.ScenarioDownloadService;
import com.catalogap.systemcommon.exception.LogicException;
import com.catalogap.web.controller.dto.scenariodownload.DownloadScenarioDataRequest;
import com.catalogap.web.controller.dto.scenariodownload.DownloadScenarioDataResponse;
import com.catalogap.web.mapper.ScenarioDownloadMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * シナリオデータダウンロードAPIコントローラーです.
 */
@RestController
@Tag(name = "ScenarioDataDownload", description = "シナリオデータダウンロードAPIコントローラー")
@RequestMapping("/api/scenario")
@Validated
@AllArgsConstructor
public class ScenarioDownloadController {

  @Autowired
  private ScenarioDownloadService service;

  /**
   * 引数をもとにシナリオのデータおよび機械学習用の画像のデータをダウンロードする.
   *
   * @param downloadScenarioDataRequest 検索条件
   * @param userId ユーザーID
   * @return シナリオデータのダウンロードurl
   */
  @Operation(summary = "引数をもとにシナリオのデータおよび機械学習用の画像のデータをダウンロードする.",
      description = "引数をもとにシナリオのデータおよび機械学習用の画像のデータをダウンロードする.")
  @ApiResponses(value = {
      @ApiResponse(responseCode = "200", description = "成功",
          content = @Content(mediaType = "application/json",
              schema = @Schema(implementation = DownloadScenarioDataResponse.class))),
      @ApiResponse(responseCode = "500", description = "想定外例外",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "400", description = "入力チェックエラー",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "500", description = "DBアクセスエラー",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "400", description = "業務エラー（AWS CloudFront 署名のURL生成に失敗エーラ)",
          content = @Content(mediaType = "application/json"))})
  @GetMapping("/download")
  public ResponseEntity<DownloadScenarioDataResponse> downloadScenarioData(
      @Valid DownloadScenarioDataRequest downloadScenarioDataRequest, String userId)
      throws LogicException {
    userId = "sample@email.com";
    DownloadScenarioDataResponse downloadScenarioDataResponse =
        ScenarioDownloadMapper.convertToDownloadScenarioDataResponse(
            this.service.downloadScenarioData(downloadScenarioDataRequest.getUuid(),
                downloadScenarioDataRequest.getDataDivision(), userId));
    return ResponseEntity.ok().body(downloadScenarioDataResponse);
  }


}
