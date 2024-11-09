<template>
  <div class="file-manager-container">
    <div class="user-info-box">
      <h3>用户信息</h3>
      <p>用户名: {{ username }}</p>
      <p>用户类型: {{ userType }}</p>
      <p>存储空间: {{ usedStorage }} / {{totalStorage}}</p>
    </div>
    <div class="file-manager-card">
      <h1 class="main-title">文件管理中心</h1>

      <!-- 文件上传区域 -->
      <section class="upload-section">
        <h2 class="section-title">文件上传</h2>
        <div class="upload-area" :class="{ 'drag-over': isDragging }" @drop.prevent="handleDrop"
          @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false">
          <i class="fas fa-cloud-upload-alt upload-icon"></i>
          <p class="upload-text">拖拽文件到这里或</p>
          <label class="upload-button">
            <input type="file" multiple @change="handleFileUpload" class="file-input" />
            选择文件
          </label>
        </div>

        <!-- 待上传文件列表 -->
        <div v-if="uploadQueue.length" class="upload-queue">
          <h3 class="queue-title">待上传文件 ({{ uploadQueue.length }})</h3>
          <div class="queue-files">
            <div v-for="(file, index) in uploadQueue" :key="index" class="queue-item">
              <div class="file-info">
                <i :class="getFileIcon(file.name)" class="file-icon"></i>
                <div class="file-details">
                  <span class="file-name">{{ file.name }}</span>
                  <span class="file-size">{{ formatFileSize(file.size) }}</span>
                  <span class="file-type">{{ getFileType(file.name) }}</span>
                </div>
              </div>
              <div class="file-actions">
                <button @click="previewFile(file)" v-if="isPreviewable(file)" class="preview-button">
                  <i class="fas fa-eye"></i>
                </button>
                <button @click="removeFromQueue(index)" class="remove-button">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        <!-- 上传进度条 -->
        <!--<div v-if="isUploading" class="upload-progress">
          <div v-for="(progress, filename) in uploadProgress" :key="filename" class="progress-item">
            <div class="progress-info">
              <span class="filename">{{ filename }}</span>
              <span class="percentage">{{ progress }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progress + '%' }"></div>
            </div>
            <div class="upload-speed-info">
              <span>上传速率: {{ uploadSpeed }} KB/s</span>
              <span>预估完成时间: {{ estimatedTime }} 分钟</span>
            </div>
          </div>
        </div>-->

        <!-- <div v-if="isUploading" class="upload-progress">
          <div v-for="(progress, filename) in uploadProgress" :key="filename" class="progress-item">
            <div class="progress-info">
              <span class="filename">{{ filename }}</span>
              <span class="percentage">{{ progress }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progress + '%' }"></div>
            </div>
            <div class="upload-stats">
              <div class="speed-info">
                <span>上传速率: {{ fileProgress[filename]?.speed.toFixed(2) || 0 }} KB/s</span>
              </div>
              <div class="time-info">
                <span>预估剩余时间: {{ fileProgress[filename]?.estimatedTime || 0 }} 分钟</span>
              </div>
            </div>
          </div>

          添加总体进度显示 
          <div class="total-progress" v-if="Object.keys(uploadProgress).length > 1">
            <h4>总体进度</h4>
            <div class="progress-info">
              <span>平均上传速度: {{ uploadSpeed }} KB/s</span>
              <span>预估总剩余时间: {{ estimatedTime }} 分钟</span>
            </div>
          </div>
        </div>-->
        <div v-if="isUploading" class="upload-progress">
          <div v-for="(progress, filename) in uploadProgress" :key="filename" class="progress-item">
            <div class="progress-info">
              <span class="filename">{{ filename }}</span>
              <span class="percentage">{{ progress }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progress + '%' }"></div>
            </div>
            <div class="upload-stats">
              <div class="speed-info">
                <span>上传速率: {{ fileProgress[filename]?.speed.toFixed(2) || 0 }} KB/s</span>
              </div>
              <div class="time-info">
                <span>预估剩余时间: {{ fileProgress[filename]?.estimatedTime || 0 }} 分钟</span>
              </div>
            </div>
          </div>
        </div>
        <!-- 文件预览模态框 -->
        <!-- <div v-if="showPreview" class="preview-modal" @click="closePreview">
          <div class="preview-content" @click.stop>
            <div class="preview-header">
              <h3>{{ previewFile?.name }}</h3>
              <button @click="closePreview" class="close-button">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="preview-body">
              <img v-if="isImageFile(previewFile?.name)" :src="previewUrl" alt="文件预览" />
              <div v-else-if="isTextFile(previewFile?.name)" class="text-preview">
                {{ previewContent }}
              </div>
              <div v-else class="preview-unsupported">
                该文件类型暂不支持预览
              </div>
            </div>
          </div>
        </div> -->

        <!-- 上传进度显示 
        <div v-if="isUploading" class="upload-progress">
          <div v-for="(progress, filename) in uploadProgress" :key="filename" class="progress-item">
            <div class="progress-info">
              <span class="filename">{{ filename }}</span>
              <span class="percentage">{{ progress }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progress + '%' }"></div>
            </div>
          </div>
        </div>-->

        <button @click="uploadFiles" class="action-button upload" :disabled="!uploadQueue.length || isUploading">
          <i class="fas fa-upload"></i>
          {{ isUploading ? '上传中...' : '开始上传' }}
        </button>
      </section>

      <!-- 文件下载区域 -->
      <section class="download-section">
        <h2 class="section-title">文件下载</h2>
        <div class="file-list" v-if="availableFiles.length">
          <div class="file-list-header">
            <label class="select-all">
              <input type="checkbox" @change="toggleSelectAll" :checked="isAllSelected" />
              全选
            </label>
            <span>文件类型</span>
          </div>

          <div class="file-items">
            <div v-for="file in availableFiles" :key="file.name" class="file-item">
              <label class="file-label">
                <input type="checkbox" :value="file.name" v-model="selectedFiles" />
                <span class="file-name">{{ file.name }}</span>
                <span class="file-type">{{ file.type }}</span>
              </label>
            </div>
          </div>
        </div>
        <p v-else class="no-files">暂无可下载文件</p>
        <!-- <progress-bar :value="downloadProgress" /> -->
        <div class="action-buttons">
          <button @click="downloadFiles" class="action-button download" :disabled="!selectedFiles.length">
            <i class="fas fa-download"></i> 下载选中文件
          </button>

          <div v-for="(task, index) in downloadTasks" :key="index">
            <div v-if="task.isDownloading">
              <div>文件：{{ task.fileName }}</div>
              <progress :value="task.progress" max="100"></progress>
              <div>进度：{{ task.progress }}% | 速度：{{ task.speed }} KB/s</div>
            </div>
            <div v-else>
              <div>文件 {{ task.fileName }} 下载完成！</div>
            </div>
          </div>

          <button @click="closeSocket" class="action-button disconnect">
            <i class="fas fa-plug"></i> 断开连接
          </button>
        </div>

        <!-- 删除文件按钮 -->
        <div class="action-buttons">
          <button @click="deleteSelectedFiles" class="action-button delete" :disabled="!selectedFiles.length">
            <i class="fas fa-trash-alt"></i> 删除选中文件
          </button>
        </div>

      </section>



      <!-- 消息提示 -->
      <transition name="fade">
        <div v-if="message" class="message" :class="{ 'error': isError }">
          {{ message }}
        </div>
      </transition>

      <input type="file" ref="fileInput" @change="verifyDownloadedFile" accept=".zip" style="display: none;" />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { io } from 'socket.io-client';
