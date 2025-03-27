<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { listSearch } from '@/stores/listSearch/listSearch';
import { useSearchStore } from '@/stores/search/search';
import type { SearchControl } from '@/stores/search/search.model';
import type { GetListDataResultsResponse } from '@/generated/api-client';
import { scenarioListApi } from '@/api-client';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { dateFormat } from '@/shared/helpers/datetimeHelper';
import { useTransferFromScenarioInfoStore } from '@/stores/transferFrom/transferFrom';
import { useItemsPerPageStore } from '@/stores/search/itemsPerPage';
import {
  catalogConsoleLog,
  errorToString,
  ConsoleLogLevel,
} from '@/shared/helpers/consoleLogHelper';

// tはlabelTextList、codesListのjsonファイルを使用
const { t } = useI18n({ useScope: 'global' });
// 表示件数データ
const selectCountItems = [10, 20, 30];
// store初期化
const searchStore = useSearchStore();
const transferFromScenarioInfoStore = useTransferFromScenarioInfoStore();
const itemsPerPageStore = useItemsPerPageStore();

// 表示用一覧データ
const displayItem = ref([]);

const totalPage = ref(0);
const displayFlag = ref(true);

//データをロード
const handleSearchEvent = () => {
  onMountedGetResult();
};
//画面を初期表示
onMounted(() => {
  const listWorkStore = listSearch();
  listWorkStore.on('search', handleSearchEvent);
});

// データをロード
const loadItems = () => {
  const searchParam = {
    ...searchStore.getPageControl,
    ...searchStore.getSearch,
    ...searchStore.getSelectSectionRow,
    ...searchStore.getSelectLocationRow,
    ...itemsPerPageStore.getItemsPerPageControl,
  };
  getScenarioListAPI.fetch(searchParam).then(({ total, items }) => {
    if (items.length == 0) {
      items = [];
      displayFlag.value = false;
    } else {
      displayItem.value = items;
      displayFlag.value = true;
    }
    totalPage.value = total;
  });
};

// バックエンドAPI
const getScenarioListAPI = {
  async fetch(searchControl: SearchControl) {
    const options: AxiosRequestConfig = {
      params: {
        happenTime:
          searchControl.happenTime === null || searchControl.happenTime === ''
            ? ''
            : dateFormat(searchControl.happenTime),
        happenSection: searchControl.sectionId,
        happenLocation: searchControl.locationId,
        nearmissType: searchControl.nearmissType.toString(),
        requestPage: searchControl.page.toString(),
        itemsPerPage: searchControl.itemsPerPage.toString(),
      },
    };
    // シナリオ情報一覧検索APIを実行
    return scenarioListApi
      .getScenarioList({}, '', options)
      .then((res: AxiosResponse<GetListDataResultsResponse>) => {
        const total = res.data.results.counts;
        const items = res.data.results.lists;

        return Promise.resolve({ total, items });
      })
      .catch((err) => {
        catalogConsoleLog(
          ConsoleLogLevel.ERROR,
          'シナリオ情報一覧検索API失敗:' + errorToString(err),
          'searchResult.vue',
          'getScenarioListAPI',
          true,
          'シナリオ情報一覧検索API失敗:' + errorToString(err),
        );

        return Promise.resolve({ total: 0, items: [] });
      });
  },
};

// v-chip表示用
function chipsRows(item) {
  const chipsRows = [];
  const chipLength = 7; // ヒヤリハットが7個おきに行替えする
  for (let i = 0; i < item.length; i += chipLength) {
    chipsRows.push(item.slice(i, i + chipLength));
  }

  return chipsRows;
}
// 画面を初回ロードと表示件数変更の検索結果取得
function onMountedGetResult() {
  if (!transferFromScenarioInfoStore.isTransferFromScenarioInfo) {
    searchStore.setPage(1);
  }
  transferFromScenarioInfoStore.clear();
  loadItems();
}
// pagination検索結果取得
function paginationGetResult() {
  loadItems();
}
// シナリオ情報画面へ遷移
const router = useRouter();
function displayScenarioInfo(uuid) {
  router.push({ path: '/scenario', query: { uuid: uuid } });
}
</script>

