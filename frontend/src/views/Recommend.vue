<template>
<div>
  <h1 class="my-skill">My skills</h1>
  <router-link to="/editprofile" class="right-nav username">
  <i class="fas fa-user"></i> {{ username }} <i class="fas fa-caret-down"></i>
  </router-link>
  <button class="logout" @click="logOut">Logout</button>
  <router-link to="/daemon" class="right-nav" style="background: #0e1030;
  font-weight: 400; color: #ddd;">
  <i class="fas fa-coins"></i> Backend Daemon
  </router-link>
  <div class="container-1">
    <div class="skills" >
      <span class="skill" v-for="skill in added_skills" :key="skill">{{ skill }}
        <i class="fa fa-times" @click="removeSkill(skill)"></i>
      </span>
    </div>
    <span class="confirmation">
      <button disabled="disabled" id="confirm" @click="saveSkills">
        Confirm Saving New Skills
      </button>
    </span>
  </div>

  <div class="left">
    <h2>Add Skills</h2>
    <div class="add-skills">
      <div class="skills-inner">
        <span class="skill" v-for="skill in all_skills_filtered" :key="skill">{{ skill }}
          <i class="fa fa-plus" @click="addSkill(skill)"></i>
        </span>
      </div>
      <input type="text" placeholder="Type skill name to search" v-model="search_term">
    </div>
    <div class="filters">
      <h2>More filters</h2>
      <table>
        <tr>
          <td><div class="salary">Salary:</div></td>
          <td><input type="text" class="value"> - <input type="text" class="value"></td>
        </tr>
        <tr>
          <td><div class="location">Location:</div></td>
          <td><input type="text" class="value-evl"
          v-model="filter_location"></td>
        </tr>
        <tr>
          <td><div class="deadline">Deadline:</div></td>
          <td>within <input type="text" class="value-sm"> days<br>
              within <input type="text" class="value-sm"> month
          </td>
        </tr>
        <tr>
          <td><div class="company-name">Job Name</div></td>
          <td><input type="text" class="value-evl"
          v-model="filter_name"></td>
        </tr>
        <tr>
          <td><div class="company-name">Qualification</div></td>
          <td><input type="text" class="value-evl"
          v-model="filter_qualification"></td>
        </tr>
        <tr>
          <td><div class="company-name">Experience</div></td>
          <td><input type="text" class="value-evl"
          v-model="filter_experience"></td>
        </tr>
      </table>
    </div>
  </div>
  <div class="right">
    <div class="job" v-for="job in jobs_filtered" :key="job">
      <div class="top-content">
        <span class="job-title">
          <h1>{{ job.title }}</h1>
        </span>
        <router-link :to="'/job/' + job.id">Read More</router-link>
        <span class="job-deadline"><strong>Deadline:</strong> {{ job.deadline }}</span>
      </div>
      <div class="bottom-content">
        <table class="first-table">
          <tr>
            <td><div class="matching-skills"><strong>Matching Skills:</strong></div></td>
            <td class="matching-skills-chips">
              <span class="matching-skill" v-for="skill in job.matching_skills" :key="skill">
                {{ skill }}
              </span>
            </td>
          </tr>

          <tr>
            <td><div class="qualification"><strong>Qualification:</strong></div></td>
            <td>{{ job.qualification }}</td>
          </tr>
          <tr>
            <td><div class="experience"><strong>Experience:</strong></div></td>
            <td>{{ job.experience }}</td>
          </tr>
          <tr>
            <td><strong>Description:</strong></td>
            <td class="description-value">{{ job.description }}</td>
          </tr>
        </table>
        <table class="second-table">
          <tr>
            <td><div class="st-salary"><strong>Salary:</strong></div></td>
            <td>{{ job.salary }}</td>
          </tr>
          <tr>
            <td><div class="st-location"><strong>Location:</strong></div></td>
            <td>{{ job.location }}</td>
          </tr>
          <tr>
            <td><div class="st-level"><strong>Level:</strong></div></td>
            <td>{{ job.level }}</td>
          </tr>
        </table>
      </div>
    </div>
  </div>
