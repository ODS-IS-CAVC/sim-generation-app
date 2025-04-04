package com.catalogap.systemcommon.util;

import org.springframework.beans.BeansException;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.stereotype.Component;

/**
 * アプリケーションコンテキストラッパークラスです.
 */
@Component
public class ApplicationContextWrapper implements ApplicationContextAware {

  private static ApplicationContext context;

  @Override
  public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
    context = applicationContext;
  }

  public static <T> T getBean(Class<T> clazz) {
    return context.getBean(clazz);
  }

  public static Object getBean(String name) {
    return context.getBean(name);
  }
}
