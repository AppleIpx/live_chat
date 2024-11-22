import { createStore } from 'vuex';

const store = createStore({
  state: {
    newMessageCount: 0,
    latestMessage: null,
  },
  mutations: {
    incrementNewMessage(state) {
      state.newMessageCount++;
    },
    resetNewMessageCount(state) {
      state.newMessageCount = 0;
    },
    setLatestMessage(state, message) {
      state.latestMessage = message;
    },
  },
  actions: {
    incrementNewMessage({ commit }) {
      commit('incrementNewMessage');
    },
    resetNewMessageCount({ commit }) {
      commit('resetNewMessageCount');
    },
    receiveMessage({ commit, dispatch }, message) {
      dispatch('incrementNewMessage');
      commit('setLatestMessage', message);
    },
  },
  getters: {
    newMessageCount: (state) => state.newMessageCount,
    latestMessage: (state) => state.latestMessage,
  },
});

export default store;
