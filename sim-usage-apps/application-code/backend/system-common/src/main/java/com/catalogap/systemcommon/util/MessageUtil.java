package com.catalogap.systemcommon.util;

import java.util.Locale;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.MessageSource;
import org.springframework.context.MessageSourceAware;
import org.springframework.stereotype.Component;

/**
 * メッセージ取得用ユーティリティ.
 **/
@Component
public class MessageUtil implements MessageSourceAware {

  private static MessageSource messageSource;

  /**
   * IDに対応するメッセージを取得します(メッセージにプレースホルダーがない場合).
   *
   * @param messageId メッセージID.
   * @return メッセージ
   */
  public static String getMessage(String messageId) {
    return getMessage(messageId, null);
  }

  /**
   * IDに対応するメッセージを取得します(メッセージにプレースホルダーがある場合).
   *
   * @param messageId メッセージID.
   * @param placeholder プレースホルダ.
   * @return メッセージ
   */
  public static String getMessage(String messageId, String[] placeholder) {
    return messageSource.getMessage(messageId, placeholder, Locale.getDefault());
  }

  /**
   * メッセージソースを設定します.
   *
   * @param messageSource メッセージソース.
   */
  @Autowired
  public void setMessageSource(MessageSource messageSource) {
    if (MessageUtil.messageSource == null) {
      MessageUtil.messageSource = messageSource;
    }
  }
}
