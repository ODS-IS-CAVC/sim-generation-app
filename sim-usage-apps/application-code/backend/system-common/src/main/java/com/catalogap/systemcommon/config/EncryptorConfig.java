package com.catalogap.systemcommon.config;

import com.catalogap.systemcommon.property.AppProperties4JasyptPass;
import org.jasypt.encryption.StringEncryptor;
import org.jasypt.encryption.pbe.PooledPBEStringEncryptor;
import org.jasypt.encryption.pbe.config.SimpleStringPBEConfig;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 *  Jasyptの復号化設定クラス.
 */
@Configuration
public class EncryptorConfig {
  // application.propertiesの"catalogap.jasypt.password"を取得

  @Autowired
  private AppProperties4JasyptPass prop; // encryptorBeanという名前でEncryptorをBean登録する  

  /**
   * Jasyptの復号化文字.
   *
   * @return encryptor対象
   */
  @Bean(name = "encryptorBean")
  public StringEncryptor stringEncryptor() {
    SimpleStringPBEConfig config = new SimpleStringPBEConfig();
    config.setPassword(prop.getPassword());
    // 下記パラメータ値は参考値です。
    config.setAlgorithm("PBEWithMD5AndDES");
    config.setKeyObtentionIterations("1000");
    config.setPoolSize("1");
    config.setProviderName("SunJCE");
    config.setSaltGeneratorClassName("org.jasypt.salt.RandomSaltGenerator");
    config.setStringOutputType("base64");

    PooledPBEStringEncryptor encryptor = new PooledPBEStringEncryptor();
    encryptor.setConfig(config);
    return encryptor;
  }
}
