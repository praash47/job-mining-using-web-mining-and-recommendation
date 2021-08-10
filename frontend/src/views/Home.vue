<template>
  <div class="home">
    <div class="button-container">
      <!-- the BEAUTIFUL BUTTON -->
      <button class="button" @click="scrape">
        Scrape &forall;
      </button>
    </div>
    <div class="data">
      <DataContainer v-for="data in datas" :type="container_type"
      :key="data.id" />
    </div>
    <Loading />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import DataContainer from '@/components/DataContainer.vue';
import Loading from '@/components/Loading.vue';

export default defineComponent({
  name: 'Home',
  components: {
    DataContainer,
    Loading,
  },
  methods: {
    scrape() {
      // Show the scraping loading component
      const loading = document.querySelector<HTMLElement>('.loading');
      loading.style.visibility = 'visible';
      
      this.ws.send('hello');
      
      this.ws.onmessage = (message) => {
        console.log(message);
      };
      this.ws.onclose = () => {
        console.error('Chat socket closed unexpectedly!');
      };
    },
  },
  data() {
    return {
      container_type: '',
      datas: [],
      ws: new WebSocket('wss://echo.websocket.org/'),
    };
  },
});
</script>

<style lang="sass">
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300&display=swap');

.home
  display: flex
  flex-direction: column
  justify-content: center
  font-family: 'Roboto', sans-serif;

  .button-container
    display: flex
    justify-content: center
    margin-bottom: 20px
  .button
    position: relative
    display: inline-block
    padding: 10px 30px
    letter-spacing: 2px
    font-size: 1.25em
    background: #262c37
    color: rgba(255, 255, 255, .5)
    cursor: pointer
    transition: .5s

    &:hover
      color: rgba(255, 255, 255, 1)

</style>
