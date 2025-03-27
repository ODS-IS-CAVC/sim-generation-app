package com.catalogap.web.controller.dto.scenarioinfo;

import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * GET シナリオ情報詳細取得 API のリクエストです.
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class GetScenarioDetailRequest {
  /**
   * UUID.
   */
  @NotEmpty(message = "シナリオのIDは必須です")
  private String uuid;

}
