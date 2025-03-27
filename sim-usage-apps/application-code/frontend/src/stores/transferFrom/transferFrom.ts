import { defineStore } from 'pinia';

export const useTransferFromScenarioInfoStore = defineStore({
  id: 'transferFromScenarioInfo',
  state: () => ({
    transferFromScenarioInfo: false,
  }),
  persist: {
    key: 'TRANSFER_FROM_SCENARIO_INFO',
    storage: sessionStorage,
  },
  actions: {
    async clear() {
      this.transferFromScenarioInfo = false;
    },

    // 詳細画面から遷移する
    async setTransferFromScenarioInfo() {
      this.transferFromScenarioInfo = true;
    },
  },
  getters: {
    isTransferFromScenarioInfo(state) {
      return state.transferFromScenarioInfo;
    },
  },
});
