<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useForm } from 'vee-validate';
import { useI18n } from 'vue-i18n';
import { listSearch } from '@/stores/listSearch/listSearch';
import { useSearchStore } from '@/stores/search/search';
import VueDatePicker from '@vuepic/vue-datepicker';
import { useLanguageStore } from '@/stores/language/language';
import { scenarioCodeApi } from '@/api-client';
import {
  catalogConsoleLog,
  errorToString,
  ConsoleLogLevel,
} from '@/shared/helpers/consoleLogHelper';

// tはlabelTextList、codesListのjsonファイルを使用
const { t } = useI18n({ useScope: 'global' });
// 場所リスト
const selectLocationItems = ref([]);
// 区間リスト
const selectSectionItems = ref([]);
// チェックボックスリスト
const checkboxItems = ref([]);

const selectSection = ref();

// store初期化
const searchStore = useSearchStore();
const languageStore = useLanguageStore();

// 初期表示時、区間リストとチェックボックスの値の取得api
const getCodeListAPI = {
  async fetch() {
    const options: AxiosRequestConfig = {
      params: {},
    };
    return scenarioCodeApi
      .getCodeList({}, options)
      .then((res: AxiosResponse<GetListDataResultsResponse>) => {
        const items = res.data.results;
        return Promise.resolve({ items });
      })
      .catch((err) => {
        catalogConsoleLog(
          ConsoleLogLevel.ERROR,
          '検索条件コード値取得API失敗:' + errorToString(err),
          'searchCondition.vue',
          'getCodeListAPI',
          true,
          '検索条件コード値取得API失敗:' + errorToString(err),
        );
        return Promise.resolve({ items: [] });
      });
  },
};

// 場所リストの取得api
const getLocationListAPI = {
  async fetch() {
    const options: AxiosRequestConfig = {
      params: {
        sectionId: searchStore.getSelectSectionId,
      },
    };

    return scenarioCodeApi
      .getLocationList({}, '', options)
      .then((res: AxiosResponse<GetListDataResultsResponse>) => {
        const items = res.data.results;
        return Promise.resolve({ items });
      })
      .catch((err) => {
        catalogConsoleLog(
          ConsoleLogLevel.ERROR,
          '発生場所コード値取得API失敗:' + errorToString(err),
          'searchCondition.vue',
          'getLocationListAPI',
          true,
          '発生場所コード値取得API失敗:' + errorToString(err),
        );

        return Promise.resolve({ items: [] });
      });
  },
};

//検索のフォーム項目の検証ルールと初期化
const { handleSubmit } = useForm({
  initialValues: {
    happenTime: '',
    selectSection: '',
    selectLocation: '',
    nearmissType: [],
  },
});

//検索イベントを引き渡される
const triggerEvent = () => {
  const listSearchStore = listSearch();
  listSearchStore.emit('search');
};

// //検索イベント用
const submit = handleSubmit(() => {
  triggerEvent();
});

// datePicker用
const datePickerLanguage = computed(() => languageStore.getLanguageCode).value;
const datePickerFormat = computed(
  () => languageStore.getDatePickerFormat,
).value;

// 初期表示時、区間リストとチェックボックスの値の取得
onMounted(() => {
  getCodeListAPI.fetch().then(({ items }) => {
    if (items === undefined || items === null) {
      items = [];
    } else {
      // urlで初期表示の場合、画面に検索条件をクリアする
      selectSectionItems.value = items.happenSection;
      checkboxItems.value = items.nearmissType;
      triggerEvent();
    }
  });
  if (searchStore.getSelectSectionRow != null) {
    //  発生場所欄をクリックできる
    disableLocationFlag.value = false;
    if (selectLocationItems.value.length === 0) {
      // 発生場所リストを検索する
      getLocationListAPI.fetch().then(({ items }) => {
        if (items === undefined || items === null) {
          selectLocationItems.value = [];
        } else {
          selectLocationItems.value = items.happenLocation;
        }
      });
    }
  } else {
    disableLocationFlag.value = true;
  }
});

// 発生場所表示フラグの設定
// 場所リストの取得
const disableLocationFlag = ref(true);
function setLocationFlag() {
  selectSection.value = searchStore.getSelectSectionRow;
  // 発生区間があり、 発生場所が押下できる
  if (searchStore.getSelectSectionRow != null) {
    //  発生場所欄をクリア
    disableLocationFlag.value = false;
    searchStore.clearSelectLocationRow();
    // 発生場所リストを検索する
    getLocationListAPI.fetch().then(({ items }) => {
      if (items === undefined || items === null) {
        items = [];
      } else {
        selectLocationItems.value = items.happenLocation;
      }
    });
    // 発生区間がない、 発生場所が押下できない
  } else {
    disableLocationFlag.value = true;
    //  発生場所欄をクリア
    selectLocationItems.value = [];
    searchStore.clearSelectLocationRow();
  }
}
// 全てクリアの実装
function clearFunction() {
  searchStore.setNearmissType([]);
}
</script>

