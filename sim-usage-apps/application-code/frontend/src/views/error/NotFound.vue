<script setup lang="ts">
import { useI18n } from 'vue-i18n';

// tはlabelTextList、codesListのjsonファイルを使用
const { t } = useI18n({ useScope: 'global' });
</script>
<template>
  <v-container>
    <v-row class="mt-4">
      <v-col class="d-flex align-center justify-center">
        <h1 class="text-h2 text-primary">
          {{ t('labelTextList.notFound') }}
        </h1>
      </v-col>
    </v-row>
  </v-container>
</template>
