package com.catalogap.web.config;

import com.catalogap.web.filter.Slf4jMdcFilter;
import jakarta.servlet.Filter;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;

/**
 * catalogap Web用の設定クラスです.
 */
@Configuration
@ComponentScan(basePackages = {"com.catalogap"})
public class CatalogApWebConfig {
  public static final String DEFAULT_RESPONSE_TOKEN_HEADER = "Response_Token";
  public static final String DEFAULT_MDC_UUID_TOKEN_KEY = "Slf4jMDCFilter.UUID";

  private String responseHeader = DEFAULT_RESPONSE_TOKEN_HEADER;
  private String mdcTokenKey = DEFAULT_MDC_UUID_TOKEN_KEY;

  /**
   * log4jMdcFilter の設定をします.
   *
   * @return log4jMdcFilter.
   */
  @Bean
  public FilterRegistrationBean<Filter> log4jMdcFilter() {
    final FilterRegistrationBean<Filter> registrationBean = new FilterRegistrationBean<>();
    final Slf4jMdcFilter log4jMdcFilterFilter =
        new Slf4jMdcFilter(responseHeader, mdcTokenKey, null);
    registrationBean.setFilter(log4jMdcFilterFilter);
    registrationBean.setOrder(2);
    return registrationBean;
  }
}
