<template>
<form v-on:submit.prevent="registerUser">
    <div class="container-register">
        <h1>Register</h1>
          <div class="box-1">
              <i class="fa fa-user"></i>
              <input type="username" name="username" v-model="username"
              placeholder="Enter your username" class="username" required="required"
              minlength="3">
          </div>
          <div class="box-1">
              <i class="fa fa-envelope"></i>
              <input type="email" name="email" v-model="email"
              placeholder="Enter your email" required="required">
          </div>
          <div class="box-1">
              <i class="fa fa-key"></i>
              <input type="password" name="password" v-model="password"
              placeholder="Enter your password" required="required" minlength="8">
          </div>
          <button class="btn" type="submit">Register</button>
    </div>
    </form>
</template>
<script lang="ts">
import axios from 'axios';
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Register',
  props: ['message'],
  emits: ['emit-snackbar'],
  components: {
  },
  watch: {
    username() {
      const inputbox = document.querySelector<HTMLElement>('.username');
      if (this.rusername === '') {
        inputbox.style.backgroundColor = 'white';
        inputbox.style.color = 'black';
      } else {
        axios({
          method: 'POST',
          url: 'http://localhost:8000/register',
          headers: { 'X-CSRFToken': this.csrftoken },
          data: {
            csrfmiddlewaretoken: this.csrftoken,
            username: this.username,
            action: 'username_check',
          },
        }).then((response) => {
          if (response.data) {
            if (response.data.message === 'username exists!') {
              inputbox.style.backgroundColor = 'red';
              inputbox.title = response.data.message;
              inputbox.style.color = 'white';
              this.$emit('emit-snackbar', response.data.message);
            } else {
              inputbox.style.backgroundColor = 'green';
              inputbox.style.color = 'white';
            }
          }
        });
      }
    },
  },
  methods: {
    registerUser() {
      const inputbox = document.querySelector<HTMLElement>('.username');
      if (!(inputbox.style.backgroundColor === 'red')) {
        axios({
          method: 'POST',
          url: 'http://localhost:8000/register',
          data: {
            username: this.username,
            email: this.email,
            password: this.password,
            action: '',
          },
        }).then((response) => {
          if (response.data.message === 'successfully registered!') {
            this.$store.dispatch('setUsername', response.data.user);
            localStorage.setItem('username', this.username);
            this.$store.dispatch('setIsAdmin', response.data.isAdmin);
            localStorage.setItem('isAdmin', response.data.isAdmin);
            this.$router.push('skills');
          }
        });
      } else {
        this.$emit('emit-snackbar', 'Please correct the errors first!');
      }
    },
  },
  data() {
    return {
      username: '',
      email: '',
      password: '',
    };
  },
});
</script>
<style scoped>
.container-register, .container-login {
    background: rgba(0, 0, 0, .5);
    padding: 10px;
}

.container-register{
    /* border:12px solid black; */
    color:white;
    position:absolute;
    top:20%;
    left:10%;
    width:393px;
}

.container-register h1{
    font-size:40px;
    border-bottom: 2px solid white;
    margin-bottom: 43px;
    padding:13px 0;
}

.box-1{
    width:100%;
    /* border:2px solid purple; */
}

.box-1 input{
    width:75%;
    margin:13px 0px;
    padding:10px 10px;
    font-size:15px;
    border:none;
    border-radius: 10px;
    outline:none;
}

.box-1 i{
    width:25px;
    text-align:center;
}

.btn{
    cursor:pointer;
    outline:none;
    width:25%;
    margin:12px 0;
    padding:6px;
    /* border:2px solid purple; */
    border-radius:10px;
}
</style>
