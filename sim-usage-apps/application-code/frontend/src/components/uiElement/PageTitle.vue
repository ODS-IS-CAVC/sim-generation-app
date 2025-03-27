<script setup lang="ts">
// props
export interface Props {
  title: string | undefined;
}
const props = withDefaults(defineProps<Props>(), {
  title: '',
});
</script>

<template>
  <v-container>
    <v-row>
      <v-col class="d-flex align-center">
        <slot name="title">
          <h1 class="text-h4 font-weight-bold" data-test="pageTitle">
            {{ props.title }}
          </h1>
        </slot>
      </v-col>
    </v-row>
  </v-container>
</template>
