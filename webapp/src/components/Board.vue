<template>
  <NCard>
      <KeyForm v-show="isFirstLogin" @submit="toggleFirstLogIn"/>
  </NCard>
</template>

<script setup>
import KeyForm from "./KeyForm.vue";
import {NCard} from "naive-ui";
import {ref} from "vue";

const isFirstLogin = ref(true)

const toggleFirstLogIn = function () {
  isFirstLogin.value = isFirstLogin.value === true ? false : false
};
</script>

<style scoped>

</style>