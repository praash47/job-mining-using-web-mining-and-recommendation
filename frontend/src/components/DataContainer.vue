<template>
    <div>
      <div v-if="data.type=='msg'" class="message">
        {{ data.message }}
      </div>
      <div v-if="data.type == 'title_content'" class="title-content">
        <div class="title">
          {{ data.title }}
        </div>
        <div class="content">
          <p v-for="value in data.content" :key="value">
            <span v-if="value.dict">
              {{ value.dict.key }} :
              {{ value.dict.value }}
            </span>
            <span v-else>
              {{ value }}
            </span>
          </p>
        </div>
      </div>
    </div>
</template>
<script>
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'DataContainer',
  props: [
    'data',
  ],
});
</script>
<style lang="sass">
@mixin randombgr
  background: rgb(random(255), random(255), random(255))

.message, .title-content
  background: #4CBB17
  display: flex
  justify-content: center
  padding: 50px
  font-size: 1.5em
  color: #F1F1F1
  margin: 10px 0
  box-shadow: inset 0 0 10px rgba(0, 0, 0, .6)
  text-shadow: 2px 2px 2px green
  transition: .5s
.title-content
  background: #1F75FE
  flex-direction: column

  .title
    background: rgba( 255, 255, 255, 0.15 )
    box-shadow: 0 8px 32px 0 rgba( 31, 38, 135, 0.37 )
    backdrop-filter: blur( 6.5px )
    -webkit-backdrop-filter: blur( 6.5px )
    border-radius: 10px
    border: 1px solid rgba( 255, 255, 255, 0.18 )
    display: flex
    justify-content: center
    padding: 6px

  .content
    display: flex
    flex-wrap: wrap
    margin: 10px

    p
      justify-content: space-between
      font-size: 0.45em
      padding: 10px
      margin: 5px

      @for $i from 0 through 500
        &:nth-child(#{$i})
          @include randombgr
</style>
