<script setup>

import Board from "./components/Boards/BoardContainer.vue";
import {NConfigProvider, darkTheme, NMessageProvider} from "naive-ui";
import hljs from 'highlight.js/lib/core'
import json from 'highlight.js/lib/languages/json'

hljs.registerLanguage('json', json)

</script>

<template>
  <NConfigProvider :theme="darkTheme" :hljs="hljs">
    <NMessageProvider>
      <div>
        <a href="https://bingx.com/en-us/" target="_blank">
          <img src="./assets/bingx.svg" class="logo" alt="BingX" />
        </a>
      </div>
    <Board />
    </NMessageProvider>
  </NConfigProvider>

</template>

<style scoped>

.logo {
  height: 100%;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;

}
.logo:hover {
  filter: drop-shadow(0 0 2em #63e2b7aa);
}


</style>
