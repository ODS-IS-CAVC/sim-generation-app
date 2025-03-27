import { defineStore } from 'pinia';
import type { GridSearch } from '@/stores/search/search.model';
import type { PageControl } from '@/stores/search/search.model';

export const useSearchStore = defineStore({
  id: 'search',
  state: () => ({
    search: {
      happenTime: '',
      nearmissType: [],
    } as GridSearch,
    pageControl: {
      page: 1,
    } as PageControl,
    selectSectionRow: null,
    selectLocationRow: {
      locationId: '',
      locationName: '',
    } as selectLocationRow,
  }),
  persist: {
    key: 'SEARCH',
    storage: sessionStorage,
  },
  actions: {
    // その他条件の設定
    setSearch(search: GridSearch) {
      this.search = search;
    },
    // 選択したpageの設定
    setPage(page: number) {
      this.pageControl.page = page;
    },
    // 選択したpageの設定
    setPageControl(pageControl: PageControl) {
      this.pageControl = pageControl;
    },
    // 選択した区間の設定
    setSelectSectionRow(selectSectionRow: selectSectionRow) {
      this.selectSectionRow = selectSectionRow;
    },
    // 選択した場所の設定
    setSelectLocationRow(selectLocationRow: selectLocationRow) {
      this.selectLocationRow = selectLocationRow;
    },
    // 選択したヒヤリハット種別の設定
    setNearmissType(nearmissType: Array<string>) {
      this.search.nearmissType = nearmissType;
    },

    /**
     * 選択した場所をクリアする
     */
    clearSelectLocationRow() {
      const selectLocationRow = {
        locationId: '',
        locationName: '',
      };
      this.setSelectLocationRow(selectLocationRow);
    },
  },
  getters: {
    getSearch(state) {
      return state.search;
    },
    getPageControl(state) {
      return state.pageControl;
    },
    getPage(state) {
      return state.pageControl.page;
    },
    getSelectSectionRow(state) {
      return state.selectSectionRow;
    },
    getSelectLocationRow(state) {
      return state.selectLocationRow;
    },
    getSelectSectionId(state) {
      return state.selectSectionRow.sectionId;
    },
  },
});
