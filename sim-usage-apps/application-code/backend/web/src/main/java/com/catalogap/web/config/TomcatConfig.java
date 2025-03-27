package com.catalogap.web.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.embedded.tomcat.TomcatServletWebServerFactory;
import org.springframework.boot.web.server.WebServerFactoryCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * tomcatアクセスログの出力用のクラスです.
 */
@Configuration
public class TomcatConfig {

  @Value("${server.tomcat.accesslog.pattern}")
  private String accesslogPattern;

  /**
   * 設定クラスの作成とカスタムValveの追加.
   *
   * @return カスタムファクトリ.
   */
  @Bean
  public WebServerFactoryCustomizer<TomcatServletWebServerFactory> accessLogCustomizer() {
    return factory -> {
      ConsoleAccessLogValve valve = new ConsoleAccessLogValve();
      valve.setPattern(accesslogPattern);
      factory.addContextValves(valve);
    };
  }
}