import JSZip from 'jszip';
// eslint-disable-next-line
import { ref, reactive } from 'vue';  // 引入 Vue 3 的响应式 API

export default {
  data() {
    return {
      files: [],
      // filenames: '',
      message: '',
      selectedFiles: [],  // 存储用户选中的文件列表
      availableFiles: [], // 存储可下载的文件列表
      socket: null,
      downloadedFileHashes: {}, // 用于存储下载时的哈希值
      isDragging: false,
      isError: false,
      uploadQueue: [],
      isUploading: false,
      uploadProgress: {},
      showPreview: false,
      previewFile: null,
      currentPreviewFile: null,
      previewUrl: null,
      previewContent: null,
      token: '',
      // eslint-disable-next-line
      uploadQueue: [],
      // eslint-disable-next-line
      isUploading: false,
      // eslint-disable-next-line
      uploadProgress: {},  // 使用 reactive 创建响应式对象
      fileProgress: {}, // 新增：跟踪每个文件的具体进度信息
      uploadSpeed: 0,
      estimatedTime: 0,
      username: '',
      usertype: '',
      usedStorage: '',
      totalStorage: '',
      pollInterval: null,
      isDownloading: false,  // 下载状态
      downloadProgress: {  // 下载进度和速度
        progress: 0,
        speed: 0
      },
      downloadTasks: []    // 存储下载任务列表，每个任务包含进度、文件名等信息

    };
  },
  async mounted() {

    this.token = localStorage.getItem('token');
    // localStorage.clear()
    if (!this.token) {
      // 如果 token 缺失，重定向到登录页面或显示错误
      this.$router.push({ path: '/auth/login' });
    }

    // 创建 Socket.IO 客户端连接
    this.socket = io("https://localhost:5000");

    // 监听连接事件
    this.socket.on("connect", () => {
      console.log("Connected to Socket.IO server");
      this.message = "连接到 Socket.IO 服务器";
    });

    // 监听断开连接事件
    this.socket.on("disconnect", () => {
      console.log("Disconnected from Socket.IO server");
      this.message = "与 Socket.IO 服务器断开连接";
    });

    // 获取文件列表以供选择下载
    await this.fetchAvailableFiles();


    // 获取用户信息
    // await this.getUserInfo();

    // 获取存储空间使用情况
    await this.getStorageUsage();



  },
  computed: {
    isAllSelected() {
      return this.availableFiles.length === this.selectedFiles.length;
    }
  },
  methods: {
    // 文件图标获取
    getFileIcon(filename) {
      const extension = filename.split('.').pop().toLowerCase();
      const iconMap = {
        pdf: 'fa-file-pdf',
        doc: 'fa-file-word',
        docx: 'fa-file-word',
        xls: 'fa-file-excel',
        xlsx: 'fa-file-excel',
        jpg: 'fa-file-image',
        jpeg: 'fa-file-image',
        png: 'fa-file-image',
        gif: 'fa-file-image',
        txt: 'fa-file-alt',
      };
      return `fas ${iconMap[extension] || 'fa-file'}`;
    },

    // 获取文件类型
    getFileType(filename) {
      const extension = filename.split('.').pop().toLowerCase();
      const typeMap = {
        pdf: 'PDF文档',
        doc: 'Word文档',
        docx: 'Word文档',
        xls: 'Excel表格',
        xlsx: 'Excel表格',
        jpg: '图片',
        jpeg: '图片',
        png: '图片',
        gif: '动图',
        txt: '文本文件',
      };
      return typeMap[extension] || '未知类型';
    },
    // 格式化文件大小
    formatFileSize(size) {
      if (size < 1024) return size + ' B';
      if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB';
      if (size < 1024 * 1024 * 1024) return (size / (1024 * 1024)).toFixed(1) + ' MB';
      return (size / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
    },

    // 文件是否可预览
    isPreviewable(file) {
      return this.isImageFile(file.name) || this.isTextFile(file.name);
    },

    // 是否为图片文件
    isImageFile(filename) {
      return /\.(jpg|jpeg|png|gif)$/i.test(filename);
    },

    // 是否为文本文件
    isTextFile(filename) {
      return /\.(txt|log|md)$/i.test(filename);
    },

    // 预览文件
    // eslint-disable-next-line
    async previewFile(file) {
      this.previewFile = file;
      this.showPreview = true;

      if (this.isImageFile(file.name)) {
        this.previewUrl = URL.createObjectURL(file);
      } else if (this.isTextFile(file.name)) {
        try {
          const text = await this.readFileAsText(file);
          this.previewContent = text;
        } catch (error) {
          console.error('读取文件失败:', error);
          this.previewContent = '文件读取失败';
        }
      }
    },

    // 读取文件内容
    readFileAsText(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(e);
        reader.readAsText(file);
      });
    },

    // 关闭预览
    closePreview() {
      this.showPreview = false;
      if (this.previewUrl) {
        URL.revokeObjectURL(this.previewUrl);
      }
      this.previewUrl = null;
      this.previewContent = null;
      this.previewFile = null;
    },

    handleFileUpload(event) {
      const files = Array.from(event.target.files || event.dataTransfer.files);
      this.uploadQueue.push(...files);
      if (event.target.value) {
        event.target.value = '';
      }
    },
    handleDrop(e) {
      this.isDragging = false;
      const files = Array.from(e.dataTransfer.files);
      this.handleFileUpload({ target: { files } });
    },

    removeFromQueue(index) {
      this.uploadQueue.splice(index, 1);
    },

    async calculateFileHash(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = async (event) => {
          const buffer = event.target.result;
          crypto.subtle.digest('SHA-256', buffer).then(hashBuffer => {
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
            resolve(hashHex);
          }).catch(error => reject(error));
        };
        reader.onerror = () => reject("读取文件失败");
        reader.readAsArrayBuffer(file);
      });
    },
    async pollUploadProgress() {
      try {
        const response = await axios.get('https://localhost:5000/upload', {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.token}`
          },
          withCredentials: true
        });

        this.uploadProgress = response.data.progress;
        this.fileProgress = response.data.progress;
      } catch (error) {
        console.error('Failed to fetch upload progress:', error);
      }
    },
    // async uploadFiles() {
    //   const formData = new FormData();
    //   const fileHashes = {}; // 用于存储文件的哈希值
    //   this.isUploading = true;
    //   const startTime = new Date().getTime();

    //   for (const file of this.uploadQueue) {
    //     const hash = await this.calculateFileHash(file);
    //     fileHashes[file.name] = hash; // 保存文件的哈希值
    //     formData.append('files', file);
    //     formData.append(`hash_${file.name}`, hash); // 将哈希值附加到表单数据中

    //   }

    //   try {
    //     const response = await axios.post('https://localhost:5000/upload', formData, {
    //       headers: {
    //         'Content-Type': 'multipart/form-data',
    //         Authorization: `Bearer ${this.token}`,
    //       },
    //       withCredentials: true,
    //     });

    //     alert('文件上传成功！在传输过程中未被篡改！' + response.data.uploaded_files.join(', '));
    //     await this.fetchAvailableFiles(); // 上传成功后重新获取可下载文件列表
    //   } catch (error) {
    //     if (error.response && error.response.data) {
    //       // 如果后端返回了错误信息，显示给用户
    //       alert('上传失败: ' + error.response.data.error);
    //     } else {
    //       console.error("上传文件失败", error);
    //       alert('上传失败');
    //     }
    //   }
    //   this.isUploading = false;

    //   const endTime = new Date().getTime();
    //   const elapsedTime = endTime - startTime;
    //   const totalBytes = Object.values(this.uploadProgress).reduce((total, progress) => total + progress, 0);
    //   this.uploadSpeed = (totalBytes / (elapsedTime / 1000)) / 1024; // 计算上传速率(KB/s)
    //   this.estimatedTime = this.uploadQueue.length * (elapsedTime / totalBytes); // 计算预估完成时间(秒)


    // },


    async uploadFiles() {
      if (this.uploadQueue.length === 0) {
        alert("请选择要上传的文件！");
        return;
      }

      this.isUploading = true;
      const startTime = new Date().getTime();
      const formData = new FormData();
      const fileHashes = {};

      // 初始化进度信息
      this.uploadQueue.forEach(file => {
        this.fileProgress[file.name] = {
          loaded: 0,
          total: file.size,
          speed: 0,
          lastLoaded: 0,
          lastTime: startTime,
          estimatedTime: 0,
          status: 'pending' // 添加状态跟踪
        };
      });

      try {
        // 计算总大小
        const totalSize = this.uploadQueue.reduce((sum, file) => sum + file.size, 0);

        // 计算哈希并准备上传数据
        for (const file of this.uploadQueue) {
          const hash = await this.calculateFileHash(file);
          fileHashes[file.name] = hash;
          formData.append('files', file);
          formData.append(`hash_${file.name}`, hash);
        }

        // 创建用于轮询上传状态的函数
        const pollUploadProgress = async () => {
          try {
            const response = await axios.get('https://localhost:5000/upload', formData, {
              headers: {
                'Content-Type': 'multipart/form-data',
                Authorization: `Bearer ${this.token}`
              },
              withCredentials: true
            });

            const serverProgress = response.data.progress;

            // 更新每个文件的实际进度
            Object.keys(serverProgress).forEach(fileName => {
              if (this.fileProgress[fileName]) {
                const fileInfo = serverProgress[fileName];
                const currentTime = new Date().getTime();
                const fileProgressInfo = this.fileProgress[fileName];

                // 更新实际已上传量
                const newLoaded = fileInfo.bytesWritten;
                const loadedDelta = newLoaded - fileProgressInfo.lastLoaded;
                const timeDelta = (currentTime - fileProgressInfo.lastTime) / 1000;

                // 计算实际上传速度 (KB/s)
                const currentSpeed = timeDelta > 0 ? (loadedDelta / 1024) / timeDelta : 0;
                fileProgressInfo.speed = (fileProgressInfo.speed * 0.7 + currentSpeed * 0.3);

                // 更新进度
                const progress = Math.min(Math.round((newLoaded / fileInfo.totalBytes) * 100), 100);
                this.uploadProgress[fileName] = progress;

                // 更新预估剩余时间
                const remainingBytes = fileInfo.totalBytes - newLoaded;
                const estimatedSeconds = fileProgressInfo.speed > 0
                  ? (remainingBytes / 1024) / fileProgressInfo.speed
                  : 0;
                fileProgressInfo.estimatedTime = (estimatedSeconds / 60).toFixed(2);

                // 更新状态
                fileProgressInfo.status = fileInfo.status;
                fileProgressInfo.lastLoaded = newLoaded;
                fileProgressInfo.lastTime = currentTime;
              }
            });

            // 更新总体进度
            const totalLoaded = Object.values(this.fileProgress)
              .reduce((sum, progress) => sum + progress.lastLoaded, 0);
            const averageSpeed = Object.values(this.fileProgress)
              .reduce((sum, progress) => sum + progress.speed, 0) / this.uploadQueue.length;

            this.uploadSpeed = averageSpeed.toFixed(2);
            const remainingTotal = totalSize - totalLoaded;
            this.estimatedTime = averageSpeed > 0
              ? ((remainingTotal / 1024) / averageSpeed / 60).toFixed(2)
              : 0;

            // 检查是否所有文件都已完成
            const allCompleted = Object.values(serverProgress)
              .every(fileInfo => fileInfo.status === 'completed');

            if (!allCompleted && this.isUploading) {
              // 继续轮询
              setTimeout(pollUploadProgress, 1000);
            }
          } catch (error) {
            console.error('Failed to fetch upload progress:', error);
            if (this.isUploading) {
              // 如果出错但上传未结束，继续轮询
              setTimeout(pollUploadProgress, 1000);
            }
          }
        };

        // 开始上传
        const response = await axios.post('https://localhost:5000/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${this.token}`,
          },
          withCredentials: true,
        });

        // 启动进度轮询
        pollUploadProgress();

        // 上传成功后的处理
        if (response.data.uploaded_files && response.data.uploaded_files.length > 0) {
          this.uploadQueue = this.uploadQueue.filter(
            file => !response.data.uploaded_files.includes(file.name)
          );

          alert('文件上传成功！在传输过程中未被篡改！' + response.data.uploaded_files.join(', '));
          await this.fetchAvailableFiles();
          await this.getStorageUsage();
        }
      } catch (error) {
        if (error.response && error.response.data) {
          alert('上传失败: ' + error.response.data.error);
        } else {
          console.error("上传文件失败", error);
          alert('上传失败');
        }
      } finally {
        this.isUploading = false;
        // this.resetUploadState();
      }
    },
    // async uploadFiles() {
    //   if (this.uploadQueue.length === 0) {
    //     this.$message.warning("请选择要上传的文件！");
    //     return;
    //   }

    //   this.isUploading = true;
    //   const formData = new FormData();
    //   // eslint-disable-next-line
    //   const fileHashes = {};

    //   try {
    //     // 准备上传文件
    //     for (const file of this.uploadQueue) {
    //       formData.append('files', file);
    //       const hash = await this.calculateFileHash(file);
    //       formData.append(`hash_${file.name}`, hash);

    //       // 初始化进度信息
    //       this.fileProgress[file.name] = {
    //         loaded: 0,
    //         total: file.size,
    //         speed: 0,
    //         status: 'pending'
    //       };
    //     }

    //     this.resetUploadState();
    //     // 开始轮询进度
    //     this.startProgressPolling();

    //     // 执行上传
    //     const response = await axios.post('https://localhost:5000/upload', formData, {
    //       headers: {
    //         'Content-Type': 'multipart/form-data',
    //         Authorization: `Bearer ${this.token}`
    //       },
    //       withCredentials: true,
    //       // 添加上传进度处理
    //       onUploadProgress: (progressEvent) => {
    //         // eslint-disable-next-line
    //         const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
    //         // 更新总体上传进度
    //         this.calculateOverallProgress();
    //       }
    //     });

    //     if (response.data.status === 'success') {
    //       this.$message.success('文件上传成功！');
    //       await this.fetchAvailableFiles();
    //     }
    //   } catch (error) {
    //     this.handleUploadError(error);
    //   } finally {
    //     this.stopProgressPolling();
    //     this.isUploading = false;
    //   }
    // },

    // startProgressPolling() {
    //   this.pollInterval = setInterval(async () => {
    //     try {
    //       const response = await axios.get('https://localhost:5000/upload', {
    //         headers: {
    //           Authorization: `Bearer ${this.token}`
    //         }
    //       });

    //       this.updateProgress(response.data.progress);
    //     } catch (error) {
    //       console.error('获取进度失败:', error);
    //     }
    //   }, 1000);
    // },

    // stopProgressPolling() {
    //   if (this.pollInterval) {
    //     clearInterval(this.pollInterval);
    //     this.pollInterval = null;
    //   }
    // },

    // updateProgress(serverProgress) {
    //   Object.entries(serverProgress).forEach(([filename, progress]) => {
    //     if (this.fileProgress[filename]) {
    //       const currentTime = Date.now();
    //       const fileProgress = this.fileProgress[filename];

    //       // 更新进度信息
    //       const loadedDelta = progress.bytesWritten - fileProgress.loaded;
    //       const timeDelta = (currentTime - (fileProgress.lastUpdate || currentTime)) / 1000;

    //       if (timeDelta > 0) {
    //         fileProgress.speed = (loadedDelta / 1024) / timeDelta; // KB/s
    //       }

    //       fileProgress.loaded = progress.bytesWritten;
    //       fileProgress.status = progress.status;
    //       fileProgress.lastUpdate = currentTime;

    //       // 更新上传进度百分比
    //       this.uploadProgress[filename] = progress.percentage;
    //     }
    //   });

    //   // 计算总体进度
    //   this.calculateOverallProgress();
    // },

    // calculateOverallProgress() {
    //   const totalLoaded = Object.values(this.fileProgress)
    //     .reduce((sum, progress) => sum + progress.loaded, 0);
    //   const totalSize = Object.values(this.fileProgress)
    //     .reduce((sum, progress) => sum + progress.total, 0);

    //   this.uploadSpeed = Object.values(this.fileProgress)
    //     .reduce((sum, progress) => sum + (progress.speed || 0), 0);

    //   if (this.uploadSpeed > 0) {
    //     const remainingBytes = totalSize - totalLoaded;
    //     this.estimatedTime = (remainingBytes / 1024) / this.uploadSpeed / 60; // 分钟
    //   }
    // },

    // handleUploadError(error) {
    //   let errorMessage = '上传失败';
    //   // 更健壮的错误处理
    //   if (error?.response?.data?.error) {
    //     errorMessage = error.response.data.error;
    //   } else if (error?.message) {
    //     errorMessage = error.message;
    //   }
    //   this.$message.error(errorMessage);
    //   console.error('上传错误:', error);

    //   // 确保清理上传状态
    //   this.resetUploadState();
    // },
    // resetUploadState() {
    //   this.uploadProgress = {};
    //   this.fileProgress = {};
    //   this.uploadSpeed = 0;
    //   this.estimatedTime = 0;
    // },

    // async uploadFiles() {
    //   this.isUploading = true;
    //   const startTime = new Date().getTime();
    //   const formData = new FormData();
    //   // eslint-disable-next-line
    //   const fileHashes = {}; // 用于存储文件的哈希值
    //   try {
    //     const response = await axios.post('https://localhost:5000/upload', formData, {
    //       headers: {
    //         'Content-Type': 'multipart/form-data',
    //         Authorization: `Bearer ${this.token}`,
    //       },
    //       withCredentials: true,
    //       onUploadProgress: (progressEvent) => {
    //         if (progressEvent.lengthComputable) {
    //           const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
    //           const filename = this.uploadQueue.find((file) => file.name === progressEvent.config.data.get('files')).name;
    //           this.$set(this.uploadProgress, filename, progress);
    //         }
    //       },
    //     });

    //     alert('文件上传成功！在传输过程中未被篡改！' + response.data.uploaded_files.join(', '));
    //     await this.fetchAvailableFiles(); // 上传成功后重新获取可下载文件列表

    //     // 从 uploadQueue 中移除已上传的文件
    //     this.uploadQueue = this.uploadQueue.filter(
    //       (file) => !response.data.uploaded_files.includes(file.name)
    //     );
    //   } catch (error) {
    //     if (error.response && error.response.data) {
    //       // 如果后端返回了错误信息，显示给用户
    //       alert('上传失败: ' + error.response.data.error);
    //     } else {
    //       console.error("上传文件失败", error);
    //       alert('上传失败');
    //     }
    //   } finally {
    //     this.isUploading = false;
    //     const endTime = new Date().getTime();
    //     const elapsedTime = endTime - startTime;
    //     const totalBytes = Object.values(this.uploadProgress).reduce((total, progress) => total + progress, 0);
    //     this.uploadSpeed = (totalBytes / (elapsedTime / 1000)) / 1024; // 计算上传速率(KB/s)
    //     this.estimatedTime = this.uploadQueue.length * (elapsedTime / totalBytes); // 计算预估完成时间(秒)
    //   }
    // },

    // 获取可用文件列表
    async fetchAvailableFiles() {
      try {
        const response = await axios.get('https://localhost:5000/upload/download', { withCredentials: true, headers: { Authorization: `Bearer ${this.token}`, } });
        this.availableFiles = response.data.files;
        console.log("文件列表:", this.availableFiles);  // 调试信息
      } catch (error) {
        console.error("获取文件列表失败", error);
      }
    },

    // 下载选中的文件并解压、验证哈希值

    async downloadFiles() {
      if (this.selectedFiles.length === 0) {
        alert("请选择至少一个文件进行下载！");
        return;
      }
      // 清空现有的下载任务
      this.downloadTasks = [];
      this.isDownloading = true;  // 开始下载
      this.downloadProgress = { progress: 0, speed: 0 }; // 重置下载进度

      try {
        const response = await axios.post(
          'https://localhost:5000/upload/download/zip',
          { file_names: this.selectedFiles },
          {
            responseType: 'blob',
            withCredentials: true,
            headers: {
              Authorization: `Bearer ${this.token}`,
            },
            onDownloadProgress: (progressEvent) => {
              // // 计算下载进度并更新 Progress Bar 组件
              // const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              // this.downloadProgress = progress;
              if (progressEvent.loaded && progressEvent.total) {
                const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                const speed = ((progressEvent.loaded / 1024) / (progressEvent.time / 1000)).toFixed(2);
                // 更新进度和速度
                this.downloadProgress = {
                  progress: progress,
                  speed: speed,
                };
              }
            },
          }
        );

        // 获取文件哈希值
        const fileHashes = response.headers['x-file-hashes'];
        if (!fileHashes) {
          console.error("未收到文件哈希值");
          return;
        }

        const parsedHashes = JSON.parse(fileHashes);
        console.log("服务器返回的文件哈希值:", parsedHashes);

        // 创建 Blob 对象
        const zipBlob = new Blob([response.data]);

        // 验证下载的文件哈希值
        const isValid = await this.verifyDownloadedFiles(zipBlob, parsedHashes);

        if (isValid) {
          // 创建下载链接
          const url = window.URL.createObjectURL(zipBlob);
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', 'selected_files.zip');
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        } else {
          alert('文件完整性验证失败，请重新下载！');
        }
      } catch (error) {
        console.error("下载文件失败", error);
        alert('下载失败: ' + error.message);
      } finally {
        this.isDownloading = false;  // 下载完成
      }
    },

    async verifyDownloadedFiles(zipBlob, fileHashes) {
      const jszip = new JSZip();

      try {
        console.log("开始验证文件...");
        const zip = await jszip.loadAsync(zipBlob);
        let allFilesValid = true;

        for (const filename of Object.keys(zip.files)) {
          const file = zip.files[filename];
          if (file.dir) continue; // 跳过目录

          // 获取服务器端的哈希值
          const serverHash = fileHashes[filename];
          if (!serverHash) {
            console.warn(`未找到文件 ${filename} 的服务器端哈希值`);
            continue;
          }

          // 读取文件内容
          const fileData = await file.async("arraybuffer");
          // 计算哈希值
          const clientHash = await this.calculateSHA256(fileData);

          console.log(`文件: ${filename}`);
          console.log(`服务器哈希: ${serverHash}`);
          console.log(`客户端哈希: ${clientHash}`);

          if (serverHash !== clientHash) {
            console.error(`文件 ${filename} 哈希值不匹配`);
            allFilesValid = false;
          }
        }

        return allFilesValid;
      } catch (error) {
        console.error("验证文件时出错", error);
        return false;
      }
    },


    // 删除文件
    async deleteFiles(filenames) {
      // 提示用户确认是否删除文件
      const confirmDelete = window.confirm("确定要删除选中的文件吗？此操作无法撤销。");
      if (!confirmDelete) {
        // 如果用户取消操作，直接返回
        console.log('用户取消删除操作');
        return;
      }
      try {
        const response = await fetch('https://localhost:5000/upload/delete', {

          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.token}`,
          },
          body: JSON.stringify({ filenames })
        });

        // 检查响应是否有效且返回 JSON
        if (response.ok && response.headers.get('Content-Type').includes('application/json')) {
          const data = await response.json();
          return data;
        } else {
          const text = await response.text();  // 解析错误信息
          throw new Error(text || 'Error deleting files');
        }
      } catch (error) {
        console.error('Error deleting files:', error);
        throw error;
      }
    },


    // 使用 SHA-256 计算哈希值
    async calculateSHA256(data) {
      try {
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        return hashHex;
      } catch (error) {
        console.error("计算哈希值出错", error);
        throw error;
      }
    },
    // 1111111111111111111111111111111111111111111111111111111111111
    async deleteSelectedFiles() {
      try {
        await this.deleteFiles(this.selectedFiles);
        this.selectedFiles = [];
        await this.fetchAvailableFiles();
        this.message = '选中文件已删除成功';
        await this.getStorageUsage();
      } catch (error) {
        this.message = '删除文件失败: ' + error.message;
        this.isError = true;
      }
    },
    // eslint-disable-next-line
    // async deleteFiles(filenames) {
    //   try {
    //     const response = await fetch('/upload/delete', {
    //       method: 'POST',
    //       headers: {
    //         'Content-Type': 'application/json'
    //       },
    //       body: JSON.stringify({ filenames })
    //     });

    //     const data = await response.json();
    //     if (response.ok) {
    //       return data;
    //     } else {
    //       throw new Error(data.error || 'Error deleting files');
    //     }
    //   } catch (error) {
    //     console.error('Error deleting files:', error);
    //     throw error;
    //   }
    // },


    // async getUserInfo() {
    //   try {
    //     const response = await fetch('https://localhost:5000/user/info', {
    //       headers: {
    //         Authorization: `Bearer ${this.token}`,
    //       },
    //     });

    //     if (response.ok) {
    //       const data = await response.json();
    //       this.username = data.username || '未知用户名';
    //       this.usertype = data.usertype || '普通用户';
    //     } else {
    //       throw new Error('获取用户信息失败');
    //     }
    //   } catch (error) {
    //     console.error('Error getting user info:', error);
    //     this.username = '未知用户名';
    //     this.usertype = '未知类型';
    //   }
    // },
    // eslint-disable-next-line
    async getStorageUsage() {
      try {
        const response = await fetch('https://localhost:5000/upload/usage', {
          headers: {
            Authorization: `Bearer ${this.token}`,
          },
        });
        const data = await response.json();
        console.log("获取用户信息")
        console.log(data)
        if (response.ok) {
          this.username = data.username;
          this.userType = data.user_type;
          this.usedStorage = data.used_space || 0;
          this.totalStorage = data.total_space || 0;
        } else {
          throw new Error(data.error || 'Error getting storage usage');
        }
      } catch (error) {
        console.error('Error getting storage usage:', error);
        this.usedStorage = 0;
        this.totalStorage = 0;
      }
    },
    // eslint-disable-next-line
    formatFileSize(size) {
      if (size < 1024) return size + ' B';
      if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB';
      if (size < 1024 * 1024 * 1024) return (size / (1024 * 1024)).toFixed(1) + ' MB';
      return (size / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
    },
    toggleSelectAll(e) {
      if (e.target.checked) {
        this.selectedFiles = this.availableFiles.map(file => file.name);
      } else {
        this.selectedFiles = [];
      }
    },
    // eslint-disable-next-line
    handleDrop(e) {
      this.isDragging = false;
      const files = Array.from(e.dataTransfer.files);
      this.handleFileUpload({ target: { files } });
    },


    closeSocket() {
      // 手动关闭 Socket.IO 客户端连接
      if (this.socket) {
        this.socket.disconnect();
        console.log("Socket.IO 客户端已断开连接");
        this.message = "Socket.IO 客户端已断开连接";
      }
    }
  },
  beforeDestroy() {
    // 确保在组件销毁时关闭连接
    this.closeSocket();
  }
};
</script>

<style scoped>
.file-manager-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 2rem 1rem;
}

.file-manager-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 800px;
  padding: 2rem;
}

.main-title {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 2rem;
  text-align: center;
  font-weight: 600;
}

.section-title {
  color: #4a5568;
  font-size: 1.2rem;
  margin-bottom: 1rem;
  font-weight: 500;
}

/* 上传区域样式 */
.upload-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e2e8f0;
}

.upload-area {
  border: 2px dashed #cbd5e0;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
}

.upload-area.drag-over {
  border-color: #4299e1;
  background-color: #ebf8ff;
}

.upload-icon {
  font-size: 2.5rem;
  color: #4299e1;
  margin-bottom: 1rem;
}

.upload-text {
  color: #718096;
  margin-bottom: 1rem;
}

.file-input {
  display: none;
}

.upload-button {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: #4299e1;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.upload-button:hover {
  background-color: #3182ce;
}

/* 文件列表样式 */
.file-list {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.file-list-header {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: #f7fafc;
  border-bottom: 1px solid #e2e8f0;
}

.select-all {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4a5568;
}

.file-items {
  max-height: 300px;
  overflow-y: auto;
}

.file-item {
  border-bottom: 1px solid #e2e8f0;
}

.file-item:last-child {
  border-bottom: none;
}

.file-label {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.file-label:hover {
  background-color: #f7fafc;
}

.file-name {
  flex: 1;
  margin-left: 0.5rem;
  color: #2d3748;
}

.file-type {
  color: #718096;
  font-size: 0.875rem;
}

/* 按钮样式 */
.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.action-button.upload {
  background-color: #4299e1;
  color: white;
}

.action-button.upload:hover {
  background-color: #3182ce;
}

.action-button.download {
  background-color: #48bb78;
  color: white;
}

.action-button.download:hover {
  background-color: #38a169;
}

.action-button.download:disabled {
  background-color: #cbd5e0;
  cursor: not-allowed;
}

.action-button.disconnect {
  background-color: #e53e3e;
  color: white;
}

.action-button.disconnect:hover {
  background-color: #c53030;
}

/* 消息提示样式 */
.message {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 4px;
  background-color: #9ae6b4;
  color: #276749;
  text-align: center;
}

.message.error {
  background-color: #fed7d7;
  color: #c53030;
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .file-manager-card {
    padding: 1rem;
  }

  .main-title {
    font-size: 1.5rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-button {
    width: 100%;
  }
}

/* 确保添加 Font Awesome 的 CDN */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

.upload-queue {
  margin-top: 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.queue-title {
  padding: 0.75rem 1rem;
  background-color: #f7fafc;
  border-bottom: 1px solid #e2e8f0;
  color: #4a5568;
  font-size: 1rem;
  font-weight: 500;
}

.queue-files {
  max-height: 300px;
  overflow-y: auto;
}

.queue-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.queue-item:last-child {
  border-bottom: none;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.file-icon {
  color: #4a5568;
  font-size: 1.25rem;
}

.file-details {
  display: flex;
  flex-direction: column;
}

.file-size {
  font-size: 0.875rem;
  color: #718096;
}

.remove-button {
  padding: 0.25rem;
  color: #e53e3e;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.3s ease;
}

.remove-button:hover {
  color: #c53030;
}

.upload-progress {
  margin-top: 1rem;
}

.progress-item {
  margin-bottom: 0.75rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.filename {
  font-size: 0.875rem;
  color: #4a5568;
}

.percentage {
  font-size: 0.875rem;
  color: #718096;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background-color: #edf2f7;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #4299e1;
  transition: width 0.3s ease;
}

.action-button:disabled {
  background-color: #cbd5e0;
  cursor: not-allowed;
}

.preview-button {
  padding: 0.25rem;
  color: #4299e1;
  background: none;
  border: none;
  cursor: pointer;
  margin-right: 0.5rem;
  transition: color 0.3s ease;
}

.preview-button:hover {
  color: #2b6cb0;
}

.preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.preview-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.preview-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #2d3748;
}

.close-button {
  background: none;
  border: none;
  color: #718096;
  cursor: pointer;
  padding: 0.5rem;
  transition: color 0.3s ease;
}

.close-button:hover {
  color: #4a5568;
}

.preview-body {
  padding: 1rem;
  overflow: auto;
  max-height: calc(90vh - 60px);
}

.preview-body img {
  max-width: 100%;
  height: auto;
}

.text-preview {
  white-space: pre-wrap;
  font-family: monospace;
  padding: 1rem;
  background-color: #f7fafc;
  border-radius: 4px;
}

.preview-unsupported {
  text-align: center;
  padding: 2rem;
  color: #718096;
}

.file-type {
  font-size: 0.75rem;
  color: #718096;
  margin-top: 0.25rem;
}

.file-actions {
  display: flex;
  align-items: center;
}

.upload-speed-info {
  font-size: 0.75rem;
  color: #718096;
  display: flex;
  justify-content: space-between;
  margin-top: 0.25rem;
}

.user-info-box {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-info-box h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
}

.user-info-box p {
  font-size: 14px;
  margin-bottom: 8px;
}

.user-info-box p:last-child {
  margin-bottom: 0;
}

.upload-progress {
  margin-top: 20px;
}

.progress-item {
  margin-bottom: 15px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background-color: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #4CAF50;
  transition: width 0.3s ease;
}

.upload-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
  font-size: 0.9em;
  color: #666;
}

.total-progress {
  margin-top: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}
</style>
