import { defineStore } from 'pinia';

export const listSearch = defineStore({
  id: 'listSearch',
  actions: {
    listeners: {},
    on(event, callback) {
      if (!this.listeners[event]) {
        this.listeners[event] = [];
      }
      this.listeners[event].push(callback);
    },
    emit(event, ...args) {
      if (this.listeners[event]) {
        this.listeners[event].forEach((callback) => callback(...args));
      }
    },
  },
});
