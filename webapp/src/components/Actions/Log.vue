<template>
  <div>
    <NButton
        round
        type="primary"
        @click="sendMessage">
    <pre>{{ state.logs }}</pre>
    </NButton>
  </div>
</template>

<script setup>
import {NButton} from "naive-ui";
import io from 'socket.io-client'

import {onMounted, onUnmounted, reactive, ref} from "vue";

const state = reactive({
  logs: '',
});
const socket = io('http://127.0.0.1:8000/');
const message = ref(null)

const handleConnect = () => {
  console.log('Connected to server');
};
const handleDisconnect = () => {
  console.log('Disconnected from server');
};
const handleResponse = data => {
  console.log('Received response:', data);
  message.value = data;
};

onMounted(() => {
  socket.on('connect', handleConnect);
  socket.on('disconnect', handleDisconnect);
  socket.on('response', handleResponse);
  socket.on('logs', logs => {
    state.logs = logs;
  });
});
onUnmounted(() => {
  socket.off('connect', handleConnect);
  socket.off('disconnect', handleDisconnect);
  socket.off('response', handleResponse);
});

const sendMessage = () => {
  socket.emit('message', 'Hello from client');
};



</script>

<style scoped>

</style>