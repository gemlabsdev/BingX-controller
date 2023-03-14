<template>
  <NTabs
      class="action-board-tabs__container"
      default-value="log"
      size="small"
      justify-content="center"
      type="line"
      display-directive="show"
    >
    <NTabPane
        class="action-board-tabs__tab"
        name="log"
        tab="Log">
      <Log />
    </NTabPane>
    <NTabPane
        class="action-board-tabs__tab"
        name="keys"
        tab="API Keys"
    >
      <KeyForm :is-to-update="true"/>
    </NTabPane>
    <NTabPane
        class="action-board-tabs__tab"
        name="templates"
        tab="Templates"
        display-directive="show:lazy"
    >
      <Template />
    </NTabPane>
  </NTabs>
</template>

<script setup>
import {NTabPane, NTabs} from "naive-ui";
import KeyForm from "../Actions/KeyForm.vue";
import Template from "../Actions/Template.vue";
import Log from "../Actions/Log.vue";
</script>

<style scoped>
.action-board-tabs__tab {
  margin-top: 18px;

}
</style>