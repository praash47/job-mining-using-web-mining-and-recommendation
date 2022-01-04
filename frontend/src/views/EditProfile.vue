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
  <div class="left-container">
    <h1>Profile</h1>
    <form v-on:submit.prevent="updateUser">
    <div class="username">
      <i class="fa fa-user"></i>
      <input type="text" v-model="username"
      required="required" class="nusername">
    </div>
    <div class="email-id">
      <i class="fa fa-envelope"></i>
      <input type="email" required="required"
      v-model="email">
    </div>
    <div class="left-container-button">
      <button type="submit">Update</button>
    </div>
    </form>
  </div>
  <div class="right-container">
    <form v-on:submit.prevent="changePassword">
    <h1>Change Password</h1>
    <div class="old-password">
      <input type="password" required="required" v-model="password"
      placeholder="Enter old password">
    </div>

    <div class="new-password">
      <input type="password" required="required" v-model="new_password"
      minlength="8" placeholder="Enter new password">
    </div>

    <div class="update-password-button">
      <button type="submit">Update Password</button>
    </div>
    </form>
  </div>

  <div class="skills-container">
    <h1>My skills</h1>
    <div class="skills-to-be-added">
      <div class="search-box">
        <input class="search-txt" type="text" v-model="search_term"
         placeholder="Type to search...">
        <a class="search-btn" href="#">
            <i class="fa fa-search"></i>
        </a>
      </div>
      <ul class="skills" id="nonselected">
        <li class="skill" v-for="skill in skills_filtered" :key="skill">{{ skill }}
          <i class="fa fa-arrow-circle-right" @click="moveSelected(skill)"></i></li>
      </ul>
    </div>

    <div class="container container-2">
      <ul class="skills" id="selected">
        <li class="skill" v-for="skill in selected_skills" :key="skill">{{ skill }}
          <i class="fa fa-arrow-circle-left" @click="moveSelected(skill)"></i></li>
      </ul>
    </div>
    <div class="continue-button">
      <button @click="updateUser">Save</button>
    </div>
  </div>
</div>
</template>
<script lang="ts">
import { defineComponent } from 'vue';
import axios from 'axios';

