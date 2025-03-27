<script setup lang="ts">
import scenarioDetail from '@/components/layouts/scenarioDetail.vue';
import downLoad from '@/components/layouts/downLoad.vue';
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { scenarioListApi } from '@/api-client';
import { useI18n } from 'vue-i18n';
import { useTransferFromScenarioInfoStore } from '@/stores/transferFrom/transferFrom';
import {
  catalogConsoleLog,
  errorToString,
  ConsoleLogLevel,
} from '@/shared/helpers/consoleLogHelper';

// tはlabelTextList、codesListのjsonファイルを使用
const { t } = useI18n({ useScope: 'global' });
const uuid = ref('');
const breadItems = ref();

// videoのパースの設定
const videoUrl = ref('');
const displayItem = ref({});
const router = useRouter();

const transferFromScenarioInfoStore = useTransferFromScenarioInfoStore();
//画面を初期表示
onMounted(() => {
  uuid.value = router.currentRoute.value.query.uuid;
  breadItems.value = [
    {
      title: t('labelTextList.search'),
      href: '/search',
      color: '#1760A5',
    },
    {
      title: t('labelTextList.scenario'),
    },
    {
      title: uuid.value,
    },
  ];

  getScenarioDetailAPI.fetch().then(({ item }) => {
    if (item === undefined || item === null) {
      router.push('system/not-found');
    } else {
      displayItem.value = item;
    }
  });

  videoUrl.value = '';
});
// 実際バックエンドAPI
const getScenarioDetailAPI = {
  async fetch() {
    const options: AxiosRequestConfig = {
      params: {
        uuid: uuid.value,
      },
    };
    return scenarioListApi
      .getScenarioDetail({}, '', options)
      .then((res: AxiosResponse<GetScenarioDetailResponse>) => {
        const item = res.data.results;
        return Promise.resolve({ item });
      })
      .catch((err) => {
        catalogConsoleLog(
          ConsoleLogLevel.ERROR,
          'シナリオ情報詳細取得API失敗:' + errorToString(err),
          'scenarioInfoView.vue',
          'getScenarioDetailAPI',
          true,
          'シナリオ情報詳細取得API失敗:' + errorToString(err),
        );
        return Promise.resolve({ item: [] });
      });
  },
};

function setTransferFrom() {
  transferFromScenarioInfoStore.setTransferFromScenarioInfo();
}
</script>
<template>
  <div class="mt-5 ml-6">
    <v-breadcrumbs
      bg-color="background"
      :items="breadItems"
      class="pl-2"
      @click="setTransferFrom()"
    >
      <template #divider>
        <v-icon icon="mdi-chevron-right"></v-icon>
      </template>
    </v-breadcrumbs>
    <div class="mt-2 d-flex position-absolute w-100">
      <div class="info-1-1 px-2">
        <div class="w-100 info-1-1-1">
          <video
            class="h-100 w-100 border-sm content"
            :controls="true"
            v-if="displayItem.videoUrl"
          >
            <source :src="displayItem.videoUrl" type="video/mp4" />
          </video>
        </div>
      </div>

      <div class="info-1-2 mx-6 px-2">
        <scenarioDetail :display="displayItem"></scenarioDetail>
        <downLoad :download="displayItem"></downLoad>
      </div>
    </div>
  </div>
</template>
<style lang="scss" scoped>
.info-1-1 {
  width: 60%;
}

// 幅と高さが16:9の比率を設定する
.info-1-1-1 {
  position: relative;
  height: 100%;
  padding-bottom: 57.75%;
  border-radius: 5px;
}

.info-1-1-1 > .content {
  background-color: black;
  position: absolute;
}

.info-1-2 {
  width: 40%;
}

/* stylelint-disable-next-line no-descending-specificity */
.v-breadcrumbs {
  font-size: 14px;
  padding: 0 8px;
}
</style>
