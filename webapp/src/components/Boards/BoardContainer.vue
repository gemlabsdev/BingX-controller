<template>
  <NCard
       v-show="!isLoading"
      class="board-container__card">
      <KeyForm
          :isToUpdate="false"
          v-show="isFirstLogin"
          @submit="isReturningUser"/>
      <ActionBoard v-show="!isFirstLogin" />
  </NCard>
  <NButtonGroup
      v-show="!isFirstLogin"
      class="hidden-buttons-container">
    <NButton
      class="hidden-button"
      type="error"
      ghost
      @click="clearCacheHandler">
    Clear Cache
  </NButton>
    <NButton
      class="hidden-button"
      type="error"
      ghost
      @click="clearLogsHandler">
    Clear Logs
  </NButton>
  </NButtonGroup>

</template>

<script setup>
import KeyForm from "../Actions/KeyForm.vue";
import {NCard, NButton, useMessage} from "naive-ui";
import {onBeforeMount, onMounted, ref} from "vue";
import ActionBoard from "./ActionBoard.vue";
import {hostname} from "../hostname.js";

// const isFirstLogin = ref(false)
//prod
const emit = defineEmits(['mounted'])
const isFirstLogin = ref(true)
const isLoading = ref(true)
const message = useMessage()

const isReturningUser = async function () {
    const userStatus = await getUserStatus()
    if (userStatus !== "NEW_USER") {
      isFirstLogin.value = false
    }
};

async function getUserStatus() {
  const response = await fetch(`${hostname}/credentials/bingx/status`, {
    method: 'GET',
  })
  const data = await response
  return data.user

}

async function clearCacheHandler() {
  try{
  const response = await fetch(`${hostname}/perpetual/dump`, {
    method: 'POST',
  })
      message.success('Cache has being cleared')
  } catch (e) {
    console.log(e)
  }
}

async function clearLogsHandler() {
  try{
  await fetch(`${hostname}/logs`, {
    method: 'DELETE',
  })
      message.success('Log file has being cleared')
      setTimeout(() => {
        location.reload()
      }, 500)
  } catch (e) {
    console.log(e)
  }
}

onBeforeMount(async () => {
  await isReturningUser()
  isLoading.value = false
})

onMounted(() => {
  emit('mounted')
  const cacheButton = document.querySelector('.hidden-buttons-container')
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Shift') {
      cacheButton.style.visibility = 'visible'
      cacheButton.style.cursor = 'pointer'
      cacheButton.style.opacity = '1'
    }
  })
  document.addEventListener('keyup', (event) => {
    if (event.key === 'Shift') {
      cacheButton.style.opacity = '0'
      cacheButton.style.cursor = 'auto'
      setTimeout(() => { cacheButton.style.visibility = 'hidden'}, 501)

    }
  })
})


</script>

<style scoped>
.board-container__card {
  min-height: 435px;
}

.hidden-buttons-container {
  margin: 20px 20px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.5s ease;
}

.hidden-button {
  margin: 0 10px;
  width: auto;
}
</style>