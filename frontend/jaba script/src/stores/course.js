import { defineStore } from 'pinia';

export const useCourseStore = defineStore('course', {
  state: () => ({
    refreshTrigger: 0,
  }),
  
  actions: {
    triggerRefresh() {
      this.refreshTrigger++;
    },
  },
}); 