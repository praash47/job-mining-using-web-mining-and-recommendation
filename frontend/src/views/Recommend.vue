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
  <router-link to="/logs" class="right-nav" style="background: #2b5701;
  font-weight: 400; color: #ddd;" v-if="isAdmin">
  <i class="fas fa-scroll"></i> Logs
  </router-link>
  <div class="container-1">
    <div class="skills"
        @drop.prevent="addSkill($event)"
        @dragover.prevent
        >
      <Loading v-if="loading_added_skills" />
      <span class="skill"
            title="You can drag this to another box"
            @dragstart = "$event.dataTransfer.setData('skill', skill)"
            v-for="skill in added_skills"
            draggable="true"
            :key="skill">
        {{ skill }}
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
    <div class="add-skills"
        @drop.prevent="removeSkill($event)"
        @dragover.prevent>
      <Loading v-if="loading_all_skills" />
      <div class="skills-inner" v-else>
        <span class="skill"
              title="You can drag this to another box"
              v-for="skill in all_skills_filtered"
              draggable="true"
              @dragstart = "$event.dataTransfer.setData('skill', skill)"
              :key="skill">
          {{ skill }}
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
          <td><input type="number" class="value" v-model="filter_salary.lower" min="1">
          - <input type="number" class="value" v-model="filter_salary.upper" min="2"></td>
        </tr>
        <tr>
          <td><div class="location">Location:</div></td>
          <td><input type="text" class="value-evl"
          v-model="filter_location"></td>
        </tr>
        <tr>
          <td><div class="deadline">Deadline:</div></td>
          <td>
            within
             <input type="number" class="value-sm" v-model="filter_deadline.days" min="0"> day(s)
             <br>
            within
            <input type="number" class="value-sm" v-model="filter_deadline.months" min="0"> month(s)
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
  <div class="right" @scroll="lazyLoading">
    <div class="job" v-for="job in this.jobs" :key="job">
      <div class="top-content">
        <span class="job-title">
          <h1>{{ job.title }}</h1>
        </span>
        <router-link :to="'/job/' + job.id">Read More</router-link>
        <span class="job-deadline">
          <strong>Deadline:</strong> {{ deadline(job.deadline) }}
        </span>
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
    <Loading v-if="loading_jobs" />
  </div>
</div>
</template>
<script lang="ts">
import axios from 'axios';
import { defineComponent } from 'vue';
import Loading from '../components/Loading.vue';

