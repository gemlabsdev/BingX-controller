<template>
  <div class="logs__log-content_container">
    <NCard class="logs__log-content_card" @click="scrollToLogBottom">
      <div class="logs__log-content_card-border">
        <NCode
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

const activity = ref(`
INFO - 2023-03-14 08:52:42,262 - ---------------------CLOSE-POSITION---------------------
INFO - 2023-03-14 08:52:42,262 - No cached positions for BTC-USDT
INFO - 2023-03-14 08:52:42,262 - Requesting open BTC-USDT positions from BingX
INFO - 2023-03-14 08:52:42,569 - Adding BTC-USDT Long position to cache
INFO - 2023-03-14 08:52:42,569 - No open positions for BTC-USDT
INFO - 2023-03-14 08:52:42,570 - CLOSE-POSITION: DONE IN 307ms
INFO - 2023-03-14 08:52:42,570 - -----------------REQUEST-FINISHED-----------------------
INFO - 2023-03-14 08:58:19,705 - ---------------------CLOSE-POSITION---------------------
INFO - 2023-03-14 08:58:19,706 - No cached positions for BTC-USDT
INFO - 2023-03-14 08:58:19,707 - Requesting open BTC-USDT positions from BingX
INFO - 2023-03-14 08:58:20,017 - Adding BTC-USDT Long position to cache
INFO - 2023-03-14 08:58:20,017 - No open positions for BTC-USDT
INFO - 2023-03-14 08:58:20,017 - CLOSE-POSITION: DONE IN 311ms
INFO - 2023-03-14 08:58:20,017 - -----------------REQUEST-FINISHED-----------------------
INFO - 2023-03-14 09:00:00,349 - ---------------------CLOSE-POSITION---------------------
INFO - 2023-03-14 09:00:00,349 - No cached positions for BTC-USDT
INFO - 2023-03-14 09:00:00,349 - Requesting open BTC-USDT positions from BingX
INFO - 2023-03-14 09:00:00,658 - Adding BTC-USDT Long position to cache
INFO - 2023-03-14 09:00:00,658 - No open positions for BTC-USDT
INFO - 2023-03-14 09:00:00,658 - CLOSE-POSITION: DONE IN 309ms
INFO - 2023-03-14 09:00:00,658 - -----------------REQUEST-FINISHED-----------------------
INFO - 2023-03-14 09:00:24,820 - ---------------------CLOSE-POSITION---------------------
INFO - 2023-03-14 09:00:24,820 - No cached positions for BTC-USDT
INFO - 2023-03-14 09:00:24,820 - Requesting open BTC-USDT positions from BingX
INFO - 2023-03-14 09:00:25,635 - Adding BTC-USDT Long position to cache
INFO - 2023-03-14 09:00:25,636 - No open positions for BTC-USDT
INFO - 2023-03-14 09:00:25,636 - CLOSE-POSITION: DONE IN 816ms
INFO - 2023-03-14 09:00:25,636 - -----------------REQUEST-FINISHED-----------------------
INFO - 2023-03-14 09:00:56,972 - ---------------------CLOSE-POSITION---------------------
INFO - 2023-03-14 09:00:56,972 - No cached positions for BTC-USDT
INFO - 2023-03-14 09:00:56,973 - Requesting open BTC-USDT positions from BingX
INFO - 2023-03-14 09:00:57,268 - Adding BTC-USDT Long position to cache
INFO - 2023-03-14 09:00:57,268 - No open positions for BTC-USDT
INFO - 2023-03-14 09:00:57,269 - CLOSE-POSITION: DONE IN 296ms
INFO - 2023-03-14 09:00:57,269 - -----------------REQUEST-FINISHED-----------------------
INFO - 2023-03-14 09:01:12,447 - ---------------------CLOSE-POSITION---------------------
INFO - 2023-03-14 09:01:12,447 - No cached positions for BTC-USDT
INFO - 2023-03-14 09:01:12,447 - Requesting open BTC-USDT positions from BingX
INFO - 2023-03-14 09:01:12,750 - Adding BTC-USDT Long position to cache
INFO - 2023-03-14 09:01:12,750 - No open positions for BTC-USDT
INFO - 2023-03-14 09:01:12,750 - CLOSE-POSITION: DONE IN 303ms
INFO - 2023-03-14 09:01:12,750 - -----------------REQUEST-FINISHED-----------------------

`)
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
  overflow: scroll;
  max-height: 246px;
}

.logs__log-content_content {
  text-align: start;
  margin: 40px 0px;

}
</style>