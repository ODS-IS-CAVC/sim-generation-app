import { defineStore } from 'pinia';

export const useRoutingStore = defineStore({
  id: 'ROUTING',
  state: () => ({
    redirectFrom: null as null | string,
    uuid: null as null | string,
  }),
  persist: {
    key: 'ROUTING',
    storage: sessionStorage,
  },
  actions: {
    setRedirectFrom(from: string) {
      this.redirectFrom = from;
    },
    setUuid(uuid: string) {
      this.uuid = uuid;
    },
  },
});