<template>
  <div class="mt-5 ml-6 px-2">
    <form id="searchForm" @submit="submit">
      <div class="font-weight-bold">{{ t('labelTextList.filters') }}</div>
      <div class="mt-4 d-flex">
        <div class="title-pic">&nbsp;</div>
        <v-label class="ml-2 wrap">{{ t('labelTextList.dateTime') }}</v-label>
      </div>
      <div class="mt-1">
        <VueDatePicker
          v-model="searchStore.$state.search.happenTime"
          cancel-text="Close"
          :locale="datePickerLanguage"
          :multiple="false"
          :format="datePickerFormat"
        />
      </div>
      <div class="mt-4 d-flex flex-wrap">
        <div class="title-pic">&nbsp;</div>
        <v-label class="ml-2">{{ t('labelTextList.happenLocation') }}</v-label>
      </div>
      <!-- 発生区間 -->
      <div class="mt-1">
        <div class="select-pic-style d-flex flex-wrap border-sm">
          <v-select
            class="select-style"
            :placeholder="t('labelTextList.selectArea')"
            v-model="searchStore.$state.selectSectionRow"
            :items="selectSectionItems"
            item-title="sectionName"
            item-value="sectionId"
            clearable
            prepend-inner-icon="mdi-map-outline"
            bg-color="#FFFFFF"
            base-color="#FFFFFF"
            persistent-hint
            return-object
            single-line
            @update:model-value="setLocationFlag()"
          >
          </v-select>
        </div>
      </div>
      <!-- 発生場所 -->
      <div class="mt-1">
        <div
          class="select-pic-style border-sm"
          style="background-color: #f2f2f2"
        >
          <v-select
            class="select-style"
            :label="''"
            v-model="searchStore.$state.selectLocationRow"
            :items="selectLocationItems"
            item-title="locationName"
            item-value="locationId"
            clearable
            :disabled="disableLocationFlag"
            prepend-inner-icon="mdi-map-marker-outline"
            return-object
            bg-color="#FFFFFF"
            base-color="#FFFFFF"
            auto
          >
          </v-select>
        </div>
      </div>

      <div class="mt-4 d-flex">
        <div class="title-pic">&nbsp;</div>
        <v-label class="ml-2">{{
          t('labelTextList.nearMissTriggers')
        }}</v-label>
        <v-btn
          variant="text"
          class="all-clear ml-auto mr-0"
          @click="clearFunction()"
          color="#FFFFFF"
          height="24px"
        >
          {{ t('labelTextList.allClear') }}
        </v-btn>
      </div>

      <div class="reason">
        <div class="reason-body mt-1">
          <v-checkbox-btn
            v-for="item in checkboxItems"
            class="mt-1"
            :key="item.code"
            :value="item.code"
            :label="t(`codesList.${item.code}`)"
            v-model="searchStore.$state.search.nearmissType"
            multiple
          ></v-checkbox-btn>
        </div>
      </div>

      <div class="mt-4">
        <v-btn class="h-8 w-100" type="commit">{{
          t('labelTextList.search')
        }}</v-btn>
      </div>
    </form>
  </div>
</template>

<style lang="scss" scoped>
.title-pic {
  background-color: #1760a5;
  width: 5px;
}

// v-selectの高さ
:deep(.v-select .v-field.v-field) {
  max-height: 32px;
}

// v-selectのiconと文字
:deep(.v-field) {
  display: inline-flex;
}

.all-clear {
  font-size: 12px;

  /* stylelint-disable-next-line scss/double-slash-comment-empty-line-before */
  // 全てをクリアボタンの文字色
  /* stylelint-disable-next-line selector-class-pattern */
  :deep(.v-btn__content) {
    color: #4781b8;
  }
}
/* stylelint-disable-next-line scss/double-slash-comment-empty-line-before */
// 全てをクリアボタンの高さ
/* stylelint-disable-next-line selector-class-pattern */
:deep(.v-btn--size-default) {
  padding: 0;
}

.reason {
  height: 432px;
  overflow-y: scroll;
}

.reason-body {
  font-size: 14px;
}
/* stylelint-disable-next-line rule-empty-line-before */
.wrap {
  word-wrap: break-word;
  white-space: normal;
}

// チェックボックスの高さ
/* stylelint-disable-next-line selector-class-pattern */
.v-selection-control--density-default {
  --v-selection-control-size: 32px;
}

// v-select :選択した表示ラベルの様式
.select-style {
  // /* stylelint-disable-next-line declaration-no-important */
  /* stylelint-disable-next-line declaration-no-important */
  box-sizing: content-box !important;
}
/* stylelint-disable-next-line selector-class-pattern */
:deep(.v-field__input) {
  display: inline;
  width: 215px;
}

// v-selectの様式
/* stylelint-disable-next-line selector-class-pattern */
:deep(.v-input__details) {
  display: none;
}
/* stylelint-disable-next-line scss/double-slash-comment-empty-line-before */
// datePickerの高さ
/* stylelint-disable-next-line selector-class-pattern */
:deep(.dp__input) {
  height: 32px;
  font-size: 14px;
}
</style>
