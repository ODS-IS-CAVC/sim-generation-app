package com.catalogap.systemcommon.property;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;


/**
 * application.propertiesの中のcatalogap.jasypt.passwordを取得するためのクラス.  
 * ApplicationPropertiesを作成する際の復号化で利用するため循環参照にならないように別定義とする.  
 */
@Getter
@Setter
@Component
@ConfigurationProperties("catalogap.jasypt")
public class AppProperties4JasyptPass {
  private String password;
}
