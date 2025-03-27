import { defineStore } from 'pinia';

export const useItemsPerPageStore = defineStore({
  id: 'itemsPerPage',
  state: () => ({
    itemsPerPageControl: {
      itemsPerPage: 10,
    } as itemsPerPageControl,
  }),

  persist: true,
  actions: {
    setItemsPerPageControl(itemsPerPageControl: itemsPerPageControl) {
      this.itemsPerPageControl = itemsPerPageControl;
    },
    setItemsPerPage(itemsPerPage: number) {
      this.itemsPerPageControl.itemsPerPage = itemsPerPage;
    },
  },
  getters: {
    getItemsPerPage(state) {
      return state.itemsPerPageControl.itemsPerPage;
    },
    getItemsPerPageControl(state) {
      return state.itemsPerPageControl;
    },
  },
});
