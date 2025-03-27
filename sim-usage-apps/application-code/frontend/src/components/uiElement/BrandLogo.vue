<script setup lang="ts">
import { ref } from 'vue';
const logo = ref(import.meta.env.VITE_CONTENT_PATH + 'top_logo.png');
// emits
interface Emits {
  (event: 'click', modelValue: MouseEvent): void;
}
const emit = defineEmits<Emits>();
</script>

<template>
  <v-btn
    color="on-primary"
    @click="(event: MouseEvent) => emit('click', event)"
  >
    <v-img
      :src="logo"
      alt="logo"
      style="height: 36px; width: 400px; margin-left: 24px"
    ></v-img>
  </v-btn>
</template>

<style scoped lang="scss">
.logo {
  cursor: pointer;
}
</style>
