<template>
  <NCard class="board-container__card">
      <KeyForm
          :isToUpdate="false"
          v-show="isFirstLogin"
          @submit="toggleFirstLogIn"/>
      <ActionBoard v-show="!isFirstLogin" />
  </NCard>
</template>

<script setup>
import KeyForm from "../Actions/KeyForm.vue";
import {NCard} from "naive-ui";
import {onMounted, ref} from "vue";
import ActionBoard from "./ActionBoard.vue";

// const isFirstLogin = ref(false)
//prod
const isFirstLogin = ref(true)

const toggleFirstLogIn = function () {
  const hasRegisteredKeys = localStorage.getItem("hasRegisteredKeys")
  if (!hasRegisteredKeys) {
    localStorage.setItem("hasRegisteredKeys","true")
  }
  isReturningUser()

};

const isReturningUser = function () {
    const hasRegisteredKeys = localStorage.getItem("hasRegisteredKeys")
    if (hasRegisteredKeys === "true") {
      isFirstLogin.value = false
    }
};

onMounted(() => isReturningUser())

</script>

<style scoped>
.board-container__card {
  min-height: 415px;
}
</style>