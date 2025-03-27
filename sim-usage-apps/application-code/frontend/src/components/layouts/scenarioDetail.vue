<script setup lang="ts">
import { defineProps } from 'vue';
import { useI18n } from 'vue-i18n';

// tはlabelTextList、codesListのjsonファイルを使用
const { t } = useI18n({ useScope: 'global' });
defineProps({
  display: {
    type: Object,
    required: true,
  },
});

// v-chip表示用
function chipsRows(item) {
  const chipsRows = [];
  const chipLength = 3; // 三つのヒヤリハットおきに行替えする
  for (let i = 0; i < item.length; i += chipLength) {
    chipsRows.push(item.slice(i, i + chipLength));
  }

  return chipsRows;
}
</script>
<template>
  <div class="scenario-detail px-2 py-2 border-sm w-100">
    <div class="d-flex">
      <div class="title-pic">&nbsp;</div>
      <v-label class="ml-2 font-weight-bold">{{
        t('labelTextList.detailOfScenario')
      }}</v-label>
    </div>
    <div class="font-size-12 mt-4">
      {{ t('labelTextList.scenarioCreationDate')
      }}{{ display.scenarioCreateTime }}
    </div>
    <div class="font-size-12 mt-2">
      {{ t('labelTextList.area') }}{{ display.sectionName }}
    </div>
    <div class="font-size-12 mt-2">
      {{ t('labelTextList.location') }}{{ display.locationName }} 付近
    </div>
    <div class="font-size-12 mt-2">
      {{ t('labelTextList.locationOfOccurrenceDetails')
      }}{{ t('labelTextList.lat') }}
      {{ display.latitude }}
    </div>
    <div class="font-size-12 mt-2">
      {{ t('labelTextList.lon') }}
      {{ display.longitude }}
    </div>
    <div class="d-flex mt-4">
      <div class="font-size-12 mt-2">
        {{ t('labelTextList.nearMissType') }}
      </div>
      <div>
        <div
          v-for="(row, index) in display.nearmissTypeList === undefined ||
          display.nearmissTypeList === null
            ? null
            : chipsRows(display.nearmissTypeList)"
          :key="index"
        >
          <div class="d-flex flex-wrap">
            <div>
              <v-chip
                label=""
                class="ml-1 mt-1 font-size-12"
                size="small"
                v-for="(row1, index1) in row"
                :key="index1"
                >{{ t(`codesList.${row1.nearmissType}`) }}</v-chip
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<style lang="scss" scoped>
.scenario-detail {
  border-radius: 5px;
}

.title-pic {
  width: 5px;
  background-color: #1760a5;
}

.font-size-12 {
  font-size: 12px;
}
</style>
