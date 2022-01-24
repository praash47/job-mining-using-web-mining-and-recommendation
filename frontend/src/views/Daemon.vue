<template>
  <div>
    <div class="top">
      <div class="back-to-job-button">
        <router-link to="/recommend"><i class="fa fa-arrow-left"></i></router-link>
      </div>
      <nav>
        <ul>
          <li>
            <router-link to="/editprofile">
              <i class="fas fa-pencil-alt"></i> Edit Profile / Skills
            </router-link>
          </li>
          <li>
            <router-link to="/daemon"><i class="fas fa-coins"></i> Backend Daemon</router-link>
          </li>
        </ul>
      </nav>
    </div>
    <div :class="'container-1 ' + message_priority">
        <span class="text">
            {{ current_message }}
        </span>
    </div>

    <div class="container-2">
        <span :class="'message ' + message.priority" v-for="message in messages"
        :key="message">
          {{ message.timestamp }} {{ message.message }}
        </span>
    </div>
  </div>
</template>
<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Daemon',
  computed: {
  },
  created() {
    this.setIdle();
    const es = new EventSource('http://192.168.133.141:8000/events/');
    es.onmessage = (e) => {
      const data = JSON.parse(e.data);
      this.current_message = data.currentMessage;
      this.message_priority = data.messagePriority;
      const currentdate = new Date();
      const timestamp = `${currentdate.getFullYear()}-
        ${currentdate.getMonth() + 1}-
        ${currentdate.getDate()} @ 
        ${currentdate.getHours()}:
        ${currentdate.getMinutes()}:
        ${currentdate.getSeconds()}`;
      this.messages.unshift({
        message: this.current_message,
        priority: this.message_priority,
        timestamp,
      });
      setTimeout(this.setIdle, 5000);
    };
  },
  components: {
  },
  watch: {
  },
  methods: {
    setIdle() {
      this.current_message = 'Idle';
      this.message_priority = 'idle';
    },
  },
  data() {
    return {
      current_message: 'Idle',
      message_priority: 'idle',
      messages: [],
    };
  },
});
</script>
<style scoped>
*{
    margin:0;
    padding:0;
    font-family: 'Source Sans Pro', sans-serif;
}
body{
    background: url(../assets/bg.jpg) no-repeat center center fixed;
    background-size:cover;
}
.top {
    justify-content: space-between;
    position: fixed;
    top: 0;
    z-index: 1;
    background: rgba(0,0,0);
    border-bottom: 1px solid rgba(0, 0, 0, 0.082);
    width: 100%;
    display: flex;
}
.top ul {
    list-style-type: none;
    display: flex;
    justify-content: center;
}
.top ul li a {
    display: inline-block;
    margin:  10px;
    background: #c44910;
    box-shadow: inset 5px 5px 4px #b2420f,
            inset -5px -5px 4px #d65011;
    color: white;
    padding: 10px;
    cursor: pointer;
    border-radius: 10px;
    text-shadow: -1px -1px 0 rgb(36, 19, 19), 1px -1px 0 rgb(17, 9, 9),
    -1px 1px 0 rgb(17, 10, 10), 1px 1px 0 rgb(14, 5, 5);
    text-decoration: none;
}
.top ul li:nth-child(2) a {
    display: inline-block;
    background: #001fac;
    box-shadow: inset 5px 5px 10px #001a8f,
            inset -5px -5px 10px #0024c9;
    color: white;
    padding: 10px;
    text-decoration: none;
}
.back-to-job-button {
  display: inline;
}
.back-to-job-button a{
    z-index: 2;
    background-color: rgb(10, 4, 4);
    border: none;
    color: white;
    cursor: pointer;
    border-radius: 10px;
    padding: 15px 32px;
    text-align: center;
    font-size: 16px;
    display: inline-block;
    box-shadow: inset 8px 8px 16px rgb(12, 12, 12),
    inset -8px -8px 16px rgb(12, 12, 12);
    position: relative;
    margin: 10px;
}

.container-1{
    color:white;
    position:absolute;
    width:500px;
    top:70px;
    height:250px;
    left:50%;
    transform: translateX(-50%);
    margin:20px 0;
    font-size:30px;
    padding: 20px;
    text-align: center;
    display: flex;
    justify-content: center;
    align-items: center;
}
.container-2{
    background:rgba(0,0,0,0.9);
    color:white;
    position:absolute;
    margin:10px;
    padding:10px;
    bottom:-10px;
    width:97%;
    height:200px;
    overflow-y:auto;
}
.container-1.scraping {
  background:rgb(2, 32, 2);
}
.container-1.info {
  background: rgb(3, 3, 49);
}
.container-1.idle {
  background: gray;
  color: #000;
}
.container-1.error {
  background: rgb(97, 13, 13);
}
.container-2 .message{
    display:block;
}
.message.scraping{
    color:green;
}
.message.info{
    color:rgb(2, 2, 255);
}
.message.error{
    color:red;
}
.text {
    font-size: 50px;
}
</style>
