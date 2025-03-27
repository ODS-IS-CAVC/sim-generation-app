package com.catalogap.web;

import com.ulisesbocchio.jasyptspringboot.annotation.EnableEncryptableProperties;
import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.info.Info;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * SpringBootのアプリケーションクラスです.
 */
@SpringBootApplication
@OpenAPIDefinition(info = @Info(title = "catalogap", description = "catalogap", version = "v1"))
@EnableEncryptableProperties
public class WebApplication {

  public static void main(String[] args) {
    SpringApplication.run(WebApplication.class, args);

  }

}
