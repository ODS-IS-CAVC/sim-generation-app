package com.catalogap.systemcommon.property;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;


/**
 * application.propertiesの中でcatalogap固有の設定値（prefixがcatalogap）を取得するためのクラス.
 */
@Getter
@Setter
@Component
@ConfigurationProperties("catalogap")
public class AppProperties {
  private String test;
  private String hoge;
}
