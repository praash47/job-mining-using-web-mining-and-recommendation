<template>
<form v-on:submit.prevent="loginUser">
    <div class="container-login">
        <h1>Login</h1>
        <div class="box-2">
            <i class="fa fa-user"></i>
            <input type="username" required="required" v-model="username"
            placeholder="Enter your username">
        </div>
        <div class="box-2">
            <i class="fa fa-key"></i>
            <input type="password" required="required" v-model="password"
            placeholder="Enter your password">
        </div>
        <button class="btn" type="submit">Login</button>
    </div>
</form>
</template>
<script lang="ts">
import axios from 'axios';
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Login',
  props: ['message'],
  emits: ['emit-snackbar'],
  components: {
  },
  mounted() {
    if (this.$store.getters.getUsername) {
      this.checkSkillsAdded();
    }
  },
  watch: {
  },
  methods: {
    loginUser() {
      if (!this.message.length) {
        axios({
          method: 'POST',
          url: 'http://127.0.0.1:8000/login',
          data: {
            username: this.username,
            password: this.password,
          },
        }).then((response) => {
          if (response.data.message === 'username or password doesn\'t match!') {
            this.$emit('emit-snackbar', response.data.message);
          } else {
            this.$store.dispatch('setUsername', this.username);
            localStorage.setItem('username', this.username);
            this.checkSkillsAdded();
          }
        });
      }
    },
    checkSkillsAdded() {
      axios({
        method: 'POST',
        url: 'http://127.0.0.1:8000/register',
        data: {
          username: this.$store.getters.getUsername,
          action: 'skills_check',
        },
      }).then((response) => {
        if (response.data.skills.length > 2) {
          this.$router.push('/recommend');
        } else {
          this.$router.push('/skills');
        }
      });
    },
  },
  data() {
    return {
      username: '',
      password: '',
    };
  },
});
</script>
<style scoped>
.btn{
    cursor:pointer;
    outline:none;
    width:25%;
    margin:12px 0;
    padding:6px;
    /* border:2px solid purple; */
    border-radius:10px;
}
.container-register, .container-login {
    background: rgba(0, 0, 0, .5);
    padding: 10px;
}
.container-login{
    /* border:12px solid black; */
    color:white;
    position:absolute;
    top:20%;
    right:10%;
    width:393px;
}

.container-login h1{
    font-size:40px;
    border-bottom: 2px solid white;
    margin-bottom: 43px;
    padding:13px 0;
}

.box-2{
    width:100%;
}

.box-2 input{
    width:75%;
    margin:13px 0px;
    padding:10px 10px;
    font-size:15px;
    border:none;
    border-radius: 10px;
    outline:none;
}
.box-2 i{
    /* padding:0 0px; */
    width:25px;
    text-align:center;
}
</style>
