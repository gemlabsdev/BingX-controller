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
    <NButton
      type="error"
      ghost
      @click="clearCacheHandler"
      class="clear-cache">
    Clear Cache
  </NButton>
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
  const response = await fetch(`${hostname}/user`, {
    method: 'GET',
  })
  const data = await response.json()

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

onBeforeMount(async () => {
  const cacheButton = document.querySelector('.clear-cache')
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
  await isReturningUser()
  isLoading.value = false
})

onMounted(() => {
    emit('mounted')
})


</script>

<style scoped>
.board-container__card {
  min-height: 415px;
}

.clear-cache {
  margin: 20px 20px;
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.5s ease;

}
</style>