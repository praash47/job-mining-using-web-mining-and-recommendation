<template>
    <div class="loading">
      <img src="@/assets/loading.gif" alt="Loading Image">
      <p>Scraping ...</p>
    </div>
</template>
<script>
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Loading',
});
</script>
<style lang="sass">
.loading
  display: flex
  visibility: hidden
  justify-content: center
img
  width: 50px
p
  display: flex
  justify-content: center
  align-items: center
  font-weight: bold
</style>
