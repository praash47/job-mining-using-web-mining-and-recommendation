import { createStore } from 'vuex';

export default createStore({
  state: {
    username: localStorage.getItem('username'),
  },
  mutations: {
    setUsername: (state, username) => {
      state.username = username;
    },
  },
  getters: {
    getUsername: (state) => state.username,
  },
  actions: {
    setUsername: ({ commit }, username) => {
      commit('setUsername', username);
    },
  },
  modules: {
  },
});
