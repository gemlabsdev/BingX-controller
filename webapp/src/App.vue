<script setup>

import {NConfigProvider, darkTheme, NMessageProvider} from "naive-ui";
import hljs from 'highlight.js/lib/core'
import json from 'highlight.js/lib/languages/json'
import javascript from 'highlight.js/lib/languages/javascript'
import BoardContainer from "./components/Boards/BoardContainer.vue";
import {ref} from "vue";

hljs.registerLanguage('json', json)
hljs.registerLanguage('javascript', javascript)

const isLoading = ref(true)

const showContent = function () {
  isLoading.value = false
}
</script>

<template>
  <NConfigProvider :theme="darkTheme" :hljs="hljs">
    <NMessageProvider>
      <div v-if="!isLoading">
        <a href="https://bingx.com/en-us/" target="_blank">
          <img src="./assets/bingx.svg" class="logo" alt="BingX" />
        </a>
      </div>
      <BoardContainer @mounted="showContent" />
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
