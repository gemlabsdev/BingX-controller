<template>
  <NTabs
      class="action-board-tabs__container"
      :default-value="defaultTab"
      size="small"
      justify-content="center"
      type="line"
      @click="getCurrentTab"
    >
    <NTabPane
        class="action-board-tabs__tab"
        name="templates"
        tab="Templates"
        display-directive="show:lazy"
    >
      <Template />
</NTabPane>
    <NTabPane
        class="action-board-tabs__tab"
        name="endpoints"
        tab="Endpoints"
    >
      <Endpoints />
    </NTabPane>
    <NTabPane
        class="action-board-tabs__tab"
        name="log"
        tab="Log"
        display-directive="show"
    >
      <Log />
    </NTabPane>
    <NTabPane
        class="action-board-tabs__tab"
        name="keys"
        tab="API Keys"
    >
      <KeyForm :is-to-update="true"/>
    </NTabPane>
  </NTabs>
</template>

<script setup>
import {NTabPane, NTabs} from "naive-ui";
import KeyForm from "../Actions/KeyForm.vue";
import Template from "../Actions/Template.vue";
import Log from "../Actions/Log.vue";
import Endpoints from "../Actions/Endpoints.vue";
import {onBeforeMount, onMounted, ref} from "vue";

const defaultTab = ref('templates')
const getCurrentTab = function (event) {
  const currentTab = event.target.innerText.toLowerCase()
  saveCurrentTab(currentTab)
};

const saveCurrentTab = function (tabName) {
  localStorage.setItem('currentTab',tabName)
};

onBeforeMount(() => {
  const currentTab = localStorage.getItem('currentTab')
  console.log(currentTab)
  defaultTab.value = currentTab ? currentTab : defaultTab.value
})
</script>

<style scoped>
.action-board-tabs__tab {
  margin-top: 18px;

}
</style>