package com.catalogap.web.controller;

import com.catalogap.applicationcore.scenarioinfo.ScenarioInfoService;
import com.catalogap.systemcommon.constant.MessageIdConstant;
import com.catalogap.systemcommon.exception.LogicException;
import com.catalogap.systemcommon.exception.response.ErrorResponse;
import com.catalogap.web.controller.dto.scenarioinfo.GetScenarioDetailRequest;
import com.catalogap.web.controller.dto.scenarioinfo.GetScenarioDetailResponse;
import com.catalogap.web.controller.dto.scenarioinfo.GetScenarioListRequest;
import com.catalogap.web.controller.dto.scenarioinfo.GetScenarioListResponse;
import com.catalogap.web.mapper.ScenarioInfoMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * シナリオ情報を取得するAPIコントローラーです.
 */
@RestController
@Tag(name = "ScenarioList", description = "シナリオ情報一覧検索APIコントローラー")
@RequestMapping("/api/scenario")
@Validated
@AllArgsConstructor
public class ScenarioInfoController {

  @Autowired
  private ScenarioInfoService service;

  /**
   * 引数をもとにシナリオ検索画面の検索結果一覧に使用するデータをシナリオの情報テーブルから検索し、該当するデータを返却する.
   *
   * @param getScenarioListRequest 検索条件
   * @param userId ユーザーID
   * @return 該当するデータ
   */
  @Operation(summary = "引数をもとにシナリオ検索画面の検索結果一覧に使用するデータを取得する.",
      description = "引数をもとにシナリオ検索画面の検索結果一覧に使用するデータを取得する.")
  @ApiResponses(value = {
      @ApiResponse(responseCode = "200", description = "成功",
          content = @Content(mediaType = "application/json",
              schema = @Schema(implementation = GetScenarioListResponse.class))),
      @ApiResponse(responseCode = "500", description = "想定外例外",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "400", description = "入力チェックエラー",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "500", description = "DBアクセスエラー",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "400", description = "業務エラー(AWS CloudFront 署名のURL生成に失敗エーラ)",
          content = @Content(mediaType = "application/json"))})
  @GetMapping("/list")
  public ResponseEntity<GetScenarioListResponse> getScenarioList(
      @Valid GetScenarioListRequest getScenarioListRequest, String userId) throws LogicException {
    userId = "sample@email.com";
    GetScenarioListResponse getScenarioListResponse =
        ScenarioInfoMapper.convertToGetScenarioListResponse(
            this.service.getScenarioList(getScenarioListRequest.getNearmissType(),
                getScenarioListRequest.getRequestPage(), getScenarioListRequest.getItemsPerPage(),
                getScenarioListRequest.getHappenTime(), getScenarioListRequest.getHappenSection(),
                getScenarioListRequest.getHappenLocation(), userId));
    return ResponseEntity.ok().body(getScenarioListResponse);
  }

  /**
   * 引数をもとにシナリオ詳細画面に使用するデータをシナリオの情報テーブルから検索し、該当するデータを返却する.
   *
   * @param getScenarioDetailRequest 検索条件
   * @param userId ユーザーID
   * @return 該当するデータ
   */
  @Operation(summary = "引数をもとにシナリオ詳細画面に使用するデータを取得する.", description = "引数をもとにシナリオ詳細画面に使用するデータを取得する.")
  @ApiResponses(value = {
      @ApiResponse(responseCode = "200", description = "成功",
          content = @Content(mediaType = "application/json",
              schema = @Schema(implementation = GetScenarioDetailResponse.class))),
      @ApiResponse(responseCode = "500", description = "想定外例外",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "400", description = "入力チェックエラー",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "500", description = "DBアクセスエラー",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "400", description = "業務エラー（AWS CloudFront 署名のURL生成に失敗エーラ)",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "404", description = "業務エラー(UUIDが存在しないまたはログインユーザの権限がない)",
          content = @Content(mediaType = "application/json"))})
  @GetMapping("/detail")
  public ResponseEntity<?> getScenarioDetail(
      @Valid GetScenarioDetailRequest getScenarioDetailRequest, String userId)
      throws LogicException {
    userId = "sample@email.com";
    GetScenarioDetailResponse getScenarioDetailResponse =
        ScenarioInfoMapper.convertToGetScenarioDetailResponse(
            this.service.getScenarioDetail(getScenarioDetailRequest.getUuid(), userId));
    if (getScenarioDetailResponse == null) {
      return ResponseEntity.status(HttpStatus.NOT_FOUND)
          .body(new ErrorResponse(new LogicException(null, MessageIdConstant.E4L005,
              new String[] {"UUIDが存在しないまたはログインユーザの権限がない"})));
    }
    return ResponseEntity.ok().body(getScenarioDetailResponse);
  }
}