</div>
</template>
<script lang="ts">
import axios from 'axios';
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Recommend',
  props: ['message'],
  emits: ['emit-snackbar', 'jobs'],
  components: {
  },
  computed: {
    all_skills_filtered() {
      return this.search_term
        ? this.all_skills.filter((skill) => skill.toLowerCase().includes(this.search_term))
        : this.all_skills;
    },
    jobs_filtered() {
      return this.filter_location || this.filter_name || this.filter_qualification
        || this.filter_experience
        ? this.jobs.filter(
          (job) => job.location.toLowerCase().includes(this.filter_location)
            && job.title.toLowerCase().includes(this.filter_name)
            && job.qualification.toLowerCase().includes(this.filter_qualification)
            && job.experience.toLowerCase().includes(this.filter_experience),
        )
        : this.jobs;
    },
  },
  created() {
    this.username = this.$store.getters.getUsername;
    axios({
      method: 'POST',
      url: 'http://127.0.0.1:8000/skills',
      data: {
        username: this.username,
      },
    }).then((response) => {
      if (response.data.skills) {
        this.added_skills = response.data.skills;
        axios({
          method: 'POST',
          url: 'http://127.0.0.1:8000/skills',
        }).then((allskillsresponse) => {
          if (allskillsresponse.data.skills) {
            this.all_skills = allskillsresponse.data.skills.filter(
              (skill) => !this.added_skills.includes(skill),
            );
            axios({
              method: 'POST',
              url: 'http://127.0.0.1:8000/recommend',
              data: {
                skills: this.added_skills,
                offset: 0,
              },
            }).then((skillsresponse) => {
              if (skillsresponse.data) {
                skillsresponse.data.jobs.forEach((job) => {
                  this.jobs.push(JSON.parse(job));
                });
              }
            });
          }
        });
      }
    });
  },
  watch: {
    changes() {
      const confirm = document.querySelector<HTMLButtonElement>('#confirm');
      if (this.changes) {
        confirm.disabled = false;
      } else {
        confirm.disabled = true;
      }
    },
    added_skills() {
      axios({
        method: 'POST',
        url: 'http://127.0.0.1:8000/recommend',
        data: {
          skills: this.added_skills,
          offset: 0,
        },
      }).then((skillsresponse) => {
        if (skillsresponse.data) {
          this.jobs = [];
          skillsresponse.data.jobs.forEach((job) => {
            this.jobs.push(JSON.parse(job));
          });
        }
      });
    },
    all_skills() {
      axios({
        method: 'POST',
        url: 'http://127.0.0.1:8000/recommend',
        data: {
          skills: this.added_skills,
          offset: 0,
        },
      }).then((skillsresponse) => {
        if (skillsresponse.data) {
          this.jobs = [];
          skillsresponse.data.jobs.forEach((job) => {
            this.jobs.push(JSON.parse(job));
          });
        }
      });
    },
    $route() {
      this.$emit('jobs', this.jobs);
    },
  },
  methods: {
    logOut() {
      axios({
        url: 'http://127.0.0.1:8000/logout',
        method: 'POST',
      })
        .then((response) => {
          if (response.data.message === 'successfully logged out!') {
            this.$store.dispatch('setUsername', '');
            localStorage.setItem('username', '');
            this.$router.push('/');
          }
        });
    },
    removeSkill(skillToRemove) {
      this.added_skills = this.added_skills.filter((skill) => skill !== skillToRemove);
      this.all_skills.push(skillToRemove);
      this.changes = true;
    },
    addSkill(skillToAdd) {
      this.all_skills = this.all_skills.filter((skill) => skill !== skillToAdd);
      this.added_skills.push(skillToAdd);
      this.changes = true;
    },
    saveSkills() {
      if (!this.added_skills.length) {
        this.$emit('emit-snackbar', 'Please select at least a skill');
      } else {
        axios({
          method: 'POST',
          url: 'http://127.0.0.1:8000/register',
          data: {
            username: this.$store.getters.getUsername,
            skills: this.added_skills,
            action: 'skills_insert',
          },
        }).then((response) => {
          if (response.data.message === 'successfully inserted!') {
            this.changes = false;

            this.$emit('emit-snackbar', response.data.message);
          }
        });
      }
    },
  },
  data() {
    return {
      username: '',
      added_skills: [],
      all_skills: [],
      changes: false,
      search_term: '',
      jobs: [],
      filter_location: '',
      filter_name: '',
      filter_qualification: '',
      filter_experience: '',
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
.fa.fa-times, .fa.fa-plus {
  font-size: 0.9em;
  margin-left: 5px;
  background: rgb(167, 1, 1);
  color: white;
  border-radius: 50%;
  padding: 4px;
  text-align: center;
  width: 8px;
  cursor: pointer;
  height: 8px;
}
.fa.fa-plus {
  background: rgb(2, 58, 2);
}
.right-nav {
  border-radius: 10px;
  float: right;
  font-weight: bold;
  font-size: 1.5em;
  margin-right: 20px;
  background: rgb(17, 207, 207);
  padding: 5px;
  cursor: pointer;
  position: relative;
  text-decoration: none;
  color: black;
}
.logout {
  padding: 10px;
  font-size: 0.8em;
  background: red;
  color: white;
  border: none;
  position: absolute;
  top: 10px;
  right: 15px;
  transform: translateX(-50%);
  z-index: -5;
  border-radius: 5px;
  transition: top 0.5s ease-in-out, z-index ease-in-out 0.5s;
  cursor: pointer;
}
.right-nav.username:hover + .logout {
  top: 50px;
  z-index: 1;
}
.logout:hover {
  top: 50px;
  z-index: 1;
}
.my-skill{
  color:white;
  display: inline;
  padding: 5px;
}
.container-1 {
  position: relative;
  z-index: 0;
}
.skills{
  width:calc(100%-40px);
  margin: 10px 20px;
  box-sizing: border-box;
  height:20vh;
  background-color: white;
  overflow-y: auto;
  padding: 20px;
}
.skill {
  border: 1px solid gray;
  display: inline-block;
  padding: 10px;
  margin: 2px;
  border-radius: 10px;
  font-size: 10px;
}
.confirmation {
  position: absolute;
  bottom: -15px;
  right: 37px;
}
.confirmation button {
  background: green;
  color: white;
  border: 0;
  border-radius: 20px;
  padding: 10px 20px;
  cursor: pointer;
}
button:disabled {
  background: gray;
  cursor: not-allowed;
}
.description-value {
  display: -webkit-box;
  text-overflow: ellipsis;
  max-width: 600px;
  text-align: justify;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.left, .right {
  height: 600px;
  box-sizing: border-box;
  background: burlywood;
  margin: 10px;
  /* height: calc(90vh - 115px); */
  box-sizing: border-box;
  display: inline-block;
  vertical-align: top;
}
.left {
  width: 20%;
}
.right {
  width: 76.5%;
  overflow-y: auto;
}
.add-skills{
  width:calc(100%-40px);
  margin: 5px 10px;
  box-sizing: border-box;
  height:300px;
  background-color: white;
  position: relative;
  z-index: 1;
  padding: 10px;
}
.skills-inner {
  overflow-y: auto;
  overflow-x: none;
  height: 250px;
}
.add-skills input{
  width: 100%;
  position: absolute;
  bottom: 0;
  left: 0;
  box-sizing: border-box;
  padding: 10px;
  font-size: 13px;
  z-index: 3;
}
.filters table .salary input{
  width:30%;
}
.filters .location input{
  width:70%;
}
.filters .deadline input{
  width:10%;
}
.value {
  width: 75px;
}
.value-sm {
  width: 30px;
}
.right .job{
  width:calc(100%-40px);
  margin: 10px 20px;
  box-sizing: border-box;
  background-color: white;
  padding: 20px;
}
.right .job .top-content {
  width: 100%;
  border-bottom: 1px solid gray;
  padding: 10px;
  display: flex;
  justify-content: space-between;
}
a{
  text-decoration: none;
  cursor: pointer;
  background-color: blue;
  border: 1px solid blue;
  border-radius: 10px;
  color: white;
  padding: 5px 28px;
  text-align: center;
  display: inline-block;
  justify-content: center;
  font-size: 16px;
}
.right .job .bottom-content {
  display: flex;
  justify-content: space-between;
}
.right .job .top-content .job-title{
  font-size: 12px;
  display:inline-block;
}
.matching-skill {
  margin: 2px 5px;
  background: #111;
  color: white;
  border-radius: 10px;
  padding: 8px;
}
.matching-skills-chips {
  display: -webkit-box;
  text-overflow: clip;
  white-space: nowrap;
  max-width: 600px;
  text-align: justify;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
