<template>
<div>
  <div class="container container-1">
  <h1>Choose your skills to continue</h1>
    <div class="search-box">
        <input class="search-txt" type="text" v-model="search_term"
        placeholder="Type to search...">
        <a class="search-btn" href="#">
            <i class="fa fa-search"></i>
        </a>
    </div>
    <Loading v-if="loading"/>
    <ul class="skills"
        id="nonselected"
        @drop.prevent="moveSelected($event)"
        @dragover.prevent
        v-else>
      <li class="skill"
          title="You can drag this to another box"
          v-for="skill in skills_filtered"
          :key="skill"
          draggable="true"
          @dragstart="$event.dataTransfer.setData('skill', skill)">
        {{ skill }}
        <i class="fa fa-arrow-circle-right" @click="moveSelected(skill)"></i></li>
    </ul>
  </div>
  <div class="container container-2">
  <h2>Selected skills</h2>
    <ul class="skills"
        id="selected"
        @drop.prevent="moveSelected($event)"
        @dragover.prevent>
      <li class="skill"
          title="You can drag this to another box"
          v-for="skill in selected_skills"
          :key="skill"
          draggable="true"
          @dragstart="$event.dataTransfer.setData('skill', skill)">
        {{ skill }}
        <i class="fa fa-arrow-circle-left" @click="moveSelected(skill)"></i></li>
    </ul>
  </div>
  <div class="continue-button">
      <button @click="saveSkills">Continue</button>
  </div>
</div>
</template>
<script lang="ts">
import axios from 'axios';
import { defineComponent } from 'vue';
import Loading from '../components/Loading.vue';

export default defineComponent({
  name: 'Skills',
  components: {
    Loading,
  },
  props: ['message'],
  emits: ['emit-snackbar'],
  created() {
    axios({
      method: 'POST',
      url: 'http://192.168.1.82:8000/skills',
    }).then((response) => {
      this.loading = false;
      this.skills = response.data.skills;
    });
  },
  computed: {
    skills_filtered() {
      return this.search_term
        ? this.skills.filter((skill) => skill.toLowerCase().includes(this.search_term))
        : this.skills;
    },
  },
  methods: {
    moveSelected(skill) {
      let toMove;
      if (skill.target) {
        toMove = skill.dataTransfer.getData('skill');
      } else {
        toMove = skill;
      }
      if (this.skills.indexOf(toMove) !== -1) {
        this.skills = this.skills.filter((arraySkill) => arraySkill !== toMove);
        this.selected_skills.push(toMove);
        setTimeout(() => {
          document.querySelector('#selected').scrollTop = document.querySelector('#selected').scrollHeight;
        }, 1);
      } else if (this.selected_skills.indexOf(toMove) !== -1) {
        this.selected_skills = this.selected_skills.filter((arraySkill) => arraySkill !== toMove);
        this.skills.push(toMove);
      }
    },
    saveSkills() {
      if (!this.selected_skills.length) {
        this.$emit('emit-snackbar', 'Please select at least a skill to continue');
      } else {
        axios({
          method: 'POST',
          url: 'http://192.168.1.82:8000/register',
          data: {
            username: this.$store.getters.getUsername,
            skills: this.selected_skills,
            action: 'skills_insert',
          },
        }).then((response) => {
          if (response.data.message === 'successfully inserted!') {
            this.$router.push('/recommend');
          }
        });
      }
    },
  },
  data() {
    return {
      username: '',
      password: '',
      skills: [],
      selected_skills: [],
      search_term: '',
      loading: true,
    };
  },
});
</script>
<style>
body{
    background: url(../assets/bg.jpg) no-repeat center center fixed;
    background-size: cover;
    box-sizing: border-box;
    overflow: none;
}
</style>
<style scoped>
*{
    margin:0;
    padding:0;
    font-family: 'Source Sans Pro', sans-serif;
}

h1{
    font-size:46px;
    padding:10px;
    color:white;
}

.container{
    width: 600px;
    height: 500px;
    position: relative;
}
.search-box{
    position:absolute;
    top:25%;
    left:1%;
    /* transform:translate(-50%,-50%); */
    height:40px;
    background:white;
    border-radius: 40px;
    padding:10px;
}

.search-box:hover > .search-txt{
     width:500px;
     padding:0 6px;

}

.search-box:hover > .search-btn{
    background:white;

}

.search-btn{
    color:#e84118;
    float:right;
    width:40px;
    height:40px;
    border-radius:50%;
    background:#2f3640;
    display:flex;
    justify-content: center;
    align-items:center;
    transition:0.4s;

}

.search-txt{
    border:none;
    background:none;
    outline:none;
    float:left;
    padding:0;
    color:black;
    font-size:16px;
    transition:0.4s;
    line-height:40px;
    width:240px;
}

ul {
    position: absolute;
    top: 40%;
    left: 1%;
    height: 290px;
    overflow-y: auto;
    width: calc(100% - 1.15%);
}

.skill {
    width: 100%;
    background: white;
    border-bottom: 2px solid gray;
    padding: 10px;
    font-size: 20px;
    box-sizing: border-box;
    border-radius: 10px;
    margin-bottom: 2px;
    animation: fadein 0.5s;
    cursor: move;
}

@keyframes fadein {
    from { opacity: 0; }
    to   { opacity: 1; }
}

.fa.fa-arrow-circle-right, .fa.fa-arrow-circle-left{
    float:right;
    cursor: pointer;
}

h2{
    /* display:inline; */
    font-size:46px;
    bottom: 0px;
    color:white;
    position: absolute;
    left: 0;
    top: 2.9%;
}
.container-1{
    position: absolute;
    left: 1%;
}

.container-2{
    position: absolute;
    top: 0;
    left: 50%;
}

.continue-button{
    position: absolute;
    top: 550px;
    left: 15px;
}

.continue-button button{
    background-color: cadetblue;
    bottom:45px;
    color: white;
    padding: 15px 32px;
    border-radius: 15px;
    text-align: center;
    font-size: 16px;
}
</style>
