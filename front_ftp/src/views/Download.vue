<template>
    <div class="file-download-page">
        <h2>文件列表</h2>
        <ul>
            <li v-for="file in files" :key="file.name">
                <label>
                    <input type="checkbox" :value="file.name" v-model="selectedFiles" /> {{ file.name }}
                </label>
            </li>
        </ul>
        <button @click="downloadSelectedFiles">下载选中的文件</button>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            files: [],
            selectedFiles: [],
        };
    },
    created() {
        this.fetchFiles();
    },
    methods: {
        fetchFiles() {
            axios.get('http://localhost:5000/upload/download')
                .then(response => {
                    this.files = response.data.files;
                })
                .catch(error => {
                    console.error("获取文件列表失败:", error);
                });
        },
        downloadSelectedFiles() {
            if (this.selectedFiles.length === 0) {
                alert("请至少选择一个文件！");
                return;
            }

            axios.post('http://localhost:5000/upload/download/zip', { file_names: this.selectedFiles }, {
                responseType: 'blob'
            })
                .then(response => {
                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', 'selected_files.zip');
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                })
                .catch(error => {
                    console.error("下载文件失败:", error);
                });
        }
    }
};
</script>

<style scoped>
.file-download-page {
    padding: 20px;
}

ul {
    list-style-type: none;
    padding: 0;
}

li {
    margin-bottom: 8px;
}

button {
    margin-top: 10px;
}
</style>