export default defineComponent({
  name: 'Recommend',
  props: ['message'],
  emits: ['emit-snackbar', 'jobs'],
  components: {
    Loading,
  },
  computed: {
    all_skills_filtered() {
      return this.search_term
        ? this.all_skills.filter((skill) => skill.toLowerCase().includes(this.search_term))
        : this.all_skills;
    },
    // jobs_filtered() {
    //   return this.filter_location || this.filter_name || this.filter_qualification
    //     || this.filter_experience || this.filter_salary.lower || this.filter_salary.upper
    //     || this.filter_deadline.days || this.filter_deadline.months
    //     ? this.jobs.filter(
    //       (job) => job.location.toLowerCase().includes(this.filter_location)
    //         && job.title.toLowerCase().includes(this.filter_name)
    //         && job.qualification.toLowerCase().includes(this.filter_qualification)
    //         && job.experience.toLowerCase().includes(this.filter_experience)
    //         && this.salaryInRange(job.salary)
    //         && this.deadlineWithin(job.deadline),
    //     )
    //     : this.jobs;
    // },
  },
  created() {
    this.username = this.$store.getters.getUsername;
    this.isAdmin = this.$store.getters.getIsAdmin;
    axios({
      method: 'POST',
      url: 'http://192.168.1.82:8000/skills',
      data: {
        username: this.username,
      },
    }).then((response) => {
      if (response.data.skills) {
        this.loading_added_skills = false;
        this.added_skills = response.data.skills;
        axios({
          method: 'POST',
          url: 'http://192.168.1.82:8000/skills',
        }).then((allskillsresponse) => {
          if (allskillsresponse.data.skills) {
            this.loading_all_skills = false;
            this.all_skills = allskillsresponse.data.skills.filter(
              (skill) => !this.added_skills.includes(skill),
            );
            this.fetchJobs();
          }
        });
      }
    });
  },
  watch: {
    filter_location() {
      this.offset = 0;
      this.filterJobs();
      setTimeout(() => {
        document.querySelector('.right').scrollTop = 0;
      }, 1);
    },
    filter_name() {
      this.offset = 0;
      this.filterJobs();
      setTimeout(() => {
        document.querySelector('.right').scrollTop = 0;
      }, 1);
    },
    filter_qualification() {
      this.offset = 0;
      this.filterJobs();
      setTimeout(() => {
        document.querySelector('.right').scrollTop = 0;
      }, 1);
    },
    filter_experience() {
      this.offset = 0;
      this.filterJobs();
      setTimeout(() => {
        document.querySelector('.right').scrollTop = 0;
      }, 1);
    },
    filter_salary: {
      handler() {
        this.offset = 0;
        this.filterJobs();
        setTimeout(() => {
          document.querySelector('.right').scrollTop = 0;
        }, 1);
      },
      deep: true,
    },
    filter_deadline: {
      handler() {
        this.offset = 0;
        this.filterJobs();
        setTimeout(() => {
          document.querySelector('.right').scrollTop = 0;
        }, 1);
      },
      deep: true,
    },
    changes() {
      const confirm = document.querySelector<HTMLButtonElement>('#confirm');
      if (this.changes) {
        confirm.disabled = false;
      } else {
        confirm.disabled = true;
      }
    },
    added_skills() {
      this.offset = 0;
      if (!this.loading_jobs) this.fetchJobs();
      setTimeout(() => {
        document.querySelector('.right').scrollTop = 0;
      }, 1);
    },
    all_skills() {
      this.offset = 0;
      if (!this.loading_jobs) this.fetchJobs();
      setTimeout(() => {
        document.querySelector('.right').scrollTop = 0;
      }, 1);
    },
    $route() {
      this.offset = 0;
      this.$emit('jobs', this.jobs);
    },
  },
  methods: {
    fetchJobs() {
      this.loading_jobs = true;
      axios({
        method: 'POST',
        url: 'http://192.168.1.82:8000/recommend',
        data: {
          skills: this.added_skills,
          username: this.username,
          offset: this.offset,
          filter: {
            name: this.filter_name,
            location: this.filter_location,
            qualification: this.filter_qualification,
            experience: this.filter_experience,
            salary: {
              lower: this.filter_salary.lower,
              upper: this.filter_salary.upper,
            },
            deadline: {
              days: this.filter_deadline.days,
              months: this.filter_deadline.months,
            },
          },
        },
      }).then((response) => {
        if (response.data) {
          if (!this.offset) this.jobs = [];
          this.loading_jobs = false;
          response.data.jobs.forEach((job) => {
            this.jobs.push(JSON.parse(job));
          });
          if (!this.jobs.length) this.results_finished = true;
        }
      });
      return this.jobs;
    },
    logOut() {
      axios({
        url: 'http://192.168.1.82:8000/logout',
        method: 'POST',
      })
        .then((response) => {
          if (response.data.message === 'successfully logged out!') {
            this.$store.dispatch('setUsername', '');
            localStorage.setItem('username', '');
            this.$store.dispatch('setIsAdmin', '');
            localStorage.setItem('isAdmin', '');
            this.$router.push('/');
          }
        });
    },
    removeSkill(skillToRemove) {
      this.added_skills = this.sendFromTo(skillToRemove, this.added_skills, this.all_skills);
    },
    addSkill(skillToAdd) {
      this.all_skills = this.sendFromTo(skillToAdd, this.all_skills, this.added_skills);
    },
    sendFromTo(element, from, to) {
      let changingElement;

      if (element.target) {
        changingElement = element.dataTransfer.getData('skill');
      } else {
        changingElement = element;
      }
      // eslint-disable-line
      const fromVal = from.filter((skill) => skill !== changingElement);
      to.push(changingElement);
      setTimeout(() => {
        document.querySelector('.skills').scrollTop = document.querySelector('.skills').scrollHeight;
      }, 1);
      this.changes = true;
      return fromVal;
    },
    saveSkills() {
      if (!this.added_skills.length) {
        this.$emit('emit-snackbar', 'Please select at least a skill');
      } else {
        axios({
          method: 'POST',
          url: 'http://192.168.1.82:8000/register',
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
    salaryInRange(salary) {
      let salaries = salary.split(' ').map((number) => Number(number.replace(/[^0-9.]+/g, '')));
      salaries = salaries.filter((number) => number !== 0 && !Number.isNaN(number)).sort();
      const nSalaries = salaries.length - 1;
      if (this.filter_salary.lower
      && salaries[0] >= this.filter_salary.lower
      && this.filter_salary.lower <= salaries[nSalaries]
      && !this.filter_salary.upper) {
        return true;
      }
      if (this.filter_salary.upper
      && !this.filter_salary.lower
      && salaries[nSalaries] <= this.filter_salary.upper) {
        return true;
      }
      if (!this.filter_salary.upper && !this.filter_salary.lower) {
        return true;
      }
      if (this.filter_salary.lower
      && this.filter_salary.upper
      && this.filter_salary.upper > this.filter_salary.lower
      && this.filter_salary.lower >= salaries[0]
      && this.filter_salary.upper <= salaries[nSalaries]) {
        return true;
      }
      return false;
    },
    deadline(date) {
      const { days, months } = this.getDeadline(date);
      if (Number.isNaN(days) && Number.isNaN(months)) { return 'Not Available'; }
      if (!days && !months) { return 'Deadline Crossed'; }

      const addS = (value) => { if (value > 1) { return 's'; } return ''; };
      const isToday = () => {
        if (months > 0 && days > 0) { return `${days} day${addS(days)}`; }
        if (months === 0 && days === 0) { return 'today'; }
        if (months === 0 && days === 1) { return 'tommorow'; }
        return '';
      };

      return `Within ${(months > 0) ? `${months} month${addS(months)}` : ''}
      ${(months > 0 && days > 0) ? ' and ' : ''}
      ${(days > 1) ? `${days} day${addS(days)}` : isToday()}`;
    },
    getDeadline(date) {
      const deadlineDate = new Date(date).getTime();
      const now = new Date().getTime();
      if (now > deadlineDate) { return { days: false, months: false }; }

      const diff = Math.abs(now - deadlineDate);
      if (Number.isNaN(diff)) { return { days: NaN, months: NaN }; }

      let days = Math.floor(diff / (86400 * 1000));
      const months = Math.floor(days / 30);
      days = (months > 0) ? Math.floor(days % 30) : days;

      return { days, months };
    },
    deadlineWithin(date) {
      const { days, months } = this.getDeadline(date);
      if (!this.filter_deadline.days
      && !this.filter_deadline.months) {
        return true;
      }
      this.filter_deadline.days = this.filter_deadline.days || 0;

      this.filter_deadline.months = (
        this.filter_deadline.months)
        ? Number(this.filter_deadline.months)
        + Math.floor(this.filter_deadline.days / 30)
        : Math.floor(this.filter_deadline.days / 30);

      this.filter_deadline.days = (
        this.filter_deadline.days > 29)
        ? Math.floor(this.filter_deadline.days % 30)
        : this.filter_deadline.days;

      if (this.filter_deadline.days === 0) { return this.filter_deadline.months <= months; }
      if (this.filter_deadline.months === 0) { return this.filter_deadline.days <= days; }

      if (this.filter_deadline.days <= days
      && this.filter_deadline.months <= months) {
        return true;
      }
      if (Number.isNaN(days) && Number.isNaN(months)) { return false; }
      return false;
    },
    filterJobs() {
      this.fetchJobs();
    },
    lazyLoading(e) {
      if (Math.abs(e.target.scrollTop - e.target.scrollHeight) <= 800
      && !this.loading_jobs
      && !this.results_finished) {
        this.loading_jobs = true;
        this.offset += 10;
        this.fetchJobs();
      }
    },
  },
  data() {
    return {
      username: '',
      isAdmin: '',
      added_skills: [],
      all_skills: [],
      changes: false,
      search_term: '',
      jobs: [],
      filter_location: '',
      filter_name: '',
      filter_qualification: '',
      filter_experience: '',
      filter_salary: {
        lower: '',
        upper: '',
      },
      filter_deadline: {
        days: '',
        months: '',
      },
      offset: 0,
      results_finished: false,
      loading_added_skills: true,
      loading_all_skills: true,
      loading_jobs: true,
      first_filter: true,
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
  cursor: move;
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
  user-select: none;
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
