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
          <li v-if="isAdmin">
            <router-link to="/logs"><i class="fas fa-scroll"></i> Logs</router-link>
          </li>
        </ul>
      </nav>
    </div>
    <div class="container-1">
        <select class="log-option" @change="changeSource">
            <option value="log_main">log_main</option>
            <option value="log_requestinggoogle">log_requestinggoogle</option>
            <option value="log_checkjobs">log_checkjobs</option>
            <option value="log_interactor">log_interactor</option>
            <option value="log_jobdetailsextractor">log_jobdetailsextractor</option>
        </select>
        <button class="clear" @click="clearLog">
            Clear Log
        </button>
        <button class="clear-all" @click="clearAll">
            Clear All Logs
        </button>
    </div>
    <Loading v-if='loading'/>
    <div class="container-2" v-else>
        <span :class="'message ' + message.priority" v-for="message in messages"
        :key="message">
          {{ message.timestamp }} {{ message.message }}
        </span>
    </div>
  </div>
</template>
<script lang="ts">
import { defineComponent } from 'vue';
import axios from 'axios';
import Loading from '../components/Loading.vue';

export default defineComponent({
  name: 'Log',
  computed: {
  },
  created() {
    this.isAdmin = this.$store.getters.getUsername;
    if (!this.isAdmin) this.$router.push('/recommend');
    this.requestLog();
  },
  components: {
    Loading,
  },
  watch: {
  },
  methods: {
    clearLog() {
      this.clear = true;
      this.requestLog();
    },
    clearAll() {
      this.clear = 'all';
      this.requestLog();
    },
    changeSource(e) {
      this.source = e.srcElement.value;
      this.requestLog();
    },
    requestLog() {
      this.loading = true;
      this.messages = [];
      axios({
        url: `https://job-mining.herokuapp.com:8000/logs/${this.source}/`,
        method: 'POST',
        data: {
          clear: this.clear,
        },
      })
        .then((response) => {
          if (response.data) {
            const messages = response.data.contents.split('\n');
            const logContents = [];
            messages.forEach((message) => {
              let priority = 'info';
              if (message.includes('ERROR')) priority = 'error';
              logContents.push({
                message,
                priority,
                timestamp: '',
              });
            });
            this.messages = logContents;
          } else {
            this.messages = [];
          }
          this.loading = false;
          this.clear = false;
        });
      this.eventSource = new EventSource(`https://job-mining.herokuapp.com:8000/events/${this.source}/`);
      this.eventSource.onmessage = (e) => {
        const data = JSON.parse(e.data);
        this.current_message = data.message;
        this.message_priority = data.type;
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
      };
    },
  },
  data() {
    return {
      messages: [],
      isAdmin: '',
      source: 'log_main',
      clear: false,
      eventSource: '',
      loading: true,
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
.top ul li:nth-child(3) a {
    display: inline-block;
    background: #598000;
    box-shadow: inset 5px 5px 10px #598000,
            inset -5px -5px 10px #2b5701;
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
.container-1 {
    position: absolute;
    top: 120px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 10px;
}
select {
    font-size: 20px;
    padding: 10px;
}
.clear, .clear-all {
    background: rgb(141, 96, 103);
    border: none;
    padding: 15px 10px;
    color: white;
    cursor: pointer;
}
.clear-all {
    background-color: maroon;
}

.container-2{
    background:rgba(0,0,0,0.9);
    color:white;
    position:absolute;
    margin:10px;
    padding:10px;
    width:97%;
    height:400px;
    overflow-y:auto;
    top: 200px;
}
.container-2 .message{
    display:block;
}
.container-2 .info{
    color:gray;
}
.container-2 .error{
    color:rgb(143, 22, 22);
}
.text {
    font-size: 50px;
}
.container {
  position: absolute;
  top: 200px;
  height:400px;
}
</style>
