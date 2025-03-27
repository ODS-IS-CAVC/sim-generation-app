/* stylelint-disable selector-class-pattern */ /* stylelint-disable
selector-class-pattern */
<script setup lang="ts">
import { computed, ref } from 'vue';
import { useLanguageStore } from '@/stores/language/language';
import BrandLogo from '../uiElement/BrandLogo.vue';
import { useI18n } from 'vue-i18n';
import { varLang } from '@/shared/helpers/languageHelper.ts';

// tはlabelTextListのjsonファイルを使用
const { t, locale } = useI18n({ useScope: 'global' });

// stores
const languageStore = useLanguageStore();
// computed
const isAuthenticated = true;

const itemData = ['日本語', 'English'];
let index1 = ref(0);
const selectElement = ref(null);
let selected = ref('');
const language = computed(() => languageStore.getLanguage).value;
// ストアの言語が""の場合、ブラウザの言語を使用
if (language === '') {
  locale.value = varLang;
  if (varLang === 'ja') {
    languageStore.setLanguage('日本語');
    selected = ref('日本語');
    index1 = ref(0);
  } else {
    languageStore.setLanguage('English');
    selected = ref('English');
    index1 = ref(1);
  }
  // ストアの言語が日本語の場合、日本語を使用
} else if (language === '日本語') {
  locale.value = 'ja';
  languageStore.setLanguage('日本語');
  selected = ref('日本語');
  index1 = ref(0);
  // ストアの言語が英語の場合、英語を使用
} else if (language === 'English') {
  locale.value = 'en';
  languageStore.setLanguage('English');
  selected = ref('English');
  index1 = ref(1);
}

const avatar = ref(import.meta.env.VITE_CONTENT_PATH + 'avatar.png');

const select = (index) => {
  index1.value = index;
  selected.value = [itemData[index]]; // 選択した項目を選択状態にする
  if (languageStore.getLanguage !== itemData[index]) {
    if (itemData[index] === '日本語') {
      languageStore.setLanguage('日本語');
      location.reload();
    } else if (itemData[index] === 'English') {
      languageStore.setLanguage('English');
      location.reload();
    }
  }
  selectElement.value.menu = false; // 選択したあとでメニューを閉じる
};
</script>

<template>
  <v-app class="app-header">
    <v-app-bar
      class="app-header-bar"
      name="app-bar"
      color="#D3E3FF"
      data-test="appHeader"
      style="height: 40px"
    >
      <v-app-bar-title>
        <BrandLogo @click="(_: MouseEvent) => $router.replace('/search')" />
      </v-app-bar-title>
      <v-spacer />

      <template v-if="isAuthenticated">
        <v-select
          :items="itemData"
          item-text="text"
          item-value="value"
          v-model="selected"
          class="d-flex mr-n8 app-select"
          ref="selectElement"
        >
          <template #item="{ index }">
            <v-list-item
              class="app-list px-4"
              :title="itemData[index]"
              @click="select(index)"
              :append-icon="index1 == index ? 'mdi-check' : ''"
            >
            </v-list-item>
          </template>
        </v-select>
        <!-- 登録者 -->
        <v-btn color="on-primary">
          <v-avatar color="#FFFFFF" size="24px">
            <v-img :src="avatar" alt="avatar"></v-img>
          </v-avatar>
        </v-btn>
      </template>
    </v-app-bar>
  </v-app>
</template>

<style lang="scss" scoped>
/* stylelint-disable-next-line block-no-empty */
.app-header {
  height: 40px;
}
/* stylelint-disable-next-line selector-class-pattern */
.app-header:deep(> .v-application__wrap) {
  min-height: 0;
}

.app-select {
  justify-content: flex-end;
  font-weight: bold;
}

/* stylelint-disable-next-line selector-class-pattern */
.app-select:deep(.v-input__control .v-field .v-field__overlay) {
  background-color: #d3e3ff;
}

/* stylelint-disable-next-line selector-class-pattern */
.app-select:deep(.v-input__control .v-field .v-field__outline::before) {
  /* stylelint-disable-next-line declaration-no-important */
  border-bottom-style: none !important;
}

/* stylelint-disable-next-line selector-class-pattern */
.app-select:deep(.v-input__control .v-field .v-field__outline::after) {
  /* stylelint-disable-next-line declaration-no-important */
  border-bottom-style: none !important;
}

/* stylelint-disable-next-line selector-class-pattern */
.app-list :deep(.v-list-item__append .v-icon) {
  /* stylelint-disable-next-line declaration-no-important */
  color: #468bbf !important;
}

/* stylelint-disable-next-line selector-class-pattern */
.v-btn--icon.v-btn--density-default {
  width: 24px;
  height: 24px;
}

/* stylelint-disable-next-line selector-class-pattern */
:deep(.v-toolbar__content) {
  /* stylelint-disable-next-line declaration-no-important */
  height: 40px !important;
}

/* stylelint-disable-next-line selector-class-pattern */
.app-header-bar {
  /* stylelint-disable-next-line selector-class-pattern */
  .v-btn--size-default {
    width: 72px;
  }
}

/* stylelint-disable-next-line selector-class-pattern */
:deep(.v-toolbar-title__placeholder) {
  /* stylelint-disable-next-line declaration-no-important */
  overflow: visible !important;
}
</style>
