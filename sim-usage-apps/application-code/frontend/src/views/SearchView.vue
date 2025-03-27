<script setup lang="ts">
import searchCondition from '@/components/layouts/searchCondition.vue';
import searchResult from '@/components/layouts/searchResult.vue';
</script>

<template>
  <div class="d-flex">
    <div class="search-condition">
      <searchCondition></searchCondition>
    </div>
    <div class="search-list mt-5 ml-6 mr-6">
      <searchResult></searchResult>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.search-condition {
  width: 20%;
}

.search-list {
  width: 80%;
}
</style>
