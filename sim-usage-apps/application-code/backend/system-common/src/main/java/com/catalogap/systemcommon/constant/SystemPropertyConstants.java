package com.catalogap.systemcommon.constant;

/**
 * システムプロパティ用クラス.
 */
public class SystemPropertyConstants {
  /** アプリケーションログのロガー名. */
  public static final String APPLICATION_LOG_LOGGER = "application.log";
  public static final String TOMCAT_LOG_LOGGER = "org.apache.tomcat";
  public static final String FRONTEND_LOG_LOGGER = "front.log";
  /** 改行文字. */
  public static final String LINE_SEPARATOR = System.getProperty("line.separator");

  /** データ区分 OpenDRIVE(xodr). */
  public static final String OPEN_DRIVE = "0";

  /** データ区分 vehicleTrajectory. */
  public static final String VEHICLE_TRAJECTORY = "1";

  /** データ区分 SdmgScenario. */
  public static final String SDMG_SCENARIO = "2";

  /** データ区分 openScenario. */
  public static final String OPEN_SCENARIO = "3";

  /** データ区分 機械学習(jpg). */
  public static final String MACHINE_LEARNING = "4";

  /** シナリオ可否フラグ 0: ダウンロード可. */
  public static final String SCENARIO_POSSIBILITY_FLAG_YES = "0";

  /** 機械学習可否フラグ 0: ダウンロード可. */
  public static final String ML_POSSIBILITY_FLAG_YES = "0";

  /** ログレベル 情報レベル (INFO). */
  public static final String INFO = "INFO";

  /** ログレベル デバッグレベル (DEBUG). */
  public static final String DEBUG = "DEBUG";

  /** ログレベル 警告レベル (WARN). */
  public static final String WARN = "WARN";

  /** ログレベル エラーレベル (ERROR). */
  public static final String ERROR = "ERROR";

  /** 1048576 は 1MB をバイトに変換したサイズです (1MB = 1024 * 1024 バイト). */
  public static final double MB_TO_BYTES = 1048576.0;

  /** 1024 は 1MB をバイトに変換したサイズです (1MB = 1024 KB). */
  public static final double KB_TO_BYTES = 1024.0;

  /** ファイルサイズの単位. */
  public static final String MB = "MB";

  /** ファイルサイズの単位KB. */
  public static final String KB = "KB";
}
