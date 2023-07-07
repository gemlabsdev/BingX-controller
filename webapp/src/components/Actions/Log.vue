<template>
  <div class="logs__log-content_container">
    <NCard class="logs__log-content_card" @click="scrollToLogBottom">
      <div class="logs__log-content_card-border">
        <NCode
          :word-wrap="true"
          class="logs__log-content_content"
          :code="upToDateLogs === '' ? activity : upToDateLogs"
          language="json"
       />
      </div>
    </NCard>
  </div>

</template>

<script setup>
import {NButton, NCard, NCode, useMessage} from "naive-ui";
import io from 'socket.io-client'
import {hostname} from "../hostname.js";
import {computed, onMounted, onUnmounted, reactive, ref} from "vue";

const date = new Date(Date.now())
const activity = ref('')
const message = useMessage()
const state = reactive({
    messageCount: 0,
    logs: '',
})
const upToDateLogs = computed(() => {
  return state.logs
} )

const scrollToLogBottom = async function () {
    const element = await document.querySelector('.logs__log-content_card-border');
    element.scrollTop = element.scrollHeight;
}

const copyLogsToClipboard = async function () {
  const code = document.querySelector('.logs__log-content_card-border').innerText;
  await navigator.clipboard.writeText(code)
  message.success('Template copied to clipboard')
};

const socket = io(`${hostname}/`);

const handleConnect = () => {
  console.log('Connected to server');
};
const handleDisconnect = () => {
  console.log('Disconnected from server');
};

const handleLogging = async function (logs)  {
  state.logs += state.messageCount === 0 ? logs : logs + '\n'
  state.messageCount += 1
  await scrollToLogBottom()
}

onMounted(() => {
  scrollToLogBottom()
  socket.on('connect', handleConnect);
  socket.on('disconnect', handleDisconnect);
  socket.on('logs', logs => handleLogging(logs))
  activity.value = `INFO - ${date.toISOString()} - Connecting to websocket...`

  setTimeout(() => {
      activity.value = `INFO - ${date.toISOString()} - Welcome to the BingX Signal Bot`
      }, 500
  )
});

onUnmounted(() => {
  socket.off('connect', handleConnect);
  socket.off('disconnect', handleDisconnect);
  socket.off('logs', logs => handleLogging(logs))

});


</script>

<style scoped>
.logs__log-content_container {
  margin: 0px 0px;
  padding: 0px 10px;
}

.logs__log-content_card {
  border: 1px solid rgba(256,256,256,0.4);
  padding: 10px;
  margin-bottom: 6px;
}

.logs__log-content_card-border {
  overflow-x: hidden;
  overflow-y: scroll;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* Internet Explorer 10+ */
  min-height: 267px;
  max-height: 267px;
  width: 755px;
  overflow-wrap: break-word;
}

.logs__log-content_card-border::-webkit-scrollbar { /* WebKit */
    width: 0;
    height: 0;
}

.logs__log-content_content {
  text-align: start;
  margin: 40px 0px;

}
</style>