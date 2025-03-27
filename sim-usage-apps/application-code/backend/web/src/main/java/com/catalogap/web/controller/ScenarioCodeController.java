package com.catalogap.web.controller;

import com.catalogap.applicationcore.scenariocode.ScenarioCodeService;
import com.catalogap.systemcommon.exception.LogicException;
import com.catalogap.web.controller.dto.scenariocode.GetCodeListResponse;
import com.catalogap.web.controller.dto.scenariocode.GetLocationListRequest;
import com.catalogap.web.controller.dto.scenariocode.GetLocationListResponse;
import com.catalogap.web.mapper.ScenarioCodeMapper;
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
 * シナリオコードを取得するAPIコントローラーです.
 */
@RestController
@Tag(name = "ScenarioCode", description = "シナリオコードを取得するAPIコントローラー")
@RequestMapping("/api/codes")
@Validated
@AllArgsConstructor
public class ScenarioCodeController {

  @Autowired
  private ScenarioCodeService service;

  /**
   * 引数をもとにシナリオ検索画面の検索条件に使用するデータをシナリオの属性管理テーブルから検索し、該当するデータを返却する.
   *
   * @param userId ユーザーID
   * @return 該当するデータ
   */
  @Operation(summary = "シナリオの属性管理テーブルから引数をもとにシナリオ検索画面の検索条件に使用するデータを取得する.",
      description = "シナリオの属性管理テーブルから引数をもとにシナリオ検索画面の検索条件に使用するデータを取得する.")
  @ApiResponses(value = {
      @ApiResponse(responseCode = "200", description = "成功",
          content = @Content(mediaType = "application/json",
              schema = @Schema(implementation = GetCodeListResponse.class))),
      @ApiResponse(responseCode = "500", description = "想定外例外",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "500", description = "DBアクセスエラー",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "400", description = "ヒヤリハット種別または発生区間が不足の場合",
          content = @Content(mediaType = "application/json"))})
  @GetMapping("/list")
  public ResponseEntity<GetCodeListResponse> getCodeList(String userId) throws LogicException {
    userId = "sample@email.com";
    GetCodeListResponse getCodeListResponse =
        ScenarioCodeMapper.convertToGetCodeListResponse(this.service.getCodeList(userId));
    return ResponseEntity.ok().body(getCodeListResponse);
  }

  /**
   * 引数をもとにシナリオ検索画面の検索条件に使用するデータを場所マスタテーブルから検索し、該当するデータを返却する.
   *
   * @param getLocationListRequest 検索条件
   * @param userId ユーザーID
   * @return 該当するデータ
   */
  @Operation(summary = "場所マスタテーブルから引数をもとにシナリオ検索画面の検索条件に使用するデータを取得する.",
      description = "場所マスタテーブルから引数をもとにシナリオ検索画面の検索条件に使用するデータを取得する.")
  @ApiResponses(value = {
      @ApiResponse(responseCode = "200", description = "成功",
          content = @Content(mediaType = "application/json",
              schema = @Schema(implementation = GetLocationListResponse.class))),
      @ApiResponse(responseCode = "500", description = "想定外例外",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "400", description = "入力チェックエラー",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "500", description = "DBアクセスエラー",
          content = @Content(mediaType = "application/json")),
      @ApiResponse(responseCode = "400", description = "業務エラー（発生場所が不足の場合)",
          content = @Content(mediaType = "application/json"))})
  @GetMapping("/locationList")
  public ResponseEntity<GetLocationListResponse> getLocationList(
      @Valid GetLocationListRequest getLocationListRequest, String userId) throws LogicException {
    userId = "sample@email.com";
    GetLocationListResponse getLocationListResponse =
        ScenarioCodeMapper.convertToGetLocationListResponse(
            this.service.getLocationList(getLocationListRequest.getSectionId(), userId));
    return ResponseEntity.ok().body(getLocationListResponse);
  }
}
