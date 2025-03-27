package com.catalogap.web.controller.dto.scenariocode;

import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * GET 場所データリスト API のリクエストです.
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class GetLocationListRequest {

  /**
   * 区間ID.
   */
  @NotNull(message = "区間IDは必須です")
  private String sectionId;

}
