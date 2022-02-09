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
  <div class="left">
      <div class="jobs-list">
          <ul>
              <li v-for="job in recJobs" :key="job.id">
                <router-link :to="'/job/' + job.id">{{ job.title }}</router-link>
              </li>
          </ul>
      </div>
  </div>

  <div class="right">
      <Loading v-if="loading_job" />
      <div class="first-segment" v-else>
          <div class="first-segment-left">
              <h1 class="job-title">{{ job.title }}</h1>
              <a :href="job.url" target="blank">{{ job.url }}</a><br>
              <strong class="company-name">{{ job.company_name }}</strong><br>
              <a href=":mailtojagdambamotors@gmail.com" class="company-email">
                {{ job.company_email }}
              </a>
          </div>
          <div class="first-segment-right">
              <table>
                  <tr>
                      <td><strong>Deadline</strong></td>
                      <td>:</td>
                      <td>{{ job.deadline }}</td>
                  </tr>

                  <tr>
                      <td><strong>Location</strong></td>
                      <td>:</td>
                      <td>{{ job.location }}</td>
                  </tr>

                  <tr>
                      <td><strong>Level</strong></td>
                      <td>:</td>
                      <td>{{ job.level }}</td>
                  </tr>

                  <tr>
                      <td><strong>Salary</strong></td>
                      <td>:</td>
                      <td>{{ job.salary }}</td>
                  </tr>
              </table>
          </div>
      </div>

      <div class="second-segment">
          <h1>Skills</h1><span><strong>Bold</strong> skills are matched skills.</span>
          <div class="second-segment-skills-list">
              <ul>
                  <li v-for="skill in skills" :key="skill">
                    <span v-if="matchingSkills(job).includes(skill)">
                      <strong>{{ skill }}</strong>
                    </span>
                    <span v-else>
                      {{ skill }}
                    </span>
                  </li>
              </ul>
          </div>
      </div>
      <div class="third-segment">
          <div class="qualification">
            <h4 class="qualification-heading:">Qualification</h4> {{ job.qualification }}
          </div>
          <div class="qualification">
            <h4 class="qualification-heading:">Experience</h4> {{ job.experience }}
          </div>
      </div>

      <div class="fourth-segment">
          <h1>Job Description</h1>
          <div class="fourth-segment-description">
              <p>{{ job.description }}</p>
          </div>
      </div>

      <div class="fifth-segment">
          <h1>Miscellaneous Details</h1>
          <div class="fifth-segment-misc">
              <p>{{ job.misc }}</p>
          </div>
      </div>

      <div class="sixth-segment">
          <h1>Company Info</h1>
          <div class="sixth-segment-company-info">
              <p>{{ job.company_info }}</p>
          </div>
      </div>
  </div>
</div>
</template>
<script lang="ts">
import { defineComponent } from 'vue';
import axios from 'axios';
import Loading from '../components/Loading.vue';

export default defineComponent({
  name: 'Job',
  props: ['message', 'recJobs'],
  emits: ['emit-snackbar'],
  components: {
    Loading,
  },
  computed: {
    skills() {
      let { skills } = this.job;
      skills = skills.replaceAll("'", '').replaceAll('{', '').replaceAll('}', '').replaceAll(', ', ',');
      const skillsArr = skills.split(',');

      return skillsArr;
    },
  },
  created() {
    this.username = this.$store.getters.getUsername;
    this.isAdmin = this.$store.getters.getIsAdmin;
    axios({
      method: 'POST',
      url: 'http://localhost:8000/job',
      data: {
        id: this.$route.params.id,
      },
    }).then((response) => {
      this.loading_job = false;
      this.job = response.data;
    });
  },
  watch: {
    $route() {
      this.loading_job = true;
      axios({
        method: 'POST',
        url: 'http://localhost:8000/job',
        data: {
          id: this.$route.params.id,
        },
      }).then((response) => {
        this.loading_job = false;
        this.job = response.data;
      });
    },
  },
  methods: {
    matchingSkills(job) {
      if (this.recJobs.length > 0 && job) {
        let matchedSkills = [];
        this.recJobs.forEach((recJob) => {
          if (recJob.title === job.title) {
            if (recJob.matching_skills.length) {
              matchedSkills = recJob.matching_skills;
            } else {
              matchedSkills = [];
            }
          }
        });
        return matchedSkills;
      }
      return [];
    },
  },
  data() {
    return {
      job: null,
      loading_job: true,
      isAdmin: '',
    };
  },
});
</script>
<style scoped>
a {
  text-decoration: none;
  color: black;
}
.jobs-list ul li a {
  display: block;
}
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
    display: flex;
    justify-content: space-between;
    position: fixed;
    z-index: 200;
    background: rgba(255, 253, 253, 0.459);
    border-bottom: 1px solid rgba(0, 0, 0, 0.082);
    width: 100%;
}
.top ul {
    list-style-type: none;
    display: flex;
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
}
.top ul li:nth-child(2) a {
    display: inline-block;
    background: #001fac;
    box-shadow: inset 5px 5px 10px #001a8f,
            inset -5px -5px 10px #0024c9;
    color: white;
    padding: 10px;
}
.top ul li:nth-child(3) a {
    display: inline-block;
    background: #598000;
    box-shadow: inset 5px 5px 10px #598000,
            inset -5px -5px 10px #2b5701;
    color: white;
    padding: 10px;
}
.back-to-job-button a{
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
}
.left {
    position:absolute;
    top: 90px;
}

.jobs-list{
    width:300px;
    margin:0 10px;
    overflow-y: auto;
    overflow-x: hidden;
    height: 100%;
}

.jobs-list ul{
    height: 100%;
    position:relative;
    background:#fff;
    max-height: 82vh;
}

.jobs-list ul li{
    list-style: none;
    padding:10px;
    width:calc(100%-20px);
    background:#fff;
    box-shadow: 0 5px 25px rgba(0,0,0,.1);
    transition:transform 0.5;
    cursor: pointer;
}
.jobs-list ul li:hover, .jobs-list ul li a.router-link-active{
    transform: scale(1.1) translateX(13px);
    width: calc(100% - 50px);
    z-index:100;
    background:#25bcff;
    box-shadow: 0 5px 25px rgba(0,0,0,.1);
    color:#fff;
}

.right{
    background:rgba(151, 141, 141, 0.5);
    position:absolute;
    top: 90px;
    right: 15px;
    width: 970px;
    padding:10px;
}

.right .first-segment{
    display:flex;
    justify-content:space-between;
    border-bottom: 2px solid black;
}

.first-segment a {
    color: white;
    color: rgb(15, 17, 20);
}

.right .second-segment{
    padding-bottom: 5px;
    border-bottom: 2px solid black;
}
.right .second-segment .second-segment-skills-list{
    padding: 20px;
    columns: 150px 10;
    overflow-x: auto;
    height: 100px;
    word-wrap: break-word;
}

.right .third-segment{
    padding: 10px 0;
    display:flex;
    justify-content: space-between;
    border-bottom: 2px solid black;
}

.right .third-segment .qualification-heading{
    display:inline-block;
}
.fourth-segment{
    border-bottom: 2px solid black;
    padding-bottom:10px;
}

.fifth-segment{
    border-bottom: 2px solid black;
    padding-bottom:10px;
}

.sixth-segment{
    padding-bottom:10px;
}
.container {
  height: 100vh;
}
</style>
