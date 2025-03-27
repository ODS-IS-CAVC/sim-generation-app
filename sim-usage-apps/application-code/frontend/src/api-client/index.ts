import axios from 'axios';
import * as apiClient from '@/generated/api-client';
import {
  catalogConsoleLog,
  errorToString,
  ConsoleLogLevel,
} from '@/shared/helpers/consoleLogHelper';

/** api-client の共通の Configuration があればここに定義します。 */
const config = new apiClient.Configuration({});

/** axios の共通の設定があればここに定義します。 */
const axiosInstance = axios.create({});
// リクエスト送信前
axiosInstance.interceptors.request.use(
  async (config) => {
    //ここで、共通処理を追加する

    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// リクエスト送信後
axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const apiUrl = error.config.url;
    //frontendlogAPIの場合は、複数回呼び出しの回避のために、バクエンドに送付しない

    catalogConsoleLog(
      ConsoleLogLevel.ERROR,
      errorToString(error),
      'index.ts',
      'axiosInstance.interceptors.response.use()',
      apiUrl !== '/api/frontendlog/upload',
      errorToString(error),
    );
    //downloadAPIとfrontendlogAPIの場合は、エラー画面に遷移しない
    if (
      apiUrl === '/api/scenario/download' ||
      apiUrl === '/api/frontendlog/upload'
    ) {
      return Promise.reject(error);
    }

    switch (error.response.status) {
      case 404:
        window.location.href = 'error/not-found';
        break; //他のエラーの場合は、400と500など、エラー画面に遷移する
      default:
        window.location.href = 'error/system';
        break;
    }
    return Promise.reject(error);
  },
);

const scenarioListApi = new apiClient.ScenarioListApi(
  config,
  '',
  axiosInstance,
);

const scenarioCodeApi = new apiClient.ScenarioCodeApi(
  config,
  '',
  axiosInstance,
);

const scenarioDataDownloadApi = new apiClient.ScenarioDataDownloadApi(
  config,
  '',
  axiosInstance,
);

const frontEndLogApi = new apiClient.FrontEndLogApi(config, '', axiosInstance);

export { scenarioListApi };
export { scenarioCodeApi };
export { scenarioDataDownloadApi };
export { frontEndLogApi };