export default defineComponent({
  name: 'EditProfile',
  props: ['message', 'rec-jobs'],
  emits: ['emit-snackbar'],
  computed: {
    skills_filtered() {
      return this.search_term
        ? this.skills.filter((skill) => skill.toLowerCase().includes(this.search_term))
        : this.skills;
    },
  },
  created() {
    this.username = this.$store.getters.getUsername;
    axios({
      method: 'POST',
      url: 'http://127.0.0.1:8000/register',
      data: {
        action: 'email_needed',
        username: this.username,
      },
    }).then((response) => {
      this.email = response.data.email;
    });
    this.fillSkills();
  },
  components: {
  },
  watch: {
    username() {
      const inputbox = document.querySelector<HTMLElement>('.nusername');
      if (this.rusername === '') {
        inputbox.style.backgroundColor = 'white';
        inputbox.style.color = 'black';
      } else {
        axios({
          method: 'POST',
          url: 'http://127.0.0.1:8000/register',
          data: {
            username: this.username,
            action: 'username_check',
          },
        }).then((response) => {
          if (response.data) {
            if (response.data.message === 'username exists!'
            && this.username !== localStorage.getItem('username')) {
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
    fillSkills() {
      axios({
        method: 'POST',
        url: 'http://127.0.0.1:8000/register',
        data: {
          username: this.username,
          action: 'skills_check',
        },
      }).then((response) => {
        const skills = response.data.skills.replaceAll('[', '').replaceAll(']', '')
          .replaceAll("'", '').replaceAll(', ', ',');
        this.selected_skills = skills.split(',');
        axios({
          method: 'POST',
          url: 'http://127.0.0.1:8000/skills',
        }).then((selresponse) => {
          this.skills = selresponse.data.skills.filter(
            (skill) => !this.selected_skills.includes(skill),
          );
        });
      });
    },
    moveSelected(skill) {
      if (this.skills.indexOf(skill) !== -1) {
        this.skills = this.skills.filter((arraySkill) => arraySkill !== skill);
        this.selected_skills.push(skill);
      } else if (this.selected_skills.indexOf(skill) !== -1) {
        this.selected_skills = this.selected_skills.filter((arraySkill) => arraySkill !== skill);
        this.skills.push(skill);
      }
    },
    updateUser() {
      const inputbox = document.querySelector<HTMLElement>('.nusername');
      if (!(inputbox.style.backgroundColor === 'red')
      && this.selected_skills.length > 0) {
        axios({
          method: 'POST',
          url: 'http://127.0.0.1:8000/register',
          data: {
            username: this.username,
            ousername: localStorage.getItem('username'),
            email: this.email,
            skills: this.selected_skills,
            action: 'update',
          },
        }).then((response) => {
          if (response.data.message === 'successfully updated!') {
            this.$store.dispatch('setUsername', response.data.user);
            localStorage.setItem('username', this.username);
            this.$emit('emit-snackbar', response.data.message);
            this.fillSkills();
          }
        });
      } else if (this.selected_skills.length === 0) {
        this.$emit('emit-snackbar', 'Please select at least one skill!');
      } else {
        this.$emit('emit-snackbar', 'Please correct the errors first!');
      }
    },
    changePassword() {
      axios({
        method: 'POST',
        url: 'http://127.0.0.1:8000/register',
        data: {
          username: this.username,
          password: this.password,
          new_password: this.new_password,
          action: 'change_password',
        },
      }).then((response) => {
        this.$emit('emit-snackbar', response.data.message);
        this.password = '';
        this.new_password = '';
      });
    },
  },
  data() {
    return {
      username: '',
      email: '',
      skills: [],
      search_term: '',
      selected_skills: [],
      password: '',
      new_password: '',
    };
  },
});
</script>
<style scoped>

@import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:ital,wght@0,200;0,300;0,400;0,600;0,700;0,900;1,200;1,300;1,400;1,600;1,700;1,900&display=swap');
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
    bottom: 0;
    z-index: 1;
    background: rgba(0,0,0);
    border-bottom: 1px solid rgba(0, 0, 0, 0.082);
    width: 100%;
}
.top ul {
    list-style-type: none;
    display: flex;
    justify-content: center;
}
.top ul li a {
    display: inline-block;
    margin: 20px;
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
.back-to-job-button a{
    z-index: 2;
    background-color: rgb(10, 4, 4);
    border: none;
    color: white;
    cursor: pointer;
    border-radius: 10px;
    padding: 15px 32px;
    text-align: center;
    display: inline-block;
    font-size: 16px;
    margin: 20px;
    box-shadow: inset 8px 8px 16px rgb(12, 12, 12),
    inset -8px -8px 16px rgb(12, 12, 12);
    position: relative;
}
.left-container{
    background: rgba(0,0,0,0.5);
    margin:18px 10px;
    padding:20px;
    height:220px;
    width:400px;

}

.left-container h1{
    color:white;
    margin-bottom: 10px;

}

.left-container .username{
    margin-bottom: 10px;
    color:white;
}

.left-container .username input{
    padding:10px;
    width:80%;
    font-size: 18px;
    border-radius: 15px;
}

.left-container .email-id{
    margin-bottom: 18px;
    color:white;
}
.left-container .email-id input{
    padding:10px;
    width:80%;
    font-size: 18px;
    border-radius: 15px;
}

.left-container .left-container-button button{
    background-color: rgb(13, 13, 71);
    color: white;
    border-radius: 15px;
    padding: 15px 32px;
    cursor: pointer;
    text-align: center;
    display: inline-block;
    font-size: 16px;
}

.right-container{
    background: rgba(0,0,0,0.5);
    position:absolute;
    top:20px;
    right:100px;
    width:500px;
    padding:15px;
    height:220px;
    color:white;
}

.right-container h1{
    margin-bottom: 10px;
}

.right-container .old-password input, .new-password input{
    padding:10px;
    margin-bottom: 10px;
    width:80%;
    font-size: 18px;
    border-radius: 15px;
}

.right-container .update-password-button button{
    background-color: rgb(13, 13, 71);
    color: white;
    border-radius: 15px;
    padding: 15px 32px;
    text-align: center;
    cursor:pointer;
    display: inline-block;
    font-size: 16px;
}

.skills-container{
    position:relative;
    background:rgba(0,0,0,0.5);
    color:black;
    height:600px;
    width:97%;
    margin:80px auto;
    padding:10px;
}

.skills-container h1{
    color:white;
}

.skills-container .search-box{
    position:absolute;
    top:3%;
    left:1%;
    height:20px;
    background:white;
    border-radius: 40px;
    padding:10px;
    width:500px;
}

.search-btn{
    color:#1a40bd;
    float:right;
    width:25px;
    height:25px;
    border-radius:50%;
    background:#2f3640;
    display:flex;
    justify-content: center;
    align-items:center;
}

.search-txt{
    border:none;
    outline:none;
    float:left;
    padding:0;
    color:black;
    font-size:16px;
    line-height:20px;
    width:450px;
}

.skills-to-be-added{
    width: 600px;
    height: 500px;
    position: relative;
}

ul {
    position: absolute;
    top: 15%;
    left: 1%;
    height: 400px;
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
}

.fa.fa-arrow-circle-right, .fa.fa-arrow-circle-left{
    float:right;
    cursor: pointer;
}

.container-2{
    width: 600px;
    height: 500px;
    position: absolute;
    top: 40px;
    left: 48%;
}

.continue-button{
    position: absolute;
    bottom:10px;
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
