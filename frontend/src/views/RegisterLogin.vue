<template>
  <div class="body">
    <Register @emit-snackbar="emitSnackbar" :message="message" />
    <Login @emit-snackbar="emitSnackbar" :message="message" />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import Register from '../components/Register.vue';
import Login from '../components/Login.vue';

export default defineComponent({
  name: 'RegisterLogin',
  emits: ['emit-snackbar'],
  props: ['message'],
  components: {
    Register,
    Login,
  },
  methods: {
    emitSnackbar(message) { this.$emit('emit-snackbar', message); },
  },
});
</script>

<style lang="css" scoped>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:ital,wght@0,200;0,300;0,400;0,600;0,700;0,900;1,200;1,300;1,400;1,600;1,700;1,900&display=swap');
* {
    margin:0;
    padding:0;
    font-family: 'Source Sans Pro', sans-serif;
}

.body{
    background: url(../assets/bg.jpg) no-repeat center center fixed;
    background-size:cover;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
}

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
