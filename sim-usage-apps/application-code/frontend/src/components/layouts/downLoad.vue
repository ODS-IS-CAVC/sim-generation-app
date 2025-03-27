<script setup lang="ts">
import { ref, defineProps } from 'vue';
import { scenarioDataDownloadApi } from '@/api-client';
import { useI18n } from 'vue-i18n';
import {
  catalogConsoleLog,
  errorToString,
  ConsoleLogLevel,
} from '@/shared/helpers/consoleLogHelper';

// tはlabelTextList、codesListのjsonファイルを使用
const { t } = useI18n({ useScope: 'global' });
const index = ref(0);
const tab = ref(false);
const downLoadUrl = ref('');

const props = defineProps({
  download: {
    type: Object,
    required: true,
  },
});
function downLoad(paramDataDivision) {
  const param = {
    uuid: props.download.uuid,
    dataDivision: paramDataDivision,
  };
  // ダウンロードAPIを実行する
  DownloadAPI.fetch(param).then(({ items }) => {
    if (items.length === 0) {
      items = [];
    } else {
      //ファイルをダウンロード
      downLoadUrl.value = items;
      const url = downLoadUrl.value;
      const a = document.createElement('a');
      a.href = url;
      a.click();
      URL.revokeObjectURL(url);
    }
  });
}
// バックエンドAPI
const DownloadAPI = {
  async fetch(param) {
    const options: AxiosRequestConfig = {
      params: {
        uuid: param.uuid,
        dataDivision: param.dataDivision,
      },
    };
    return scenarioDataDownloadApi
      .downloadScenarioData({}, '', options)
      .then((res: AxiosResponse<DownloadScenarioDataResponse>) => {
        const items = res.data.results.downloadUrl;
        return Promise.resolve({ items });
      })
      .catch((err) => {
        catalogConsoleLog(
          ConsoleLogLevel.ERROR,
          'シナリオデータダウンロードAPI失敗:' + errorToString(err),
          'downLoad.vue',
          'DownloadAPI',
          true,
          'シナリオデータダウンロードAPI失敗:' + errorToString(err),
        );
        return Promise.resolve({ items: [] });
      });
  },
};
</script>
<template>
  <div class="downLoad-model mt-5 px-2 py-2 border-sm">
    <div class="d-flex">
      <div class="title-pic">&nbsp;</div>
      <v-label class="ml-2 font-weight-bold">
        {{ t('labelTextList.downloadZIP') }}
      </v-label>
    </div>
    <div class="mt-4"></div>
    <v-tabs v-model="tab" class="v-tabs-style">
      <v-tab
        value="1"
        height="30px"
        :class="index === 0 ? 'is-tab-true' : 'is-tab-false'"
        hide-slider
        @click="index = 0"
        >{{ t('labelTextList.scenario') }}</v-tab
      >
      <v-tab
        value="2"
        height="30px"
        class="ml-1"
        :class="index === 1 ? 'is-tab-true' : 'is-tab-false'"
        hide-slider
        @click="index = 1"
        >{{ t('labelTextList.MLData') }}</v-tab
      >
    </v-tabs>
    <div class="mt-1 w-100 border-t-sm"></div>
    <v-tabs-window v-model="tab" class="is-tab-false">
      <v-tabs-window-item value="1">
        <div
          class="d-flex mt-2"
          v-for="(scenarioItem, index1) in props.download.scenarioDataList"
          :key="index1"
        >
          <div class="tabs-item-name-style">
            {{ t(`labelTextList.${scenarioItem.dataDivision}`) }}
          </div>
          <div class="w-33">{{ scenarioItem.size }}</div>
          <v-icon
            class="download-icon-style"
            icon="mdi-download-circle "
            @click="downLoad(scenarioItem.dataDivision)"
          ></v-icon>
        </div>
      </v-tabs-window-item>
      <v-tabs-window-item value="2">
        <div
          class="d-flex mt-2"
          v-for="(studyItem, index2) in download.machineLearningDataList"
          :key="index2"
        >
          <div class="tabs-item-name-style">
            {{ t(`labelTextList.${studyItem.dataDivision}`) }}
          </div>
          <div class="w-33">{{ studyItem.size }}</div>
          <v-icon
            class="download-icon-style"
            icon="mdi-download-circle"
            @click="downLoad(studyItem.dataDivision)"
          ></v-icon>
        </div>
      </v-tabs-window-item>
    </v-tabs-window>
  </div>
</template>
<style lang="scss" scoped>
/* stylelint-disable-next-line selector-class-pattern */
.downLoad-model {
  border-radius: 5px;
  height: 194px;
}

.title-pic {
  width: 5px;
  background-color: #1760a5;
}

.v-tabs-style {
  height: 30px;
}

.is-tab-true {
  background-color: #d3e3ff;
  font-size: 12px;
}

.is-tab-false {
  font-size: 12px;
}

/* 選択したtab文字色 */
.text-secondary {
  /* stylelint-disable-next-line declaration-no-important */
  color: black !important;
}

.tabs-item-name-style {
  width: 60%;
}

.download-icon-style {
  color: #005fa7;
}
</style>