<template>
  <div class="d-flex px-2">
    <v-label> {{ t('labelTextList.itemShown') }}</v-label>
    <div>
      <v-select
        class="display-count-select ml-1 border-sm"
        v-model="itemsPerPageStore.$state.itemsPerPageControl.itemsPerPage"
        :items="selectCountItems"
        @update:model-value="onMountedGetResult()"
      >
      </v-select>
    </div>

    <div class="ml-auto mr-0">
      <v-pagination
        class="grid-pagination"
        v-model="searchStore.$state.pageControl.page"
        :length="Math.ceil(totalPage / itemsPerPageStore.getItemsPerPage)"
        :total-visible="7"
        @update:model-value="paginationGetResult()"
        show-first-last-page
      ></v-pagination>
    </div>
  </div>
  <div v-if="displayFlag" class="list-body mt-4 px-2">
    <v-data-iterator
      :items="displayItem"
      :page="searchStore.getPage"
      :items-per-page="itemsPerPageStore.getItemsPerPage"
    >
      <template #default="{ items }">
        <template v-for="(item, i) in items" :key="i"
          ><div
            class="search-result mb-4 px-4 py-4 d-flex border-sm"
            @click="displayScenarioInfo(item.raw.uuid)"
          >
            <div class="search-result-pic border-sm">
              <v-img
                class="pic"
                :src="item.raw.videoThumbnailUrl"
                eager
              ></v-img>
            </div>
            <div class="search-result-part ml-4 d-flex">
              <div class="w-100">
                <div class="mt-2">
                  {{ t('labelTextList.areaResult') }}{{ item.raw.sectionName }}
                </div>
                <div class="mt-2">
                  {{ t('labelTextList.locationResult')
                  }}{{ item.raw.locationName }} 付近
                </div>
                <div class="d-flex">
                  <div class="mt-2">
                    {{ t('labelTextList.nearMissResult') }}
                  </div>
                  <div>
                    <div
                      v-for="(row, index1) in chipsRows(
                        item.raw.nearmissTypeList,
                      )"
                      :key="index1"
                    >
                      <div class="d-flex">
                        <div>
                          <v-chip
                            label=""
                            class="ml-1 mt-1"
                            v-for="(row1, index2) in row"
                            :key="index2"
                            >{{ t(`codesList.${row1.nearmissType}`) }}</v-chip
                          >
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </template>
    </v-data-iterator>
  </div>
  <div v-if="!displayFlag" class="list-body mt-4 pt-4 pl-4">
    <v-label style="color: #1760a5">
      {{ t('labelTextList.message1') }}<br />{{
        t('labelTextList.message2')
      }}</v-label
    >
  </div>
</template>

<style lang="scss" scoped>
.search-result {
  border-radius: 5px;
}

.pic {
  /* stylelint-disable-next-line selector-class-pattern */
  :deep(.v-img__img--contain) {
    object-fit: cover;
  }
}

// v-selectの高さ
:deep(.v-select .v-field.v-field) {
  max-height: 32px;
}

// v-selectのiconと文字
:deep(.v-field) {
  display: inline-flex;
}

// 表示件数のv-selectの表示
.display-count-select {
  /* stylelint-disable-next-line declaration-no-important */
  box-sizing: content-box !important;
}

/* 一覧に写真サイズ */
.search-result-pic {
  width: 246px;
  height: 136px;
  border-radius: 5px;
}

.search-result-part {
  font-size: 12px;
}

// v-selectの様式
/* stylelint-disable-next-line selector-class-pattern */
:deep(.v-field__input) {
  display: inline;
}

// v-selectの様式
/* stylelint-disable-next-line selector-class-pattern */
:deep(.v-input__details) {
  display: none;
}

// v-paginationの高さ
/* stylelint-disable-next-line selector-class-pattern */
:deep(.v-btn--size-default) {
  height: 32px;
}

// v-paginationの様式
.grid-pagination:deep(ul) {
  border-left: 1px solid;
  border-top: 1px solid;
  border-bottom: 1px solid;
  border-color: #d9d9d9;

  li {
    margin: 0;
    border-right: 1px solid;
    border-color: #d9d9d9;

    button {
      /* stylelint-disable-next-line declaration-no-important */
      height: 32px !important;
      /* stylelint-disable-next-line declaration-no-important */
      width: 32px !important;
      font-size: 16px;
    }
  }

  /* stylelint-disable-next-line selector-class-pattern */
  li:not(:has(button.v-btn--disabled), :has(button[aria-current='true'])) {
    background-color: #d3e3ff;
  }
}

.list-body {
  height: 744px;
  overflow-y: scroll;
}
</style>
