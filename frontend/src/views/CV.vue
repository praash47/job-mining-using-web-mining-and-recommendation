<template>
<div
  class="container"
  @drop.prevent="assignFile($event)"
  @dragleave.prevent
  @dragover.prevent>
  <h1>Upload CV</h1>
  <p>* only pdf files (You can drag and drop your file here)</p>
  <form @submit.prevent="uploadCV" enctype="multipart/form-data">
      <input type='file' id="pdfInp" accept="application/pdf"
      @change='uploading="Selected"' required="required"/><br><br>
      <div class="confirm-button">
          <button type="submit">Confirm</button>
      </div>
  </form>

  <div class="status-bar">
      <strong>Status: </strong>
      <span id="status">{{ uploading }}</span>
  </div>
</div>
</template>
<script lang="ts">
import { defineComponent } from 'vue';
import axios from 'axios';

export default defineComponent({
  name: 'CV',
  emits: ['emit-snackbar'],
  methods: {
    uploadCV() {
      const pdfFile = document.querySelector<HTMLInputElement>('#pdfInp');
      const formData = new FormData();
      formData.append('pdf', pdfFile.files[0]);
      formData.append('username', this.username);
      axios({
        method: 'POST',
        url: 'http://localhost:8000/upload_cv',
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        data: formData,
        onUploadProgress: (e) => {
          this.uploading = `Uploading ${Math.floor((e.loaded / pdfFile.files[0].size) * 100)}%`;
        },
      })
        .then((response) => {
          pdfFile.value = null;
          this.uploading = 'Uploaded';
          this.$emit('emit-snackbar', response.data.message);
        });
    },
    assignFile(e) {
      if (e.dataTransfer.files.length > 1) {
        this.$emit('emit-snackbar', 'You can only drop a single pdf file.');
      } else if (e.dataTransfer.files[0].type !== 'application/pdf') {
        this.$emit('emit-snackbar', 'You can only upload a pdf file.');
      } else {
        document.querySelector<HTMLInputElement>('#pdfInp').files = e.dataTransfer.files;
        this.uploadCV();
      }
    },
  },
  created() {
    this.username = this.$store.getters.getUsername;
  },
  data() {
    return {
      username: '',
      uploading: 'Not Uploaded',
    };
  },
});
</script>
<style scoped>
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
}
.top ul li {
    display: inline-block;
    margin: 20px;
    background: #c44910;
    box-shadow: inset 5px 5px 4px #b2420f,
            inset -5px -5px 4px #d65011;
    color: white;
    padding: 10px;
    cursor: pointer;
    border-radius: 10px;
    text-shadow: -1px -1px 0 rgb(36, 19, 19),
    1px -1px 0 rgb(17, 9, 9),
    -1px 1px 0 rgb(17, 10, 10),
    1px 1px 0 rgb(14, 5, 5);
}
.top ul li:nth-child(2) {
    display: inline-block;
    background: #001fac;
    box-shadow: inset 5px 5px 10px #001a8f,
            inset -5px -5px 10px #0024c9;
    color: white;
    padding: 10px;
}
.container{
    background: rgba(0,0,0,0.5);
    color:white;
    position:absolute;
    width:500px;
    left:300px;
    margin: 20px;
    padding: 17px;
    top:100px;
}

.container .name input{
    height:50px;
    width:400px;
    border-radius:20px;
    padding:10px;
    font-size:15px;

}
.container .add-new-skills{
    background:burlywood;
    position:relative;
    height:200px;
    width:500px;
    margin:15px 0;
    overflow-y: auto;
    box-sizing: border-box;
}

.container .add-new-skills input{
    height:40px;
    width:450px;
    border-radius: 20px;
    font-size: 15px;
    margin:12px;
    padding:5px;
}

.container .add-new-skills .skills{
    color:black;
    background: white;
    border-radius: 20px;
    display:inline-block;
    margin:5px;
    padding:5px;
    width:80px;
    height:30px;
    border:1px solid gray;
}

.confirm-button button{
    background-color: rgb(23, 231, 145);
    border: none;
    color: white;
    padding: 15px 32px;
    text-align: center;
    font-size: 16px;
    cursor:pointer;
}

.status-bar{
    font-size: 20px;
    text-align: center;
    bottom:2px;
    margin: 30px 0;
}

.container form {
    margin: 20px;
    padding: 10px;
}

.container form img{
    max-width: 450px;
    display: none;
}
</style>
