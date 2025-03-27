<script setup lang="ts">
import AppHeader from '@/components/globals/AppHeader.vue';
</script>

<template>
  <v-app id="app" data-test="mainLayout">
    <AppHeader />
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>
