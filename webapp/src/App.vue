<script setup>

import Board from "./components/Board.vue";
import {NMessageProvider} from "naive-ui";
</script>

<template>
  <NMessageProvider>
    <div>
      <a href="https://bingx.com/en-us/" target="_blank">
        <img src="./assets/bingx.svg" class="logo" alt="BingX" />
      </a>
    </div>
  <Board />
  </NMessageProvider>

<!--  <HelloWorld />-->
</template>

<style scoped>
.logo {
  height: 100%;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #2954feaa);
}
</style>
