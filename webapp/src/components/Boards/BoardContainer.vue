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
import {ref} from "vue";
import ActionBoard from "./ActionBoard.vue";

const isFirstLogin = ref(false)
//prod
// const isFirstLogin = ref(true)

const toggleFirstLogIn = function () {
  isFirstLogin.value = isFirstLogin.value === true ? false : false
};
</script>

<style scoped>
.board-container__card {
  min-height: 415px;
}
</style>