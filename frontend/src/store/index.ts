import { createStore } from 'vuex';

export default createStore({
  state: {
    username: localStorage.getItem('username'),
    isAdmin: localStorage.getItem('isAdmin'),
  },
  mutations: {
    setUsername: (state, username) => {
      state.username = username;
    },
    setIsAdmin: (state, isAdmin) => {
      state.isAdmin = isAdmin;
    },
  },
  getters: {
    getUsername: (state) => state.username,
    getIsAdmin: (state) => state.isAdmin,
  },
  actions: {
    setUsername: ({ commit }, username) => {
      commit('setUsername', username);
    },
    setIsAdmin: ({ commit }, isAdmin) => {
      commit('setIsAdmin', isAdmin);
    },
  },
  modules: {
  },
});
