package com.catalogap.web.config;

import java.io.CharArrayWriter;
import org.apache.catalina.valves.AccessLogValve;

/**
 * 出力log方法を書き換える.
 */
public class ConsoleAccessLogValve extends AccessLogValve {
  @Override
  public void log(CharArrayWriter message) {
    System.out.println(message.toString());
  }

}
